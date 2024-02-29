import json
import threading
import time
import uuid
import os
from multiprocessing import Queue
import queue
from typing import List
from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from cluster.command.kubernetes import KubeCommand
from cluster.command.submariner import SubmarinerCommand
from cluster.command.localhost import LocalHostCommand
from repository.cache.network import NetworkStatusRepository
from repository.cache.resources import ResourceRepository
from repository.common import prometheus_client, nfs_server_client
from repository.common.type import ConnectionStatus, MultiClusterRole, CommandType, CommandResult, ExecutionStatus
from repository.common.type import SubmarinerState, MultiClusterConfigState, MultiClusterNetworkDiagnosis
from cluster.data_access_object import ClusterDAO
from repository.model.k8s.condition import Condition
from restclient.api import RestClient
from utils.dateformat import DateFormatter
from utils.fileutils import FileUtil


# noinspection PyUnusedLocal
class ComponentRepository:
    """
    Component status management class
    """
    _conditions = []  # conditions for CEdge components
    _logger = None
    _initialized = False
    _checklist = None
    _master_name = None
    _cluster_id = None
    _prometheus_connector = None
    _nfs_server_connector = None
    _lock = None
    _command_exec_thread_pool = []
    _command_exec_thread_pool_capacity = 10
    _execution_queue = None
    _trace_queue = None
    _submariner_state = SubmarinerState.BROKER_NA
    __scheduled = False
    _once_validated = False
    _is_mc_provision_executed = False

    _component_status = {
        'GEdgeNamespace': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': ['GEdgeNamespaceCreated']
        },
        'PrometheusServer': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': ['PrometheusServerReady']
        },
        'NodeExporter': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': ['NodeExporterReady']
        },
        'K8sStateMetrics': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': ['K8sStateMetricsReady']
        },
        'SubmarinerBroker': {
            # subctl deploy-broker
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': [
                'SubmarinerNamespaceCreated',
                'SubmarinerOperatorReady'
            ]
        },
        'SubmarinerComponents': {
            # subctl join-broker
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': [
                'SubmarinerOperatorServiceReady',
                'SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady',
            ]
        },
        'NfsServer': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': 'LocalNfsServerReady'
        },
        'NfsClient': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': 'LocalNfsClientReady'
        },
        'RemoteNfsClient': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': 'RemoteNfsClientReady'
        },
    }

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        """
        configure ComponentRepository() object
        :return:
        """
        self._logger = settings.get_logger(__name__)
        self._lock = threading.Lock()
        self._execution_queue = Queue(maxsize=100)
        self._trace_queue = {}
        self._start_command_exec_thread_pool()
        self._start_cleanup_command_trace_thread()
        self._submariner_gateway_connect_errors = 0

    def _get_command(self):
        """
        get command
        :return:
        """
        try:
            item = self._execution_queue.get(timeout=1)
        except queue.Empty:
            return None

        return item

    def put_command(self, *argv, **kwargs):
        """
        put command
        :return:
        (str) command_id; you can retrieve command process status with it
        """
        if "callback" in kwargs:
            callback = kwargs['callback']

        else:
            argvs = list(argv)
            callback = argvs.pop(0)
            argv = tuple(argvs)

        command_id = str(uuid.uuid4())
        command = {
            'command_id': command_id,
            'argv': argv,
            'callback': callback
        }

        self._trace_queue[command_id] = {
            'status': ExecutionStatus.PENDING,
            'issued_time': time.time(),
            'launched_time': None,
            'completed_time': None,
            'error_message': None
        }

        try:
            self._execution_queue.put(command)
            self._logger.debug('{}(command_id={}) command is issued'.format(str(callback), command_id))
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            self._logger.error('Failed in self._execution_queue.put(command), caused by ' + error_message)
            del self._trace_queue[command_id]
            return None

        return command_id

    def _start_command_exec_thread_pool(self):
        """
        start command exec thread to thread pool
        :return:
        """
        for i in range(0, self._command_exec_thread_pool_capacity):
            item = {
                'thread': threading.Thread(target=self._command_execute_thread,
                                           args=(),
                                           daemon=True),
                'lock': threading.Lock()
            }
            self._command_exec_thread_pool.append(item)
            item['thread'].start()

    def _start_cleanup_command_trace_thread(self):
        """
        start issued command cleanup thread
        :return:
        """
        thread_object = threading.Thread(target=self._cleanup_command_trace_thread,
                                         args=(),
                                         daemon=True)
        thread_object.start()

    def _cleanup_command_trace_thread(self):
        """
        cleanup command trace queue
        :return:
        """
        trace_expired_time = 60 * 60  # 1 hours

        while True:
            expired_command_ids = []

            for key, value in self._trace_queue.items():
                current_time = time.time()
                issued_time = value['issued_time']
                launched_time = value['launched_time']
                completed_time = value['completed_time']

                if issued_time is not None:
                    # not launched execution
                    if current_time - issued_time > trace_expired_time:
                        self._logger.warning(
                            'command({}) is not launched yet(elapsed:{}sec)'.format(key, current_time - issued_time))
                        expired_command_ids.append(key)
                        continue

                if launched_time is not None:
                    if current_time - launched_time > trace_expired_time:
                        self._logger.warning(
                            'command({}) is not completed yet(elapsed:{}sec)'.format(key, current_time - launched_time))
                        expired_command_ids.append(key)
                        continue

                if completed_time is not None:
                    if current_time - completed_time > trace_expired_time:
                        self._logger.warning(
                            'cleanup command({}) from trace queue'.format(key))
                        expired_command_ids.append(key)
                        continue

            for command_id in expired_command_ids:
                self.delete_command_status(command_id)

            time.sleep(60)  # cleanup interval: 1 minute

    def _command_execute_thread(self):
        """
        command execute thread
        :return:
        """
        logger = self._logger

        while True:
            command = None

            try:
                command = self._get_command()
                if not command: continue

            except Exception as exc:
                error_message = get_exception_traceback(exc)
                self._logger.error('Failed in _get_command(), caused by ' + error_message)
                self._logger.error('Ignore and continue _command_execute_thread()')
                continue

            command_id = command['command_id']

            if not command_id:
                continue

            if command_id not in self._trace_queue:
                logger.error('Command launching is to late. Ignore it')
                continue

            self._trace_queue[command_id]['status'] = ExecutionStatus.RUNNING
            self._trace_queue[command_id]['launched_time'] = time.time()

            logger.debug('{}(command_id={}) command is started'.format(str(command['callback']), command_id))

            """ run command by calling callback method """
            ok, stdout, stderr = command['callback'](command['argv'])

            logger.debug('{}(command_id={}) command is completed'.format(str(command['callback']), command_id))

            self._trace_queue[command_id]['completed_time'] = time.time()

            if not ok:
                """ error occurs in callback method """
                self._trace_queue[command_id]['status'] = ExecutionStatus.FAILED
                self._trace_queue[command_id]['error_message'] = stderr
                continue

            self._trace_queue[command_id]['status'] = ExecutionStatus.SUCCEEDED

            continue

    def get_command_status(self, command_id):
        """
        get issued command status
        :param command_id:
        :return:
        """
        if command_id not in self._trace_queue.keys():
            return None

        status = self._trace_queue[command_id]
        current = time.time()
        completed_time = launched_time = issued_time = None

        if status['completed_time'] is not None:
            elapsed = status['completed_time'] - status['issued_time']
            completed_time = DateFormatter.timestamp_to_str(status['completed_time'])

        elif status['launched_time'] is not None:
            elapsed = time.time() - status['launched_time']
            launched_time = DateFormatter.timestamp_to_str(status['launched_time'])

        else:
            elapsed = time.time() - status['issued_time']
            issued_time = DateFormatter.timestamp_to_str(status['issued_time'])

        return {
            'status': status['status'].value,
            'elapsed': int(elapsed),
            'issued_time': issued_time,
            'launched_time': launched_time,
            'completed_time': completed_time,
            'error_message': status['error_message']
        }

    def get_trace_queue(self):
        """
        get trace queue
        :return:
        """
        return self._trace_queue

    def delete_command_status(self, command_id):
        """
        delete command status in command trace queue
        :param command_id: (str)
        :return:
        """
        if command_id in self._trace_queue.keys():
            self._trace_queue.pop(command_id)

    def initialize(self, cluster_id, master_name):
        """
        initialize ComponentRepository() object
        :param cluster_id:
        :param master_name:
        :return:
        """
        if self._initialized:
            return

        else:
            self._initialized = True

        checklist_file = settings.COMPONENTS_CHECKLIST_FILE
        checklist = FileUtil.read_text_file(checklist_file)
        _cluster_id = cluster_id
        _master_name = master_name

        ''' load component checklist '''
        checklist = checklist.replace("{cluster_id}", _cluster_id)
        checklist = checklist.replace("{master_node}", _master_name)
        self._checklist = json.loads(checklist)

        ''' get service connector '''
        self._prometheus_connector = prometheus_client.Connector()
        self._nfs_server_connector = nfs_server_client.Connector()

        ''' initialize condition list for components '''
        self._init_conditions()

    def get_component_names(self):
        """
        get component names
        :return: (list[str]) ; name list for components
        """
        names = []
        for name in self._component_status.keys():
            names.append(name)

        return names

    def get_component_check_fields(self, component):
        """
        get component check fields
        :param component: (str) component name
        :return:
        list()
        """
        self._lock.acquire()
        item = self._component_status[component]
        ret = item['check_field']
        self._lock.release()

        return ret

    def get_component_status_dict(self) -> dict:
        """
        get components status
        :return: (dict)
        'GEdgeNamespace': {
            'command': CommandType.NONE,
            'is_running': False,
            'updated_date': None,
            'check_field': ['GEdgeNamespaceCreated']
        },
        """
        return self._component_status

    def get_component_status(self,
                             component: str) -> (bool, CommandType, str):
        """
        get component command(create, delete) status
        :param component: (str) component name from ComponentRepository._component_deploy_status
        :return:
        (boolean) True - running, False - not running
        (Enum(CommandType))
        (str) updated date
        """
        if type(component) != str or component is None:
            raise TypeError('Invalid component param({}) value'.format(component))

        if component not in self._component_status:
            raise ValueError('{} component not exist'.format(component))

        self._lock.acquire()
        item = self._component_status[component]
        command = item['command']
        is_running = item['is_running']
        updated_date = item['updated_date']
        self._lock.release()

        return is_running, command, updated_date

    def update_component_status(self,
                                component: str,
                                command: CommandType,
                                is_running: bool) -> (bool, str, str):
        """
        update component command status
        :param component: (str) component name
        :param command: (str in CommandType)
        :param is_running: (bool) True - running, False - not running(ready)
        :return:
        (bool) True - success, False - fail
        (str) output
        (str) error_message
        """
        if component not in self.get_component_names():
            return False, '', 'Not supported component name. ' \
                              'support components are {}'.format(','.join(self.get_component_names()))

        if not CommandType.validate(command):
            return False, '', 'Invalid command({}).'.format(command)

        if type(is_running) != bool:
            return False, '', 'Invalid parameter type(type(is_running)={})'.format(type(is_running))

        current_time = DateFormatter.current_datetime()

        self._lock.acquire()
        item = self._component_status[component]
        item['command'] = command
        item['is_running'] = is_running
        item['updated_date'] = current_time
        self._lock.release()

    def get_submariner_state(self) -> SubmarinerState:
        """
        get submariner state
        :return:
        (repository.common.type.SubmarinerState)
        """
        return self._submariner_state

    def is_submariner_busy(self) -> bool:
        """
        check whether submariner component running
        :return:
        (bool) True - yes, False - no
        """
        components = ['SubmarinerBroker', 'SubmarinerComponents']

        for component in components:
            is_running, command, updated_date = self.get_component_status(component)

            if is_running:
                return True

        return False

    def _init_conditions(self):
        """
        initialize Condition object array
        :return:
        """
        for key, value in self._checklist.items():
            condition = Condition()
            condition.set_condition(key)
            condition.set_status('False')
            condition.set_message('')
            self._conditions.append(condition)

    def get_conditions(self) -> List[Condition]:
        """
        get component conditions
        :return: (list[Condition])
        """
        return self._conditions

    def _set_condition(self,
                       condition: str,
                       status: bool,
                       error: str) -> (bool, str):
        """
        set condition
        :param condition: (str) condition
        :param status: (bool) True or False
        :param error: (str) error; if error is None, set ''
        :return:
        (bool) ok; True - success, False - fail
        (str) error; error message
        """
        if type(status) != bool:
            return False, 'Invalid type for \'status\' param({})'.format(type(status))

        if type(condition) != str:
            return False, 'Invalid type for \'condition\' param({})'.format(type(condition))

        obj = self._get_condition_object(condition)

        if not obj:
            return False, 'Invalid key for \'condition\' param({})'.format(condition)

        obj.set_status(Condition.bool_to_str(status))
        obj.set_message(error)
        obj.set_updated(DateFormatter.current_datetime())

        return True, ''

    def _get_condition_object(self,
                              key: str) -> Condition:
        """
        get condition object for key
        :param key: (str)
        :return:
        """
        for condition in self._conditions:
            if condition.get_condition() == key:
                return condition

        return None

    def _is_prometheus_connectable(self) -> (bool, str):
        """
        heck whether prometheus server is connectable or not
        raise Exception
        :return:
        (bool) True - success, False - fail
        (str) error message
        """
        ok, service = ResourceRepository().get_service(settings.PROM_NAMESPACE, settings.PROM_SERVICE)

        if not ok:
            return False, 'Not found {} service'.format(settings.PROM_SERVICE)

        ip = service.get_cluster_ip()

        if not ip:
            self._prometheus_connector.set_endpoint_none()
            return False, 'Not found ip address in {} service'.format(settings.PROM_SERVICE)

        self._prometheus_connector.set_endpoint(ip, settings.PROM_SERVICE_PORT)

        return self._prometheus_connector.is_connectable()

    def _is_local_nfs_server_connectable(self) -> (bool, str):
        """
        check "Local" NFS server connectable or not
        raise Exception
        :return:
        (bool) True - ready, False - not ready
        (str) error message
        """
        cluster_id = ResourceRepository().get_cluster_id()
        namespace = 'gedge'
        name = 'nfs-server-' + cluster_id
        ok, service = ResourceRepository().get_service(namespace, name)

        if not ok:
            return False, 'Not found {} service'.format(name)

        ip = service.get_cluster_ip()

        if not ip:
            self._nfs_server_connector.set_endpoint_none(MultiClusterRole.LOCAL.value)
            return False, 'Not found ip address in {} service'.format(name)

        # update endpoint
        self._nfs_server_connector.set_endpoint(MultiClusterRole.LOCAL.value,
                                                ip,
                                                settings.NFS_SERVER_API_PORT)

        return self._nfs_server_connector.is_connectable(MultiClusterRole.LOCAL.value)

    def _is_remote_nfs_server_connectable(self) -> (bool, str):
        """
        check whether "remote" nfs server connection is set or not
        raise Exception
        :return:
        (bool) True - ready, False - not ready
        (str) error
        """
        remote_cluster_id = NetworkStatusRepository().get_remote_mc_network_name()
        namespace = settings.NFS_SERVER_NAMESPACE
        service = settings.NFS_SERVER_SERVICE.format(cluster_id=remote_cluster_id)
        port = settings.NFS_SERVER_API_PORT

        if not remote_cluster_id:
            return False, 'Not found remote cluster name'

        if not NetworkStatusRepository().is_service_imported(namespace, service):
            error = "Service not imported(namespace={}, service={})".format(namespace, service)
            self._logger.debug(error)
            return False, error

        imported_service = NetworkStatusRepository().get_imported_service(namespace, service)

        if not imported_service:
            error = "Service not imported(namespace={}, service={})".format(namespace, service)
            self._logger.debug(error)
            return False, error

        remote_ip = imported_service.get_ip()

        if not remote_ip:
            error = 'Not found ip address in {} imported service'.format(service)
            return False, error

        # update endpoint
        self._nfs_server_connector.set_endpoint(MultiClusterRole.REMOTE.value,
                                                imported_service.get_ip(),
                                                port)

        return self._nfs_server_connector.is_connectable(MultiClusterRole.REMOTE.value)

    def print_cluster_component_conditions(self):
        """
        print cluster component conditions
        :return:
        """
        self._logger.debug('')
        self._logger.debug('------------------------------------------------------------')
        for condition in self._conditions:
            self._logger.debug('{}: {}: {}'.format(
                condition.get_condition(), condition.get_status(), condition.get_message()))
        self._logger.debug('------------------------------------------------------------')
        self._logger.debug('')

    def _validate_k8s_version(self):
        """
        validate whether k8s version is same with required version
        :return:
        """
        key = 'K8sVersionChecked'
        required = self._checklist[key]['required_version']
        k8s_version = ResourceRepository().get_k8s_version()
        error = ''

        if not required or not k8s_version:
            self._set_condition(key, False, error)
            return

        if required in k8s_version:
            self._set_condition(key, True, error)
            return

    def _validate_gedge_components(self):
        """
        validate CEdge components
        :return:
        """
        for key, value in self._checklist.items():
            if key[-7:] == 'Created' or key[-5:] == 'Ready':
                not_created_namespaces = []
                not_created_services = []
                not_created_daemonsets = []
                not_ready_daemonsets = []
                not_created_deployments = []
                not_ready_deployments = []
                not_created_pods = []
                not_ready_pods = []
                condition = self._get_condition_object(key)

                for val in value:
                    if 'kind' not in val:
                        self._logger.error('key={}, val={}'.format(key, val))

                    if val['kind'] == 'namespace':
                        # check created
                        # if not ResourceRepository().is_namespace_deployed(val['name']):
                        ok, stdout, stderr = KubeCommand().is_namespace_deployed(val['name'])

                        if not ok:
                            not_created_namespaces.append(val['name'])
                        continue

                    if val['kind'] == 'service':
                        # check created
                        # if not ResourceRepository().is_service_deployed(val['namespace'], val['name']):
                        ok, stdout, stderr = KubeCommand().is_service_deployed(val['namespace'], val['name'])

                        if not ok:
                            not_created_services.append(val['name'])

                        continue

                    if val['kind'] == 'deployment':
                        # check created
                        # if not ResourceRepository().is_deployment_deployed(val['namespace'], val['name']):
                        ok, stdout, stderr = KubeCommand().is_deployment_deployed(val['namespace'], val['name'])

                        if not ok:
                            not_created_deployments.append(val['name'])

                        # check ready
                        # if not ResourceRepository().is_all_deployment_replicas_ready(val['namespace'],
                        #                                                                   val['name']):
                        ok = KubeCommand().is_all_deployment_replicas_ready(val['namespace'], val['name'])

                        if not ok:
                            if val['name'] not in not_created_deployments:
                                not_ready_deployments.append(val['name'])

                        continue

                    if val['kind'] == 'daemonset':
                        name = val['name']

                        if key == 'RemoteNfsClientReady':
                            remote_cluster_id = NetworkStatusRepository().get_remote_mc_network_name()

                            if remote_cluster_id:
                                name = val['name'].replace('{remote_cluster_id}', remote_cluster_id)

                        # check created
                        # if not ResourceRepository().is_daemonset_deployed(val['namespace'], name):
                        ok, stdout, stderr = KubeCommand().is_daemonset_deployed(val['namespace'], name)

                        if not ok:
                            not_created_daemonsets.append(name)

                        # check ready
                        # if not ResourceRepository().is_all_daemonset_replicas_ready(val['namespace'], name):
                        ok, stdout, stderr = KubeCommand().is_all_daemonset_replicas_ready(val['namespace'], name)

                        if not ok:
                            if name not in not_created_deployments:
                                not_ready_daemonsets.append(name)

                        continue

                    if val['kind'] == 'pod':
                        # check created
                        # if not ResourceRepository().is_pod_deployed(val['namespace'], val['name']):
                        ok, stdout, stderr = KubeCommand().is_pod_deployed(val['namespace'], val['name'])

                        if not ok:
                            not_created_pods.append(val['name'])

                        # check ready
                        # if not ResourceRepository().is_pod_running(val['namespace'], val['name']):
                        ok, stdout, stderr = KubeCommand().is_pod_running(val['namespace'], val['name'])

                        if not ok:
                            if val['name'] not in not_created_pods:
                                not_ready_pods.append(val['name'])
                        continue

                fail_count = 0
                messages = []

                if len(not_created_namespaces) > 0:
                    val = ','.join(not_created_namespaces)
                    messages.append('{} namespace not created.'.format(val))
                    fail_count += 1

                if len(not_created_services) > 0:
                    val = ','.join(not_created_services)
                    messages.append('{} service not created.'.format(val))
                    fail_count += 1

                if len(not_created_daemonsets) > 0:
                    val = ','.join(not_created_daemonsets)
                    messages.append('{} daemonset not created.'.format(val))
                    fail_count += 1

                if len(not_ready_daemonsets) > 0:
                    val = ','.join(not_ready_daemonsets)
                    messages.append('{} daemonset not ready.'.format(val))
                    fail_count += 1

                if len(not_created_deployments) > 0:
                    val = ','.join(not_created_deployments)
                    messages.append('{} deployment not created.'.format(val))
                    fail_count += 1

                if len(not_ready_deployments) > 0:
                    val = ','.join(not_created_namespaces)
                    messages.append('{} deployment not ready.'.format(val))
                    fail_count += 1

                if len(not_created_pods) > 0:
                    val = ','.join(not_created_pods)
                    messages.append('{} pod not created.'.format(val))
                    fail_count += 1

                if len(not_ready_pods) > 0:
                    val = ','.join(not_ready_pods)
                    messages.append('{} pod not ready.'.format(val))
                    fail_count += 1

                # error check
                if len(messages) > 0:
                    if condition.get_message() == ExecutionStatus.CREATING.value:
                        continue

                    self._set_condition(key, False, ';'.join(messages))

                else:
                    self._set_condition(key, True, '')
        return

    def _validate_local_prometheus_connection(self):
        """
        validate prometheus server connection
        :return:
        """
        key = 'PrometheusServerReady'
        condition = self._get_condition_object(key)
        status = condition.get_status()

        key = 'LocalPrometheusServerConnected'
        condition = self._get_condition_object(key)

        if status == 'False':
            self._set_condition(key, False, 'PrometheusServerReady is False')
            return

        # check prometheus connection
        ok, error = self._is_prometheus_connectable()

        if not ok:
            self._set_condition(key, False, error)
        else:
            self._set_condition(key, True, '')

    def _validate_local_nfs_server_connection(self):
        """
        validate local nfs server connection
        :return:
        """
        key = 'LocalNfsServerReady'
        condition = self._get_condition_object(key)
        status = condition.get_status()

        key = 'LocalNfsServerConnected'

        if condition.get_status() == 'False':
            self._set_condition(key, False, 'LocalNfsServerReady is False')
            return

        # check local nfs connection
        ok, error = self._is_local_nfs_server_connectable()

        if not ok:
            self._set_condition(key, False, error)
        else:
            self._set_condition(key, True, '')

        return

    def _validate_multi_cluster_connection(self):
        """
        validate multi-cluster connection(remote cluster's gateway connection)
        :return:
        """
        if not NetworkStatusRepository().is_mc_network_connected():
            self._set_condition('RemoteClusterConnected', False, '')
            return

        self._set_condition('RemoteClusterConnected', True, '')

    def _validate_nfs_server_exported(self):
        """
        validate NFS server exported
        :return:
        """
        key = 'LocalNfsServerReady'
        condition = self._get_condition_object(key)
        status = condition.get_status()

        if status == 'False':
            self._set_condition(key, False, 'LocalNfsServerReady is False')

        key = 'LocalNfsServerExported'
        errors = []
        items = self._checklist[key]

        for item in items:
            namespace = item['namespace']
            name = item['name']

            if not NetworkStatusRepository().is_service_exported(namespace, name):
                errors.append('{} not exported'.format(name))

        if len(errors) > 0:
            self._set_condition(key, False, '{}'.format(';'.join(errors)))
            return

        self._set_condition(key, True, '')

    def _validate_remote_nfs_server_imported(self):
        """
        validate remote cluster's NFS server imported
        :return:
        """
        key = 'RemoteNfsServerImported'
        errors = []
        items = self._checklist[key]

        remote_cluster = NetworkStatusRepository().get_remote_mc_network_name()

        if not remote_cluster:
            self._set_condition(key, False, 'Not found remote cluster name')
            return

        for item in items:
            namespace = item['namespace']
            name = item['name']

            if '{remote_cluster_id}' not in item['name']:
                self._logger.error('Invalid service name')
                self._set_condition(key, False, 'Invalid service name')
                return

            name = item['name'].replace('{remote_cluster_id}', remote_cluster)

            if not NetworkStatusRepository().is_service_imported(namespace, name):
                errors.append('{} not imported'.format(name))

        if len(errors) > 0:
            self._set_condition(key, False, '{}'.format(';'.join(errors)))
            return

        self._set_condition(key, True, '')

    def _validate_remote_nfs_server_connection(self):
        """
        validate remote NFS server connection
        :return:
        """
        key = 'RemoteNfsServerImported'
        condition = self._get_condition_object(key)
        status = condition.get_status()

        key = 'RemoteNfsServerConnected'

        if status == 'False':  # not imported
            self._set_condition(key, False, 'RemoteNfsServerImported is False')
            return

        # check remote nfs server connection
        ok, error = self._is_remote_nfs_server_connectable()

        if not ok:
            self._set_condition(key, False, error)
        else:
            self._set_condition(key, True, '')

    def _is_ready_gedge_namespace(self):
        """
        check whether gedge namespace is available
        :return: (bool)
        """
        key = 'GEdgeNamespaceCreated'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'True':
            return True

        return False

    def _is_submariner_components_cleaned(self):
        """
        check whether submariner broker-joined component are cleaned up
        :return: (bool) True - cleaned, False - not cleaned
        """
        keys = ['SubmarinerNamespaceCreated',
                'SubmarinerOperatorReady',
                'SubmarinerOperatorServiceReady',
                'SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            if self._get_condition_object(key).get_status() == 'True':
                return False

        return True

    def _is_submariner_broker_components_available(self) -> bool:
        """
        check whether all submariner broker components are available
        :return:
        """
        keys = ['SubmarinerNamespaceCreated',
                'SubmarinerOperatorReady']

        for key in keys:
            condition = self._get_condition_object(key)

            if not condition or condition.get_status() == 'False':
                return False

        return True

    def _has_submariner_broker_error(self) -> bool:
        """
        check whether there exist submariner control error
        :return:
        """
        components = ['SubmarinerBroker', 'SubmarinerComponents']

        for component in components:
            check_fields = self.get_component_check_fields(component)

            for check_field in check_fields:
                condition = self._get_condition_object(check_field)
                if condition.get_status() == 'False':
                    message = condition.get_message()
                    if not message and message != ExecutionStatus.CREATING.value:
                        return True

        return False

    def is_submariner_join_components_available(self) -> bool:
        """
        check whether all submariner join components are available
        :return:
        """
        return self._is_submariner_join_components_available()

    def _is_submariner_join_components_available(self) -> bool:
        """
        check whether all submariner join components are available
        :return:
        """
        keys = ['SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            if not self._get_condition_object(key):
                return False

            if self._get_condition_object(key).get_status() == 'False':
                return False

        return True

    def _is_submariner_join_components_creating(self) -> bool:
        """
        check whether submariner join components are creating or not
        :return:
        """
        keys = ['SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            if not self._get_condition_object(key):
                return False

            if self._get_condition_object(key).get_message() == ExecutionStatus.CREATING.value:
                return True

        return False

    def _set_submariner_join_components_creating(self):
        """
        set submariner join components to creating
        :return:
        """
        keys = ['SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            self._set_condition(key, False, ExecutionStatus.CREATING.value)

    def is_remote_cluster_connected(self) -> bool:
        """
        is remote cluster connected?
        :return: (bool) True - connected, False - not connected
        """
        key = 'RemoteClusterConnected'
        condition = self._get_condition_object(key)

        if not condition:
            return False

        if condition.get_status() == 'True':
            return True

        return False

    @staticmethod
    def get_remote_cluster_connection_status() -> str:
        """
        get remote cluster connection status
        :return:
        (str) value in repository.common.type.ConnectionStatus
        CONNECTED = 'Connected'
        CONNECTING = 'Connecting'
        UNAVAILABLE = 'Unavailable'
        ERROR = 'Error'
        UNKNOWN = 'Unknown'
        """
        return NetworkStatusRepository().get_mc_network_connection_status()

    def is_remote_nfs_server_connected(self) -> str:
        """
        is remote NFS server connected?
        :return:
        (boo) True - yes, False - no
        """
        if not self.is_remote_cluster_connected():
            return False

        key = 'RemoteNfsServerConnected'
        condition = self._get_condition_object(key)

        if not condition:
            return False

        if condition.get_status() == 'True':
            return True

        return False

    def _provision_prometheus(self):
        """
        provision prometheus
        :return:
        """
        key = 'PrometheusServerReady'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'True' or \
                condition.get_message() == ExecutionStatus.CREATING.value:
            return

        # create prometheus server
        self._logger.info('create prometheus server.')
        ret, _, _ = self.create_prometheus_server()

        if ret == CommandResult.FAILED:
            self._logger.error('Failed in create_prometheus_server()')

        if ret == CommandResult.BUSY:
            self._logger.debug('Busy, create_prometheus_server()')

        if ret == CommandResult.ACCEPT:
            self._set_condition('PrometheusServerReady', False, ExecutionStatus.CREATING.value)

    def _provision_node_exporter(self):
        """
        provision node-exporter
        :return:
        """
        key = 'NodeExporterReady'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'True' or \
                condition.get_message() == ExecutionStatus.CREATING.value:
            return

        # create node-exporter
        ret, _, _ = self.create_node_exporter()

        if ret == CommandResult.FAILED:
            self._logger.error('Failed in create_node_exporter()')

        if ret == CommandResult.BUSY:
            self._logger.debug('Busy, create_node_exporter()')

        if ret == CommandResult.ACCEPT:
            self._set_condition('NodeExporterReady', False, ExecutionStatus.CREATING.value)

    def _provision_k8s_state_metric(self):
        """
        provision k8s-state-metric
        :return:
        """
        key = 'K8sStateMetricsReady'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'True' or \
                condition.get_message() == ExecutionStatus.CREATING.value:
            return

        # create k8s-state-metric
        ret, _, _ = self.create_k8s_state_metric()

        if ret == CommandResult.ACCEPT:
            self._set_condition(key, False, ExecutionStatus.CREATING.value)

        if ret == CommandResult.FAILED:
            self._logger.error('Failed in create_k8s_state_metric()')

        if ret == CommandResult.BUSY:
            self._logger.debug('Busy, create_k8s_state_metric()')

    def _provision_gedge_namespace(self):
        """
        provision CEdge namespace
        :return:
        """
        key = 'GEdgeNamespaceCreated'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'True' or \
                condition.get_message() == ExecutionStatus.CREATING.value:
            return

        # create gedge namespace
        ret, _, _ = self.create_gedge_namespace_nowait()

        if ret == CommandResult.FAILED:
            self._logger.error('Failed in create_gedge_namespace_nowait()')

        if ret == CommandResult.BUSY:
            self._logger.debug('Busy, create_gedge_namespace_nowait()')

    def _provision_nfs_server(self):
        """
        provision NFS server
        :return:
        """
        if not self._is_ready_gedge_namespace():
            return

        key = 'LocalNfsServerReady'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'True' or \
                condition.get_message() == ExecutionStatus.CREATING.value:
            return

        # create NFS server
        ret, _, _ = self.create_nfs_server()

        if ret == CommandResult.FAILED:
            self._logger.error('Failed in create_nfs_server()')

        if ret == CommandResult.BUSY:
            self._logger.debug('Busy, create_nfs_server()')

        if ret == CommandResult.ACCEPT:
            self._set_condition(key, False, ExecutionStatus.CREATING.value)

    def _provision_local_nfs_client(self):
        """
        provision CEdge service network connection
        :return:
        """
        key = 'LocalNfsServerConnected'
        condition = self._get_condition_object(key)

        if not condition:
            return

        if condition.get_status() == 'False':
            return

        key = 'LocalNfsClientReady'
        condition = self._get_condition_object(key)

        if condition.get_status() == 'True':
            return

        # create NFS client
        ret, _, _ = self.create_nfs_client()

        if ret == CommandResult.FAILED:
            self._logger.error('Failed in create_nfs_client()')

        if ret == CommandResult.BUSY:
            self._logger.debug('BUSY, create_nfs_client()')

        if ret == CommandResult.ACCEPT:
            self._set_condition('LocalNfsClientReady', False, ExecutionStatus.CREATING.value)

    def _get_cluster_role(self):
        """
        get cluster role from database
        :return:
        (str) "Local", "Remote", "None"
        """
        ok, cluster_object, error_message = ClusterDAO.get_cluster()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_cluster(), caused by ' + error_message)
            return MultiClusterRole.NONE.value

        role = cluster_object.role

        if not role or role == MultiClusterRole.NONE.value:
            self._logger.error('Fail to get role from Cluster DataAccessObject.')
            return MultiClusterRole.NONE.value

        return role

    def _export_local_nfs_server(self) -> bool:
        """
        export local nfs server
        :return:
        (bool) True - success, False - fail
        """
        key = 'LocalNfsServerExported'
        condition = self._get_condition_object(key)

        if condition.get_status() == 'True':
            # already exported before
            return True

        # export local NFS service
        items = self._checklist[key]
        errors = []

        for item in items:
            namespace = item['namespace']
            name = item['name']

            ok, stdout, stderr = SubmarinerCommand().export_service(namespace, name)

            if not ok:
                self._logger.debug('Fail to export service(ns={}, name={}) '
                                   'caused by {}'.format(namespace, name, stderr))
                self._set_condition(key, False, stderr)
                errors.append(stderr)

        if errors and len(errors) > 0:
            self._set_condition(key, False, '{}'.format(';'.join(errors)))
            return False

        self._set_condition(key, True, '')
        return True

    def _unexport_local_nfs_server(self):
        """
        unexport local nfs server
        * caution: this function must be called in case of 'Remote' cluster role
        :return:
        (bool) True - success, False - fail
        """
        key = 'LocalNfsServerExported'
        condition = self._get_condition_object(key)
        status = condition.get_status()

        if condition.get_status() == 'False' and not condition.get_message():
            # already unexported
            return True

        items = self._checklist[key]
        errors = []

        for item in items:
            namespace = item['namespace']
            name = item['name']

            ok, stdout, stderr = SubmarinerCommand().unexport_service(namespace, name)

            if not ok:
                self._logger.debug('Fail to unexport service(ns={}, name={}) '
                                   'caused by {}'.format(namespace, name, stderr))
                errors.append(stderr)

        if errors and len(errors) > 0:
            self._set_condition(key, False, '{}'.format(';'.join(errors)))
            return False

        self._set_condition(key, False, '')

        return True

    def _cleanup_invalid_remote_nfs_clients(self, local_cluster_id, remote_cluster_id):
        """
        clean up invalid remote NFS clients
        :param local_cluster_id: (str) local cluster id
        :param remote_cluster_id: (str) remote cluster id
        :return:
        """
        invalid_nfs_clients = []
        joined_clusters = [local_cluster_id, remote_cluster_id]

        daemonsets = ResourceRepository().get_daemonsets()

        # collect invalid nfs-client daemonsets which are not included in 'Local' cluster and 'Remote' cluster
        for daemonset in daemonsets:
            name = daemonset.get_name()

            if 'nfs-client-' in name:
                cluster_id = name.replace('nfs-client-', '')

                if cluster_id not in joined_clusters:
                    invalid_nfs_clients.append(cluster_id)

        if len(invalid_nfs_clients) <= 0:
            return

        # delete invalid nfs-clients
        for delete_cluster in delete_clusters:
            # delete invalid NFS clients
            ret, _, _ = self.delete_remote_nfs_client(delete_cluster)

            if ret == CommandResult.FAILED:
                self._logger.error('Failed in delete_remote_nfs_client()')

            if ret == CommandResult.BUSY:
                self._logger.debug('Busy, delete_remote_nfs_client()')

    def _provision_remote_nfs_client(self) -> (bool, str):
        """
        provision nfs-client in remote broker joined cluster
        * caution: this function must be called in case of 'Remote' cluster role
        :return:
        (bool) True - success, False - fail
        """
        # If role is 'Remote', create nfs-client to connect to 'Local' cluster's NFS-server
        key = 'RemoteNfsClientReady'
        condition = self._get_condition_object(key)
        status = condition.get_status()

        if not condition:
            return False, 'Not found condition for RemoteNfsClientReady'

        if not self.is_remote_nfs_server_connected():
            return False, 'Remote NFS server is not connected.'

        if status == 'True':
            return True, None

        if status == 'False' and condition.get_message() == ExecutionStatus.CREATING:
            return False, None

        # create remote NFS client
        ret, _, _ = self.create_remote_nfs_client()

        if ret == CommandResult.FAILED:
            error_message = 'Failed in create_remote_nfs_client()'
            self._logger.error(error_message)
            return False, error_message

        return False, ExecutionStatus.CREATING.value

    def create_remote_nfs_client(self) -> (CommandResult, str, str):
        """
        create remote nfs-client
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'RemoteNfsClient'

        running, _, _ = self.get_component_status(component)

        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        command_id = self.put_command(self._callback_create_remote_nfs_client)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_remote_nfs_client)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_create_remote_nfs_client(argv) -> (bool, str, str):
        """
        callback method to create NFS client to connect remote cluster
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        self = ComponentRepository()
        component = 'RemoteNfsClient'
        check_fields = ComponentRepository().get_component_check_fields(component)

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create remote nfs-client '''
        self._logger.debug('[CALL] apply_nfs_client(\'remote\')')
        ok, stdout, stderr = KubeCommand().apply_nfs_client(MultiClusterRole.REMOTE.value)
        self._logger.debug('[RETURN] apply_nfs_client(\'remote\')')

        if not ok:
            self._logger.error('Failed in KubeCommand().apply_nfs_client(MultiClusterRole.REMOTE.value), '
                               'caused by ' + stderr)

            for check_field in check_fields:
                ComponentRepository()._set_condition(check_field, ok, stderr)

            # update component status: is_running = False
            self.update_component_status(component, CommandType.NONE, False)

            return ok, stdout, stderr

        """ check whether nfs-client shared directory is accessible """
        cluster_id = NetworkStatusRepository().get_remote_mc_network_name()
        nfs_mount_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=cluster_id)
        ok, stderr = LocalHostCommand.is_directory_accessible(
            path=nfs_mount_path, timeout=settings.NFS_MOUNT_DIR_ACCESS_TIMEOUT)

        if not ok:
            self._logger.error('Failed in LocalHostCommand.is_directory_accessible(, caused by ' + stderr)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def delete_remote_nfs_client(self, cluster_id: str) -> (CommandResult, str, str):
        """
        delete remote nfs-client
        :param: (str) cluster_id ; deleting cluster_id(cluster_name)
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'RemoteNfsClient'

        running, _, _ = self.get_component_status(component)

        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        command_id = self.put_command(self._callback_delete_remote_nfs_client, cluster_id)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_delete_remote_nfs_client)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_delete_remote_nfs_client(argv) -> (bool, str, str):
        """
        callback method to create NFS client to connect remote cluster
        :param: argv
        argv[0]: (str) cluster_id
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        self = ComponentRepository()
        component = 'RemoteNfsClient'

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' delete remote nfs-client '''
        self._logger.debug('[CALL] delete_nfs_client_by_cluster_id({})'.format(argv[0]))
        ok, stdout, stderr = KubeCommand().delete_nfs_client_by_cluster_id(argv[0])
        self._logger.debug('[RETURN] delete_nfs_client_by_cluster_id({})'.format(argv[0]))

        if not ok:
            self._logger.error('Failed in KubeCommand().delete_nfs_client_by_cluster_id(argv[0]), '
                               'caused by ' + stderr)

        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def create_gedge_namespace_nowait(self) -> (CommandResult, str, str):
        """
        create gedge namespace
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'GEdgeNamespace'

        running, _, _ = self.get_component_status(component)

        if not running:
            # update component status: is_running = True
            self.update_component_status(component, CommandType.CREATE, True)

            ''' create gedge namespace '''
            self._logger.debug('[CALL] deploy_gedge_namespace()')
            ok, stdout, stderr = KubeCommand().deploy_gedge_namespace()
            self._logger.debug('[RETURN] deploy_gedge_namespace()')

            check_fields = ComponentRepository().get_component_check_fields(component)

            for check_field in check_fields:
                ComponentRepository()._set_condition(check_field, ok, stderr)

            # update component status: is_running = False
            self.update_component_status(component, CommandType.NONE, False)

            if not ok:
                self._logger.error('Failed in KubeCommand().deploy_gedge_namespace() caused by ' + stderr)

                return CommandResult.FAILED, None, stderr

            return CommandResult.SUCCESS, None, None

        return CommandResult.PENDING, None, None

    def create_submariner_broker(self) -> (CommandResult, str, str):
        """
        create submariner broker
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'SubmarinerBroker'

        # delete exist broker-info.subm file
        broker_info_file = os.path.join(settings.LOCAL_BROKER_INFO, 'broker-info.subm')

        if os.path.isfile(broker_info_file):
            FileUtil.delete_file(broker_info_file)

        running, _, _ = self.get_component_status(component)

        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        command_id = self.put_command(self._callback_create_submariner_broker)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_submariner_broker)'

        # set conditions(submariner broker resources) to creating
        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, False, ExecutionStatus.CREATING.value)

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_create_submariner_broker(argv) -> (bool, str, str):
        """
        callback method to create submariner broker
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'SubmarinerBroker'
        self = ComponentRepository()

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create submariner broker '''
        self._logger.debug('[CALL] create_broker()')

        ok, stdout, stderr = SubmarinerCommand().create_broker()

        self._logger.debug('[RETURN] create_broker()')

        if not ok:
            self._logger.error('Failed in SubmarinerCommand().create_broker(), caused by ' + stderr)
            ComponentRepository()._submariner_state = SubmarinerState.BROKER_NA

        else:
            ComponentRepository()._submariner_state = SubmarinerState.BROKER_READY

        # set conditions for submariner broker resources with execution result
        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def cleanup_submariner_broker(self) -> (CommandResult, str, str):
        """
        cleanup submariner broker
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'SubmarinerBroker'

        running, _, _ = self.get_component_status(component)

        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        command_id = self.put_command(self._callback_cleanup_submariner_broker)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_cleanup_submariner_broker)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_cleanup_submariner_broker(argv) -> (bool, str, str):
        """
        callback method to cleanup submariner broker
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'SubmarinerBroker'

        self = ComponentRepository()
        check_fields = self.get_component_check_fields(component)

        # update component status: is_running = True
        self.update_component_status(component, CommandType.DELETE, True)

        ''' delete submariner broker '''
        self._logger.debug('[CALL] delete_submariner()')
        ok, stdout, stderr = SubmarinerCommand().delete_submariner()
        self._logger.debug('[RETURN] delete_submariner()')

        if not ok:
            self._logger.error('Failed in SubmarinerCommand().delete_submariner(), caused by ' + stderr)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def join_submariner_broker(self,
                               mc_connect_id: str,
                               cluster_role: str,
                               broker_info_file: str) -> (CommandResult, str, str):
        """
        join to submariner broker
        :param mc_connect_id: (str) multi-cluster connection ID
        :param cluster_role: (str) MultiClusterRole(Enum) value
        :param broker_info_file: (str) joining broker info file path
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        components = ['SubmarinerBroker', 'SubmarinerComponents']

        if not MultiClusterRole.validate(cluster_role):
            return CommandResult.FAILED, '', 'Invalid cluster role({})'.format(cluster_role)

        for component in components:
            running, _, _ = self.get_component_status(component)

            # return busy
            if running:
                return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        cluster_name = ResourceRepository().get_cluster_id()

        command_id = self.put_command(self._callback_join_submariner_broker,
                                      mc_connect_id,
                                      cluster_role,
                                      cluster_name,
                                      broker_info_file)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_join_submariner_broker)'

        # set conditions(submariner broker resources) to creating
        for component in components:
            check_fields = self.get_component_check_fields(component)

            for check_field in check_fields:
                self._set_condition(check_field, False, ExecutionStatus.CREATING.value)

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_join_submariner_broker(argv) -> (bool, str, str):
        """
        callback method to join to submariner broker
        :param: argv: (list)
        argv[0]: (str) mc_connect_id
        argv[1]: (str) cluster_role
        argv[2]: (str) cluster_name; cluster name
        argv[3]: (str) broker_info_file; broker info file path
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        components = ['SubmarinerBroker', 'SubmarinerComponents']

        self = ComponentRepository()
        mc_connect_id = argv[0]
        cluster_role = argv[1]
        cluster_name = argv[2]
        broker_info_file = argv[3]
        error_messages = []

        # update component status: is_running = True
        for component in components:
            self.update_component_status(component, CommandType.CREATE, True)

        ''' run submariner-join '''
        self._logger.debug('[CALL] join_broker({}, {}, {})'.format(cluster_role, cluster_name, broker_info_file))
        ok, stdout, stderr = SubmarinerCommand().join_broker(cluster_role, cluster_name, broker_info_file)
        self._logger.debug('[RETURN] join_broker({}, {}, {})'.format(cluster_role, cluster_name, broker_info_file))

        # failed to execute command
        if not ok:
            self._logger.error('Failed in SubmarinerCommand().join_broker(, caused by ' + stderr)

        for component in components:
            # set conditions(submariner broker resources) to creating
            check_fields = self.get_component_check_fields(component)

            for check_field in check_fields:
                self._set_condition(check_field, ok, stderr)

            self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def cleanup_submariner_join_components(self) -> (CommandResult, str, str):
        """
        cleanup submariner join components
        :return:
        """
        components = ['SubmarinerBroker', 'SubmarinerComponents']

        for component in components:
            running, _, _ = self.get_component_status(component)

            # return busy
            if running:
                return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        command_id = self.put_command(self._callback_cleanup_submariner_join_components)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_cleanup_submariner_join_components)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_cleanup_submariner_join_components(argv) -> (bool, str, str):
        """
        callback method to cleanup submariner join components
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        components = ['SubmarinerBroker', 'SubmarinerComponents']

        self = ComponentRepository()

        # update component status: is_running = True
        for component in components:
            self.update_component_status(component, CommandType.CREATE, True)

        # delete submariner
        self._logger.debug('[CALL] delete_submariner()')
        ok, stdout, stderr = SubmarinerCommand().delete_submariner()
        self._logger.debug('[RETURN] delete_submariner()')

        # failed to execute command
        if not ok:
            self._logger.error('Failed in SubmarinerCommand().delete_submariner(), caused by {}'.format(stderr))

        # update component status: is_running = False
        for component in components:
            check_fields = ComponentRepository().get_component_check_fields(component)

            for check_field in check_fields:
                self._set_condition(check_field, ok, stderr)

            self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def create_nfs_server(self) -> (CommandResult, str, str):
        """
        create NFS server(LOCAL)
        :return:
        (CommandResult(Enum)); command result
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'NfsServer'

        running, _, _ = self.get_component_status(component)

        # return busy
        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        command_id = self.put_command(self._callback_create_nfs_server)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_nfs_server)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_create_nfs_server(argv) -> (CommandResult, str, str):
        """
        callback method to create nfs server
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'NfsServer'
        self = ComponentRepository()

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create NFS server '''
        self._logger.debug('[CALL] apply_nfs_server()')
        ok, stdout, stderr = KubeCommand.apply_nfs_server()
        self._logger.debug('[RETURN] apply_nfs_server()')

        # failed to execute command
        if not ok:
            self._logger.error('Failed in KubeCommand.apply_nfs_server() caused by ' + stderr)

        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def create_nfs_client(self) -> (CommandResult, str, str):
        """
        create NFS client(LOCAL)
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'NfsClient'

        running, _, _ = self.get_component_status(component)

        # return busy
        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        command_id = self.put_command(self._callback_create_nfs_client)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_nfs_client)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_create_nfs_client(argv) -> (bool, str, str):
        """
        callback method to create NFS client(LOCAL)
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'NfsClient'
        self = ComponentRepository()
        check_fields = ComponentRepository().get_component_check_fields(component)

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create NFS client for local cluster '''
        self._logger.debug('[CALL] apply_nfs_client({})'.format(MultiClusterRole.LOCAL.value))
        ok, stdout, stderr = KubeCommand.apply_nfs_client(MultiClusterRole.LOCAL.value)
        self._logger.debug('[RETURN] apply_nfs_client({})'.format(MultiClusterRole.LOCAL.value))

        # failed to execute command
        if not ok:
            self._logger.error('Failed in KubeCommand.apply_nfs_client(MultiClusterRole.LOCAL.value), '
                               'caused by' + stderr)
            for check_field in check_fields:
                ComponentRepository()._set_condition(check_field, False, stderr)

            # update component status: is_running = False
            self.update_component_status(component, CommandType.NONE, False)

            return ok, stdout, stderr

        """ check whether nfs-client shared directory is accessible """
        cluster_id = ResourceRepository().get_cluster_id()
        nfs_mount_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=cluster_id)
        ok, stderr = LocalHostCommand.is_directory_accessible(
            path=nfs_mount_path, timeout=settings.NFS_MOUNT_DIR_ACCESS_TIMEOUT)

        if not ok:
            self._logger.error('Failed in LocalHostCommand.is_directory_accessible(, caused by ' + stderr)

        migration_pod_template_dir = os.path.join(nfs_mount_path, 'template')
        try:
            if not os.path.exists(migration_pod_template_dir):
                os.makedirs(migration_pod_template_dir)
        except OSError as exc:
            ok = False
            stderr = 'Failed to create directory({}), ' \
                     'caused by {}'.format(migration_pod_template_dir, get_exception_traceback(exc))
            self._logger.error(stderr)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def create_prometheus_server(self) -> (CommandResult, str, str):
        """
        create prometheus server
        :return:
        """
        component = 'PrometheusServer'

        running, _, _ = self.get_component_status(component)

        # return busy
        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        command_id = self.put_command(self._callback_create_prometheus_server)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_prometheus_server)'

        return CommandResult.ACCEPT, command_id, None

    @staticmethod
    def _callback_create_prometheus_server(argv) -> (bool, str, str):
        """
        callback method to create prometheus server
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'PrometheusServer'
        self = ComponentRepository()

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create prometheus server '''
        self._logger.debug('[CALL] apply_prometheus()')
        ok, stdout, stderr = KubeCommand().apply_prometheus()
        self._logger.debug('[RETURN] apply_prometheus()')

        # failed to execute command
        if not ok:
            self._logger.error('Failed in KubeCommand().apply_prometheus(), caused by ' + stderr)

        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def create_node_exporter(self) -> (CommandResult, str, str):
        """
        create node exporter
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'NodeExporter'

        running, _, _ = self.get_component_status(component)

        # return busy
        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        command_id = self.put_command(self._callback_create_node_exporter)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_node_exporter)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_create_node_exporter(argv) -> (bool, str, str):
        """
        callback method to create node exporter
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'NodeExporter'
        self = ComponentRepository()

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create node-exporter '''
        self._logger.debug('[CALL] apply_node_exporter()')
        ok, stdout, stderr = KubeCommand().apply_node_exporter()
        self._logger.debug('[RETURN] apply_node_exporter()')

        # failed to execute command
        if not ok:
            self._logger.error('Failed in KubeCommand().apply_node_exporter(), caused by ' + stderr)

        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def create_k8s_state_metric(self) -> (CommandResult, str, str):
        """
        create k8s state metric
        :return:
        (CommandResultStatus(Enum))
        (str) command_id; you can retrieve command process status with it
        (str) reason; failure reason when ret0 is CommandResult.FAILED
        """
        component = 'K8sStateMetrics'

        running, _, _ = self.get_component_status(component)

        # return busy
        if running:
            return CommandResult.BUSY, None, 'Busy, component={}'.format(component)

        # issue command to execution thread pool
        command_id = self.put_command(self._callback_create_k8s_state_metric)

        if not command_id:
            return CommandResult.FAILED, None, 'Failed in self.put_command(self._callback_create_k8s_state_metric)'

        return CommandResult.ACCEPT, command_id, ''

    @staticmethod
    def _callback_create_k8s_state_metric(argv) -> (bool, str, str):
        """
        callback method to create k8s state metric
        :return:
        (bool) True - success, False - fail
        (str) stdout, success return value
        (str) stderr, error reason
        """
        component = 'K8sStateMetrics'
        self = ComponentRepository()

        # update component status: is_running = True
        self.update_component_status(component, CommandType.CREATE, True)

        ''' create k8s-state-metric '''
        self._logger.debug('[CALL] apply_k8s_state_metric()')
        ok, stdout, stderr = KubeCommand().apply_k8s_state_metric()
        self._logger.debug('[RETURN] apply_k8s_state_metric()')

        # failed to execute command
        if not ok:
            self._logger.error('Failed in KubeCommand().apply_k8s_state_metric(), caused by ' + stderr)

        check_fields = ComponentRepository().get_component_check_fields(component)

        for check_field in check_fields:
            ComponentRepository()._set_condition(check_field, ok, stderr)

        # update component status: is_running = False
        self.update_component_status(component, CommandType.NONE, False)

        return ok, stdout, stderr

    def _set_multi_cluster_to_connected(self):
        """
        set multi-cluster to connected state
        :return:
        """
        if not self._is_mc_config_state_connecting():
            return

        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
            return

        mc_connect_id = mc_config.mc_connect_id
        role = mc_config.role
        remote_cluster_name = mc_config.remote_cluster_name

        # set multi-cluster-config to Cluster table
        ok, error_message = ClusterDAO.set_multi_cluster_connection(role=role,
                                                                    mc_connect_id=mc_connect_id,
                                                                    is_mc_provisioned=False,
                                                                    remote_cluster_name=remote_cluster_name)
        if not ok:
            self._logger.error('Failed in ClusterDAO.set_multi_cluster_connection, '
                               'caused by ' + error_message)

        # reset multi-cluster-config
        ok, error_message = ClusterDAO.reset_multi_cluster_config_request()

        if not ok:
            self._logger.error('Failed in ClusterDAO.reset_multi_cluster_config_request(), '
                               'caused by ' + error_message)

    def _do_validate(self):
        """
        Validate CEdge components
        :return:
        """
        # validate kubernetes version
        self._validate_k8s_version()

        # validate CEdge components such as nfs-server/client, prometheus, exporters
        # i.e., validate resource are daemonsets, deployments, pods, services
        # todo: too slow
        self._validate_gedge_components()

        # validate CEdge services
        # such as nfs-server, prometheus
        self._validate_local_prometheus_connection()
        self._validate_local_nfs_server_connection()

        # validate multi-cluster connection
        # whether all cluster's gateway are connected to each other
        self._validate_multi_cluster_connection()

        # check whether multi-cluster network is connected.
        condition = self._get_condition_object('RemoteClusterConnected')

        if condition.get_status() == 'True':
            # validate service exports to remote cluster
            self._validate_nfs_server_exported()

            # validate service imports from remote cluster
            self._validate_remote_nfs_server_imported()

            # validate whether remote nfs-server are connectable
            self._validate_remote_nfs_server_connection()

    def _do_provision(self):
        """
        provisioning CEdge components
        :return:
        """
        # provision local gedge namespace
        self._provision_gedge_namespace()

        # provision local prometheus
        self._provision_prometheus()

        # provision local node exporter
        self._provision_node_exporter()

        # provision k8s-state-metric
        self._provision_k8s_state_metric()

        # provision local nfs server
        self._provision_nfs_server()

        # provision local nfs client
        self._provision_local_nfs_client()

        # provision multi cluster network
        submariner_state = self._provision_submariner()
        self._logger.debug('Submariner state[{}]'.format(submariner_state.value))

        if submariner_state == SubmarinerState.GATEWAY_CONNECTED:
            # In case of no multi-cluster info(role, mc_config_state, mc_connect_id) in cluster table,
            # correct invalid state
            self._set_multi_cluster_to_connected()

            ok, is_provisioned, error_message = ClusterDAO.get_multi_cluster_provisioned()

            if not ok:
                self._logger.error('Failed in ClusterDAO.get_multi_cluster_provisioned()')
                return

            if is_provisioned:
                # already multi-cluster network provisioned, pass
                return

            # get cluster role, local cluster id, remote cluster id
            ok, cluster_object, error_message = ClusterDAO.get_cluster()
            if not ok:
                self._logger.error('Failed in ClusterDAO.get_cluster()')
                return

            role = cluster_object.role
            local_cluster_id = cluster_object.cluster_name
            remote_cluster_id = cluster_object.remote_cluster_name

            if not self._is_mc_provision_executed:
                self._is_mc_provision_executed = True

                """ provisioning multi-cluster network applications """
                if role == MultiClusterRole.NONE.value or not role:
                    self._logger.error('Not found cluster role in database')
                    return

                if not local_cluster_id:
                    self._logger.error('Not found local cluster name')
                    return

                if not remote_cluster_id:
                    self._logger.debug('Not found remote cluster name')
                    return

                # clean invalid remote nfs client
                self._cleanup_invalid_remote_nfs_clients(local_cluster_id=local_cluster_id,
                                                         remote_cluster_id=remote_cluster_id)

                # check whether REMOTE NFS client is exist.
                # ex) daemonset.apps/nfs-client-gedge-cls2
                remote_nfs_client_daemonset = 'nfs-client-' + remote_cluster_id
                remote_nfs_client_ns = 'gedge'
                ok, _, error = KubeCommand().is_daemonset_deployed(
                    namespace=remote_nfs_client_ns, daemonset=remote_nfs_client_daemonset)

                if ok:
                    ok, _, error = KubeCommand().delete_daemonset(
                        namespace=remote_nfs_client_ns, daemonset=remote_nfs_client_daemonset)

                    if not ok:
                        error_message = 'Failed to delete remote nfs client daemonset, caused by ' + error
                        self._logger.error(error_message)
                        return

                # provision remote NFS client
                if role == MultiClusterRole.LOCAL.value:
                    # check nfs-server is exported
                    if not self._unexport_local_nfs_server():
                        return
                    if not self._export_local_nfs_server():
                        return

            # remote cluster role
            # self._unexport_local_nfs_server()
            if role == MultiClusterRole.REMOTE.value:
                ok, error_message = self._provision_remote_nfs_client()

                if not ok:
                    self._logger.debug(error_message)
                    return

            # set Cluster table with is_mc_provisioned=True
            ok, error_message = ClusterDAO.set_multi_cluster_provisioned()
            if not ok:
                self._logger.error('Failed in ClusterDAO.set_multi_cluster_provisioned(), caused by ' + error_message)

    def is_submariner_broker_ready(self) -> bool:
        """
        is submariner broker ready?
        :return:
        (bool) True - yes, False - no
        """
        if self._submariner_state == SubmarinerState.BROKER_NA:
            return False

        if self._submariner_state == SubmarinerState.BROKER_DEPLOYING:
            return False

        if self._submariner_state == SubmarinerState.BROKER_CLEANING:
            return False

        return True

    def _is_multi_cluster_composed(self) -> bool:
        """
        check whether multi-cluster is composed
        :return:
        (bool) True - yes, False - no
        """
        ok, cluster_object, error_message = ClusterDAO.get_cluster()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_cluster(), caused by ' + error_message)
            return False

        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
            return False

        if mc_config.mc_config_state == MultiClusterConfigState.CONNECTING.value:
            if mc_config.mc_connect_id:
                return True

        if not cluster_object.mc_connect_id:
            return False

        return True

    def _is_mc_config_state_connect_request(self) -> bool:
        """
        check whether multi-cluster-config-state is ConnectRequest
        :return:
        (bool) True - yes, False - no
        """
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by {}'.format(error_message))
            return False

        mc_config_state = mc_config.mc_config_state

        if not mc_config_state:
            self._logger.error('Invalid value in mc_config_state, mc_config_state={}'.format(mc_config_state))
            return False

        if mc_config_state != MultiClusterConfigState.CONNECT_REQUEST.value:
            return False

        return True

    def _is_mc_config_state_connecting(self) -> bool:
        """
        check whether multi-cluster-config-state is Connecting
        :return:
        (bool) True - yes, False - no
        """
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by {}'.format(error_message))
            return False

        mc_config_state = mc_config.mc_config_state

        if not mc_config_state:
            self._logger.error('Invalid value in mc_config_state, mc_config_state={}'.format(mc_config_state))
            return False

        if mc_config_state != MultiClusterConfigState.CONNECTING.value:
            return False

        return True

    def _is_mc_config_state_disconnect_request(self) -> bool:
        """
        check whether multi-cluster-config-state is DisconnectRequest
        :return:
        (bool) True - yes, False - no
        """
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by {}'.format(error_message))
            return False

        mc_config_state = mc_config.mc_config_state

        if not mc_config_state:
            self._logger.error('Invalid value in mc_config_state, mc_config_state={}'.format(mc_config_state))
            return False

        if mc_config_state != MultiClusterConfigState.DISCONNECT_REQUEST.value:
            return False

        return True

    def _is_mc_config_state_disconnecting(self) -> bool:
        """
        check whether multi-cluster-config-state is Disconnecting
        :return:
        (bool) True - yes, False - no
        """
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by {}'.format(error_message))
            return False

        mc_config_state = mc_config.mc_config_state

        if not mc_config_state:
            self._logger.error('Invalid value in mc_config_state, mc_config_state={}'.format(mc_config_state))
            return False

        if mc_config_state != MultiClusterConfigState.DISCONNECTING.value:
            return False

        return True

    def _recover_join_submariner_broker(self) -> (bool, str):
        """
        recover join submariner broker
        :return:
        (bool) ok
        (str) error_message
        """
        ok, cluster_object, error_message = ClusterDAO.get_cluster()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_cluster(), caused by {}'.format(error_message))
            return False, error_message

        # get multi-cluster config parameters
        mc_connect_id = cluster_object.mc_connect_id
        role = cluster_object.role

        mc_config = None

        if not mc_connect_id or not role:
            ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()
            if not ok:
                self._logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
                return

        if mc_config:
            mc_connect_id = mc_config.mc_connect_id
            role = mc_config.role

        if not mc_connect_id:
            self._logger.error('Not found mc_connect_id.')
            return

        if not role:
            self._logger.error('Not found mc_connect_id.')
            return

        if role == MultiClusterRole.LOCAL.value:
            # if multi-cluster role is local
            broker_info_file = os.path.join(settings.LOCAL_BROKER_INFO, 'broker-info.subm')

            # validate local broker-info.subm file
            if not os.path.isfile(broker_info_file):
                error_message = 'Not found local \'broker-info.subm\' file. file_path=' + broker_info_file
                self._logger.error(error_message)

                return False, error_message

        elif role == MultiClusterRole.REMOTE.value:
            # if multi-cluster role is remote
            broker_info_file = os.path.join(settings.REMOTE_BROKER_INFO, 'broker-info.subm')

            # validate remote broker-info.subm file
            if not os.path.isfile(broker_info_file):
                error_message = 'Not found remote \'broker-info.subm\' file. file_path=' + broker_info_file
                self._logger.error(error_message)

                return False, error_message
        else:
            # if multi-cluster role is invalid
            error_message = 'Invalid role. role=' + role

            return False, error_message

        # join submariner broker
        ret, _, error_message = self.join_submariner_broker(mc_connect_id,
                                                            cluster_role=role,
                                                            broker_info_file=broker_info_file)
        if ret != CommandResult.ACCEPT:
            return False, error_message

        return True, error_message

    def _do_join_submariner_broker_with_mc_config_request(self) -> (bool, str):
        """
        join submariner_broker with multi-cluster-config request
        :return:
        (bool) ok
        (str) error_message
        """
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            error_message = 'Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message
            self._logger.error(error_message)
            return False, error_message

        # get multi-cluster-config parameters
        mc_connect_id = mc_config.mc_connect_id
        role = mc_config.role
        mc_config_state = mc_config.mc_config_state

        # validate state
        if not mc_config_state or mc_config_state != MultiClusterConfigState.CONNECT_REQUEST.value:
            error_message = 'Busy, method=_do_join_submariner_broker_with_mc_config_request()'

            return False, error_message

        if role == MultiClusterRole.LOCAL.value:
            # if multi-cluster role is local
            broker_info_file = os.path.join(settings.LOCAL_BROKER_INFO, 'broker-info.subm')

            # validate local broker-info.subm file
            if not os.path.isfile(broker_info_file):
                error_message = 'Not found local \'broker-info.subm\' file. file_path={}'.format(broker_info_file)
                self._logger.error(error_message)

                return False, error_message

        elif role == MultiClusterRole.REMOTE.value:
            # if multi-cluster role is remote
            broker_info_file = os.path.join(settings.REMOTE_BROKER_INFO, 'broker-info.subm')

            # validate remote broker-info.subm file
            if not os.path.isfile(broker_info_file):
                error_message = 'Not found remote \'broker-info.subm\' file. file_path={}'.format(broker_info_file)
                self._logger.error(error_message)

                return False, error_message
        else:
            # if multi-cluster role is invalid
            error_message = 'Invalid role. role={}'.format(role)

            return False, error_message

        # join submariner broker
        ret, _, error_message = self.join_submariner_broker(mc_connect_id,
                                                            cluster_role=role,
                                                            broker_info_file=broker_info_file)
        if ret != CommandResult.ACCEPT:
            return False, error_message

        return True, error_message

    def _cleanup_join_submariner_broker(self) -> (bool, str):
        """
        cleanup
        :return: join submariner broker
        (bool) ok
        (str) error_message
        """
        # run cleanup submariner-join components
        ret, _, error_message = self.cleanup_submariner_join_components()

        if ret != CommandResult.ACCEPT:
            return False, error_message

        return True, error_message

    def diagnose_and_recover_multi_cluster_network(self):
        """
        diagnose and recover multi-cluster-network
        :return:
        """
        ok, cluster_object, error_message = ClusterDAO.get_cluster()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_cluster(), caused by ' + error_message)
            return

        cluster_name = cluster_object.cluster_name
        mc_connect_id = cluster_object.mc_connect_id

        if not cluster_name:
            self._logger.error('Invalid \'cluster_name\'. cluster_name=' + cluster_name)
            return

        if not mc_connect_id:
            self._logger.error('Invalid \'mc_connect_id\'. cluster_name=' + cluster_name)
            return

        ok, result, error_message = \
            RestClient.get_multi_cluster_network_diagnosis(cluster_name=cluster_name)

        if not ok:
            self._logger.error('Failed in RestClient.get_multi_cluster_network_diagnosis, '
                               'caused by ' + error_message)
            return

        if result == MultiClusterNetworkDiagnosis.BROKER_UPDATED.value:
            # get connecting cluster's local broker-info.subm, and update remote broker-info.subm
            ok, broker_info_content, error_message = RestClient.get_join_broker_info(mc_connect_id)

            if not ok:
                self._logger.error('Failed in RestClient.get_broker_info(cluster_name), '
                                   'caused by ' + error_message)
                return

            broker_info_file = os.path.join(settings.REMOTE_BROKER_INFO, 'broker-info.subm')

            try:
                FileUtil.delete_file(broker_info_file)
                FileUtil.write_text_file(broker_info_file, broker_info_content)
            except Exception as exc:
                # fail to save broker-info.subm
                error_message = get_exception_traceback(exc)
                logger.error('Failed in FileUtil.delete_file(broker_info_file) or FileUtil.write_text_file(), '
                             'caused by ' + error_message)
                return

            # rejoin to such broker
            ok, error_message = self._recover_join_submariner_broker()

            if not ok:
                # failed to run self._recover_join_submariner_broker()
                error_message = 'Failed in _recover_join_submariner_broker(), caused by ' + error_message
                self._logger.error(error_message)

            self._submariner_state = SubmarinerState.BROKER_JOINING

            return

        elif result == MultiClusterNetworkDiagnosis.MULTI_CLUSTER_NETWORK_ERROR.value:
            # stop network status and metric monitor
            ok = NetworkStatusRepository().stop_mc_network_monitor()

            if not ok:
                error_message = 'Fail to stop multi-cluster network monitor threads. ' \
                                'Thus, you can\'t disconnect multi-cluster network'
                return

            ok, error_message = self._recover_join_submariner_broker()

            if not ok:
                # failed to run self._recover_join_submariner_broker()
                error_message = 'Failed in _recover_join_submariner_broker(), caused by ' + error_message
                self._logger.error(error_message)

                return self._submariner_state

            # success to run self._recover_join_submariner_broker()
            self._submariner_state = SubmarinerState.BROKER_JOINING

            # rejoin to broker stored
            # ok, error_message = self._recover_join_submariner_broker()
            #
            # if not ok:
            #     # failed to run self._recover_join_submariner_broker()
            #     error_message = 'Failed in _recover_join_submariner_broker(), caused by ' + error_message
            #     self._logger.error(error_message)

            # self._submariner_state = SubmarinerState.BROKER_JOINING

            return

        elif result == MultiClusterNetworkDiagnosis.AGENT_NETWORK_ERROR.value:
            # ignore: wait until agent network is recovered
            return

        else:
            self._logger.error('Invalid diagnosis result. result=' + result)

        return

    def _set_submariner_gateway_connect_status(self):
        """
        set submariner gateway connect status
        :return:
        """
        connection_status = self.get_remote_cluster_connection_status()

        if connection_status == ConnectionStatus.CONNECTED.value:
            self._submariner_state = SubmarinerState.GATEWAY_CONNECTED
            self._logger.debug('Multicluster network connection status=Connected')

        elif connection_status == ConnectionStatus.CONNECTING.value:
            self._submariner_state = SubmarinerState.GATEWAY_CONNECTING
            self._logger.debug('Multicluster network connection status=Connecting')

        elif connection_status == ConnectionStatus.ERROR.value:
            self._submariner_state = SubmarinerState.GATEWAY_CONNECT_ERROR
            self._logger.debug('Multicluster network connection status=ConnectError')

        elif connection_status == ConnectionStatus.UNAVAILABLE.value:
            self._logger.debug('Multicluster network connection status=Unavailable')

        else:
            self._logger.error('Invalid multi-cluster network connection status. '
                               'status=' + connection_status)

        return self._submariner_state

    def _handle_disconnect_request(self):
        """
        handle disconnect request from center
        :return:
        (bool) True: success, otherwise: failure
        (str) error message
        """
        self._is_mc_provision_executed = False

        # stop multi-cluster network monitoring thread
        ok = NetworkStatusRepository().stop_mc_network_monitor()

        if not ok:
            error_message = 'Fail to stop multi-cluster network monitor threads. ' \
                            'Thus, you can\'t disconnect multi-cluster network'
            return False, error_message

        # delete nfs remote client
        role = self._get_cluster_role()
        remote_cluster_id = NetworkStatusRepository().get_remote_mc_network_name()

        if role == MultiClusterRole.REMOTE.value:
            # delete nfs-client connected to remote cluster's nfs-server
            if remote_cluster_id:
                ok, _, error = KubeCommand().delete_daemonset('gedge', 'nfs-client-'+remote_cluster_id)
                if not ok:
                    self._logger.error('Fail to delete remote nfs client for '+remote_cluster_id)
                # self.delete_remote_nfs_client(remote_cluster_id)
            else:
                self._logger.error('[CRITICAL] Not found remote cluster name in Cluster database')

        # unexport all service
        exported_services = NetworkStatusRepository().get_mc_network_service_exports()

        if exported_services:
            for exported_service in exported_services:
                name = exported_service.get_name()
                namespace = exported_service.get_namespace()
                ok, stdout, stderr = SubmarinerCommand().unexport_service(namespace, name)

                if not ok:
                    self._logger.debug('Fail to unexport service(ns={}, name={}) '
                                       'caused by {}'.format(namespace, name, stderr))

        # do cleanup submariner
        ok, error_message = self._cleanup_join_submariner_broker()

        if not ok:
            # failed to run self._cleanup_join_submariner_broker()
            self._logger.error('Failed in _cleanup_join_submariner_broker, '
                               'caused by ' + error_message)

            return ok, error_message

        # set multi-cluster-config state to 'Disconnecting'
        ok, error_message = ClusterDAO.set_mc_config_state_to_disconnecting()

        if not ok:
            self._logger.error('Failed in ClusterDAO.set_mc_config_state_to_disconnecting(), '
                               'caused by ' + error_message)

        return ok, error_message

    def _provision_submariner(self):
        """
        provision submariner
        :return: (SubmarinerState)
        """
        if self._submariner_state == SubmarinerState.BROKER_NA:
            # submariner broker components are not available or program init
            if not self._is_submariner_broker_components_available():
                # If broker components are not exist in cluster, deploy broker
                # create submariner broker
                ret, _, _ = self.create_submariner_broker()

                if ret == CommandResult.ACCEPT:
                    self._submariner_state = SubmarinerState.BROKER_DEPLOYING

                return self._submariner_state

            # submariner broker is available
            self._submariner_state = SubmarinerState.BROKER_READY

            return self._submariner_state

        elif self._submariner_state == SubmarinerState.BROKER_DEPLOYING:
            # submariner broker components are deploying
            if self._is_submariner_broker_components_available():
                self._submariner_state = SubmarinerState.BROKER_READY

            return self._submariner_state

        elif self._submariner_state == SubmarinerState.BROKER_READY:
            if self._is_multi_cluster_composed():
                # if multi-cluster connection is already succeeded,
                if self._is_submariner_join_components_available():
                    # submariner join components is available
                    self._submariner_state = SubmarinerState.BROKER_JOINED

                    return self._submariner_state

                else:
                    # failure in submariner join components
                    # recover submariner join
                    ok, error_message = self._recover_join_submariner_broker()

                    if not ok:
                        # failed to run self._recover_join_submariner_broker()
                        error_message = 'Failed in _recover_join_submariner_broker(), caused by ' + error_message
                        self._logger.error(error_message)

                        return self._submariner_state

                    # success to run self._recover_join_submariner_broker()
                    self._submariner_state = SubmarinerState.BROKER_JOINING

                    return self._submariner_state

            else:
                # if multi-cluster connection is not exist before(Cluster.mc_connect_id is None),
                if self._is_mc_config_state_connect_request():
                    # if CEdge-center requests multi-cluster connect,
                    # run submariner join with multi-cluster-config request
                    ok, error_message = self._do_join_submariner_broker_with_mc_config_request()

                    if not ok:
                        # failed to run self._do_join_submariner_broker_with_mc_config_request()
                        self._logger.error('Failed in _join_submariner_broker_with_mc_config_request(), '
                                           'caused by ' + error_message)

                        return self._submariner_state

                    # success to run self._do_join_submariner_broker_with_mc_config_request()
                    self._submariner_state = SubmarinerState.BROKER_JOINING

                    # set multi-cluster-config state to 'Connecting'
                    ok, error_message = ClusterDAO.set_mc_config_state_to_connecting()

                    if not ok:
                        self._logger.error('Failed in ClusterDAO.set_mc_config_state_to_connecting(), '
                                           'caused by ' + error_message)

            return self._submariner_state

        elif self._submariner_state == SubmarinerState.BROKER_JOINING:
            if self._has_submariner_broker_error():
                ok, error_message = self._recover_join_submariner_broker()
                if not ok:
                    # failed to run self._recover_join_submariner_broker()
                    error_message = 'Failed in _recover_join_submariner_broker(), caused by ' + error_message
                    self._logger.error(error_message)

                    return self._submariner_state

            # submariner broker is joining
            if not self.is_submariner_busy() and self._is_submariner_join_components_available():
                # if xxx_join_submariner_xxx is completed
                self._submariner_state = SubmarinerState.BROKER_JOINED

                if self._is_mc_config_state_connecting():
                    # if BROKER_JOINING is on by self._do_join_submariner_broker_with_mc_config_request()
                    _, mc_config, _ = ClusterDAO.get_multi_cluster_config()
                    mc_connect_id = mc_config.mc_connect_id
                    role = mc_config.role
                    remote_cluster_name = mc_config.remote_cluster_name

                    # set multi-cluster-config to Cluster table
                    ok, error_message = ClusterDAO.set_multi_cluster_connection(role=role,
                                                                                mc_connect_id=mc_connect_id,
                                                                                is_mc_provisioned=False,
                                                                                remote_cluster_name=remote_cluster_name)
                    if not ok:
                        self._logger.error('Failed in ClusterDAO.set_multi_cluster_connection, '
                                           'caused by ' + error_message)

                    # reset multi-cluster-config
                    ok, error_message = ClusterDAO.reset_multi_cluster_config_request()

                    if not ok:
                        self._logger.error('Failed in ClusterDAO.reset_multi_cluster_config_request(), '
                                           'caused by ' + error_message)

            return self._submariner_state

        elif self._submariner_state == SubmarinerState.BROKER_JOINED:
            # start mc network monitor
            ok = NetworkStatusRepository().start_mc_network_monitor()

            if not ok:
                self._logger.error('Fail to start multi-cluster network monitor threads.')

            # if CEdge-center requests multi-cluster disconnect,
            if self._is_mc_config_state_disconnect_request() or \
                    self._is_mc_config_state_disconnecting():
                # handle multi-cluster disconnect request
                ok, error_message = self._handle_disconnect_request()

                if not ok:
                    return self._submariner_state

                # success to run self._cleanup_join_submariner_broker()
                self._submariner_state = SubmarinerState.BROKER_CLEANING

                return self._submariner_state

            else:
                # check and update submariner state
                return self._set_submariner_gateway_connect_status()

        elif self._submariner_state == SubmarinerState.BROKER_CLEANING:

            if self._is_submariner_components_cleaned():
                # restart network
                # LocalHostCommand.network_restart()

                # if submariner cleaning is completed,
                self._submariner_state = SubmarinerState.BROKER_NA

                if self._is_mc_config_state_disconnecting():
                    # if BROKER_CLEANING is on by self._cleanup_join_submariner_broker()
                    ok, error_message = ClusterDAO.reset_multi_cluster_connection()

                    if not ok:
                        self._logger.error('Failed in ClusterDAO.reset_multi_cluster_connection(), '
                                           'caused by ' + error_message)

                    # reset multi-cluster-config
                    ok, error_message = ClusterDAO.reset_multi_cluster_config_request()

                    if not ok:
                        self._logger.error('Failed in ClusterDAO.reset_multi_cluster_config_request(), '
                                           'caused by ' + error_message)

            return self._submariner_state

        elif self._submariner_state == SubmarinerState.GATEWAY_CONNECTING:
            self._set_submariner_gateway_connect_status()

            if self._is_mc_config_state_disconnect_request():
                # handle multi-cluster disconnect request
                ok, error_message = self._handle_disconnect_request()

                if not ok:
                    return self._submariner_state

                # success to run self._cleanup_join_submariner_broker()
                self._submariner_state = SubmarinerState.BROKER_CLEANING

                return self._submariner_state

        elif self._submariner_state == SubmarinerState.GATEWAY_CONNECTED:
            self._set_submariner_gateway_connect_status()

            if self._is_mc_config_state_disconnect_request():
                # handle multi-cluster disconnect request
                ok, error_message = self._handle_disconnect_request()

                if not ok:
                    return self._submariner_state

                # success to run self._cleanup_join_submariner_broker()
                self._submariner_state = SubmarinerState.BROKER_CLEANING

                return self._submariner_state

            else:
                # check and update submariner state
                return self._set_submariner_gateway_connect_status()

        elif self._submariner_state == SubmarinerState.GATEWAY_CONNECT_ERROR:
            # update connection status
            self._set_submariner_gateway_connect_status()

            # if submariner network connected error
            if self._is_mc_config_state_disconnect_request():
                # if CEdge-center requests multi-cluster disconnect,
                # do cleanup submariner
                ok, error_message = self._cleanup_join_submariner_broker()

                if not ok:
                    self._logger.error('Failed in _cleanup_join_submariner_broker, '
                                       'caused by ' + error_message)

                    return self._submariner_state

                # success to run _cleanup_join_submariner_broker()
                self._submariner_state = SubmarinerState.BROKER_CLEANING

                # set multi-cluster-config state to 'Disconnecting'
                ok, error_message = ClusterDAO.set_mc_config_state_to_disconnecting()

                if not ok:
                    self._logger.error('Failed in ClusterDAO.set_mc_config_state_to_disconnecting(), '
                                       'caused by ' + error_message)

                return self._submariner_state

            else:
                if self._set_submariner_gateway_connect_status == SubmarinerState.GATEWAY_CONNECTED:
                    self._submariner_gateway_connect_errors = 0
                    return self._submariner_state

                self._submariner_gateway_connect_errors += 1

                if self._submariner_gateway_connect_errors > settings.SUBMARINER_GW_CONNECT_ERROR_WAIT:
                    # diagnosis error and recover
                    self.diagnose_and_recover_multi_cluster_network()
                    self._submariner_gateway_connect_errors = 0

            return self._submariner_state

        else:
            self._logger.error('Invalid _submariner_state. _submariner_state=' + self._submariner_state)

        return self._submariner_state

    def audit_gedge_components(self):
        """
        check CEdge cluster's components, provision components and service connections
        :return:
        """
        self._do_validate()
        self._once_validated = True

    def provision_gedge_components(self):
        """
        provision CEdge cluster's components and service connections
        :return:
        """
        if self._once_validated:
            self._do_provision()