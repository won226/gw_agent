import json
import threading
import requests
import time
import uuid

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger, WATCH_NETWORK_INTERVAL
from cluster.data_access_object import ClusterDAO
from cluster.event.object import EventObject
from cluster.watcher.resources import ResourceWatcher
from mqtt.service import MultiClusterNetworkService
from repository.cache.components import ComponentRepository
from repository.cache.metric import MetricRepository
from repository.cache.resources import ResourceRepository
from repository.common.k8s_client import Connector
from repository.model.netstat.endpoint import EndpointNetwork
from cluster.common.type import Event, ThreadType
from cluster.notifier.notify import Notifier
from repository.cache.network import NetworkStatusRepository
from repository.common.type import NetStat, MultiClusterRole, ClusterSessionStatus, ClusterNetworkConnectionStatus
from repository.model.netstat.multi_cluster import MultiClusterNetwork
from repository.model.netstat.service import ServiceExport, ServiceImport
from utils.threads import ThreadUtil
from utils.validate import Validator


class NetworkWatcher:
    """
    Watch gedge-center and connected cluster connection
    """
    _notifier = None
    _watch_threads = {}
    _center_network_name = None
    _mc_network_name = None
    _k8s_connector = None
    _last_connection_error_date = None
    _custom_obj = None

    # Center agent rest API error definition for network watcher
    SUCCESS = 'no_error'
    ClusterDataNotReady = 'Cluster data is not ready'
    NotFoundCenterNetworkError = 'Not found center network'
    NotFoundCenterClusterName = 'Not found cluster name'
    ResourceBusy = 'Resource is busy or locked'
    KeyErrorInResponseBody = 'Key error in response body'
    FailToRequest = 'Fail to request'
    InvalidHttpStatus = 'Invalid http response status code returns'
    HttpConnectionError = 'Http connection error'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()
        return cls._instance

    def _config(self):
        """
        configure NetworkWatcher
        :return:
        """
        self._logger = get_logger(__name__)
        self._k8s_connector = Connector()
        self._custom_obj = self._k8s_connector.custom_objects_api()

        # set self object to NetworkStatusRepository
        NetworkStatusRepository().set_mc_network_status_watcher(self)

        # add watch to gather center, multi-cluster network status
        self._add_watch(ThreadType.THREAD_WATCHDOG)
        self._add_watch(NetStat.CENTER_NETWORK)
        self._add_watch(NetStat.MULTI_CLUSTER_NETWORK)

    def _add_watch(self, target):
        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'paused': False,
            'pause_cond': threading.Condition(threading.Lock()),
            'callback_access_time': None
        }

    def start(self):
        """
        start network status watcher threads
        :return:
        """
        for _, value in self._watch_threads.items():
            if value['target'] == NetStat.MULTI_CLUSTER_NETWORK:
                value['paused'] = True

            value['thread'] = threading.Thread(target=self._watch_callback, args=(value['target'],), daemon=True)
            value['thread'].start()

    def is_alive(self, target):
        """
        is target thread is alive
        :param target:
        :return:
        """
        return self._watch_threads[target]['thread'].is_alive()

    def reset_callback_access_time(self, target):
        """
        set callback access time
        :param target:
        :return:
        """
        watch = self._watch_threads[target]
        watch['callback_access_time'] = None

    def set_callback_access_time(self, target):
        """
        set callback access time
        :param target:
        :return:
        """
        watch = self._watch_threads[target]
        watch['callback_access_time'] = time.time()

    def is_paused(self, target) -> bool:
        """
        is target thread is paused
        :param target:
        :return:
        """
        return self._watch_threads[target]['paused']

    def pause(self, target):
        """
        pause thread
        :param target:
        :return:
        """
        self._logger.debug('[PAUSE] MC NETWORK STATUS THREAD')
        watch = self._watch_threads[target]
        watch['paused'] = True

    def resume(self, target):
        """
        resume thread
        :param target:
        :return:
        """
        self._logger.debug('[RESUME] MC NETWORK STATUS THREAD')
        watch = self._watch_threads[target]
        watch['pause_cond'].acquire()
        watch['paused'] = False
        watch['pause_cond'].notify()
        watch['pause_cond'].release()

    def get_freezing_duration(self, target):
        """
        get freezing duration
        :param target:
        :return:
        """
        watch = self._watch_threads[target]

        if not watch or not watch['callback_access_time']:
            return 0

        return time.time() - watch['callback_access_time']

    def start_multi_cluster_network_monitor(self):
        """
        start multi cluster network status monitoring thread
        :return:
        """
        if self.is_paused(NetStat.MULTI_CLUSTER_NETWORK):
            self.resume(NetStat.MULTI_CLUSTER_NETWORK)

    def stop_multi_cluster_network_monitor(self):
        """
        stop multi-cluster network status monitoring thread
        :return:
        """
        NetworkStatusRepository().clear_mc_network()

        if not self.is_paused(NetStat.MULTI_CLUSTER_NETWORK):
            self.pause(NetStat.MULTI_CLUSTER_NETWORK)

    def _watch_callback(self, target):
        """
        thread callback for watch network(cluster, multi-cluster network, center connection)
        :return:
        """
        logger = self._logger
        watch = self._watch_threads[target]

        while True:
            # thread pause
            with watch['pause_cond']:
                while watch['paused']:
                    if target == NetStat.MULTI_CLUSTER_NETWORK:
                        NetworkStatusRepository().clear_mc_network()
                    self.reset_callback_access_time(target)
                    watch['pause_cond'].wait()

            self.set_callback_access_time(target)
            if target == NetStat.MULTI_CLUSTER_NETWORK:
                ok, error_message = self._collect_multi_cluster_network_status()
                if not ok:
                    self._logger.debug(error_message)
                    NetworkStatusRepository().clear_mc_network()

            elif target == NetStat.CENTER_NETWORK:
                self._audit_cluster_session()

            elif target == ThreadType.THREAD_WATCHDOG:
                self._thread_watchdog()

            else:
                logger.error('Invalid network target, EXIT program.')
                ThreadUtil.exit_process()

            time.sleep(WATCH_NETWORK_INTERVAL)

    def initialize_cluster_session(self) -> (bool, str):
        """
        initialize cluster session to center
        :return: (bool) success, (str) error_message
        """
        # check whether center network interface(http, https, amqp, etc) is defined or not
        name = NetworkStatusRepository().get_center_network_name()
        if name is None:
            return False, self.NotFoundCenterNetworkError

        # cluster_id refers cluster name
        cluster_id = ResourceRepository().get_cluster_id()
        if cluster_id is None:
            return False, self.NotFoundCenterClusterName

        # If cluster session is initializing, do not anything
        cluster_session_status = NetworkStatusRepository().get_cluster_session_status()
        if cluster_session_status == ClusterSessionStatus.CLUSTER_SESSION_INITIALIZING.value:
            return True, self.ResourceBusy

        # If all cluster data is ready, do not anything
        if ResourceWatcher().is_all_resource_data_ready():
            # suspend resource watch
            ResourceWatcher().suspend_all_watches()

            # get resource bulk data
            bulk_resource = ResourceRepository().get_bulk_resource()
            cluster_initialize_data = {'resource': bulk_resource.to_dict()}

            # resume resource watch
            ResourceWatcher().resume_all_watches()

        else:
            return False, self.ClusterDataNotReady

        try:
            # request to initialize cluster session
            url = name + '/api/agent/v1' \
                         '/cluster/{cluster_id}/initialize'.format(cluster_id=cluster_id)
            headers = {'Content-Type': 'application/json; charset=utf-8'}

            response = requests.post(url,
                                     headers=headers,
                                     data=json.dumps(cluster_initialize_data),
                                     timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if 'error' not in content:
                    self._logger.error('Key error(\'error\') in body content.')
                    return False, self.KeyErrorInResponseBody

                if content['error'] != 'no_error':
                    error = content['error']
                    self._logger.error('Fail to initialize cluster session caused by {}'.format(error))
                    return False, self.FailToRequest

                return True, self.SUCCESS

            else:
                error = 'Invalid http response status code. status code = {}'.format(response.status_code)
                self._logger.error(error)
                return False, self.InvalidHttpStatus

        except requests.exceptions.ConnectionError:
            error = 'Http request connection error'
            self._logger.error(error)
            return False, self.HttpConnectionError

    def _thread_watchdog(self):
        """
        thread watchdog callback
        :return:
        """
        for key, _ in self._watch_threads.items():
            if key != ThreadType.THREAD_WATCHDOG:
                val = self.get_freezing_duration(key)

                if val > settings.THREAD_FREEZING_TIMEOUT:
                    t = self._watch_threads[key]['thread']
                    if t:
                        for i in range(0, 10):
                            if t.is_alive():
                                ThreadUtil.raise_SystemExit_exception(t)
                                t.join(1)
                            else:
                                break

                    if t.is_alive():
                        self._logger.error('Failed to exit freezing thread')

                    # start freezing thread
                    self._watch_threads[key]['thread'] = threading.Thread(
                        target=self._watch_callback, args=(key,), daemon=True)
                    self._watch_threads[key]['thread'].start()
        return

    def _audit_cluster_session(self):
        """
        audit center session
        role: audit center network connection
              audit center network session
        :return:
        """
        name = NetworkStatusRepository().get_center_network_name()

        if name is None:
            return

        # cluster_id refers cluster name
        cluster_id = ResourceRepository().get_cluster_id()
        if cluster_id is None:
            return

        try:
            # Request keep alive
            url = name + '/api/agent/v1' \
                         '/cluster/{cluster_id}/keep_alive'.format(cluster_id=cluster_id)

            headers = {'Content-Type': 'application/json; charset=utf-8'}

            keep_alive_content = {
                'submariner_state': ComponentRepository().get_submariner_state().value,
            }

            response = requests.post(url,
                                     headers=headers,
                                     data=json.dumps(keep_alive_content),
                                     timeout=settings.REST_REQUEST_TIMEOUT)
            connection_status = ClusterNetworkConnectionStatus.CONNECTED.value

            if response.status_code == 200:
                content = json.loads(response.content)
                session_status = content['cluster_session_status']
                has_disconnect_request = content['has_disconnect_request']

                if has_disconnect_request:
                    ok, cluster_object, error_message = ClusterDAO.get_cluster()

                    if not ok:
                        self._logger('Failed in ClusterDAO.get_cluster(), '
                                     'caused by ' + error_message)
                    else:
                        mc_connect_id = cluster_object.mc_connect_id

                        if mc_connect_id:
                            MultiClusterNetworkService.disconnect_broker(cluster_id=cluster_id,
                                                                         request_id=str(uuid.uuid4()),
                                                                         connect_id=mc_connect_id)

                # FATAL: API error
                if 'cluster_session_status' not in content:
                    self._logger.error('Fatal: Not found key \'cluster_session_status\' in response body')
                    return

                # Get previous session status
                previous_session_status = NetworkStatusRepository().get_cluster_session_status()

                if previous_session_status == ClusterSessionStatus.UNAVAILABLE.value:
                    if session_status == ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value or \
                            ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
                        '''
                        CLUSTER_SESSION_NOT_ESTABLISHED: agent is launching
                        CLUSTER_SESSION_ESTABLISHED: center is restarted after failure '''

                        if ResourceWatcher().is_all_resource_data_ready() and \
                                NetworkStatusRepository().get_center_network_name():
                            status = ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value
                            NetworkStatusRepository().set_cluster_session_status(name, status)

                    else:
                        self._logger.error('Fatal: Invalid ClusterSessionStatus')

                elif previous_session_status == ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value:
                    if session_status == ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value or \
                            ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
                        '''
                        CLUSTER_SESSION_NOT_ESTABLISHED: session not initialized ever
                        CLUSTER_SESSION_ESTABLISHED: agent is restarted after failure '''
                        # initialize cluster session
                        ok, error_message = self.initialize_cluster_session()
                        if ok:
                            ''' 
                            If session initialization is succeed, 
                            change session status to CLUSTER_SESSION_INITIALIZING '''
                            status = ClusterSessionStatus.CLUSTER_SESSION_INITIALIZING.value
                            NetworkStatusRepository().set_cluster_session_status(name, status)

                        else:
                            if error_message == self.HttpConnectionError:
                                connection_status = ClusterNetworkConnectionStatus.TEMPORARY_NETWORK_FAILURE.value

                    else:
                        self._logger.error('Fatal: Invalid ClusterSessionStatus')

                elif previous_session_status == ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
                    if session_status == ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
                        '''
                        CLUSTER_SESSION_ESTABLISHED: cluster session is alive '''
                        pass

                    elif session_status == ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value:
                        ''' 
                        CLUSTER_SESSION_NOT_ESTABLISHED: center is restarted after failure '''
                        status = ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value
                        NetworkStatusRepository().set_cluster_session_status(name, status)
                        Notifier().flush_events()

                    else:
                        self._logger.error('Fatal: Invalid ClusterSessionStatus')

                elif previous_session_status == ClusterSessionStatus.CLUSTER_SESSION_INITIALIZING.value:
                    if session_status == ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value or \
                            session_status == ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value:
                        '''
                        CLUSTER_SESSION_ESTABLISHED: success to initialize cluster session 
                        CLUSTER_SESSION_NOT_ESTABLISHED: fail to initialize cluster session'''
                        NetworkStatusRepository().set_cluster_session_status(name, session_status)

                    else:
                        self._logger.error('Fatal: Invalid ClusterSessionStatus')
                else:
                    self._logger.error('Fatal: Invalid ClusterSessionStatus')

            else:
                # Fatal error: http response error
                error = 'Fatal: Invalid http response status code. status code = {}'.format(response.status_code)
                self._logger.error(error)

        except requests.exceptions.ConnectionError:
            connection_status = ClusterNetworkConnectionStatus.TEMPORARY_NETWORK_FAILURE.value

        '''
        check network connection status 
        '''
        # set network connection status
        NetworkStatusRepository().set_center_network_connection_status(name, connection_status)

        # If network connection status is changed to NETWORK_FAILURE,
        if NetworkStatusRepository().get_center_network_connection_status() == \
                ClusterNetworkConnectionStatus.NETWORK_FAILURE.value:
            '''
            NETWORK_FAILURE: network failure 
            '''
            # Set center session status to CLUSTER_SESSION_NOT_ESTABLISHED
            session_status = ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value
            NetworkStatusRepository().set_cluster_session_status(name, session_status)

    def _collect_multi_cluster_network_status(self) -> (bool, str):
        """
        collect multi cluster network status
        :return:
        (bool) True - success
        (str) error message
        """
        self._logger.debug('[CALL] MC_STATUS THREAD')

        """
        GET cluster info.
        - API group: submariner.io
        - API version: v1
        - name: cluster
        - plural: clusters
        """
        try:
            result = self._custom_obj.list_cluster_custom_object(
                group='submariner.io',
                plural='clusters',
                version='v1',
                _request_timeout=settings.REST_REQUEST_TIMEOUT)

        except Exception as exc:  # not exist ApiService resource
            error_message = 'Failed in list_cluster_custom_object(submariner.io.clusters.v1) request, ' \
                            'caused by ' + get_exception_traceback(exc)
            return False, error_message

        error_message = 'Failed in list_cluster_custom_object(submariner.io.clusters.v1) response, caused by '

        if 'items' not in result:
            error_message += 'not found items in body'
            return False, error_message

        items = result['items']
        if len(items) <= 0:
            error_message += 'not found items in body'
            return False, error_message

        clusters = []
        for item in items:
            if 'metadata' not in item:
                error_message += 'not found items.metadata'
                return False, error_message

            if 'namespace' not in item['metadata']:
                error_message += 'not found items.metadata.namespace'
                return False, error_message

            if item['metadata']['namespace'] != 'submariner-operator':
                continue

            if 'spec' not in item:
                error_message += 'not found items.spec'
                return False, error_message

            spec = item['spec']
            var = {
                'cluster_id': spec['cluster_id'],
                'cluster_cidr': spec['cluster_cidr'][0],
                'service_cidr': spec['service_cidr'][0],
                'global_cidr': spec['global_cidr'][0],
            }
            clusters.append(var)

        """
        GET GW endpoint info.
        - API group: submariner.io
        - API version: v1alpha1
        - name: submariner
        - plural: submariners
        """
        try:
            result = self._custom_obj.list_cluster_custom_object(
                group='submariner.io',
                plural='submariners',
                version='v1alpha1',
                _request_timeout=settings.REST_REQUEST_TIMEOUT)

        except Exception as exc:  # not exist ApiService resource
            error_message = 'Failed in list_cluster_custom_object(submariner.io.submariners.v1alpha1) request, ' \
                            'caused by ' + get_exception_traceback(exc)
            return False, error_message

        error_message = 'Failed in list_cluster_custom_object(submariner.io.submariners.v1alpha1) response, caused by '

        if 'items' not in result:
            error_message += 'not found items'
            return False, error_message

        items = result['items']

        if len(items) <= 0:
            error_message += 'not found items'
            return False, error_message

        if 'spec' not in items[0]:
            error_message += 'not found items.spec'
            return False, error_message

        if 'status' not in items[0]:
            error_message += 'not found items.status'
            return False, error_message

        spec = items[0]['spec']
        stat = items[0]['status']

        if 'clusterID' not in spec:
            error_message += 'not found items.spec.clusterID'
            return False, error_message
        cluster_id = spec['clusterID']

        if 'globalCIDR' not in stat:
            error_message += 'not found items.spec.globalCIDR'
            return False, error_message
        val = stat['globalCIDR']

        tokens = val.split('.')
        broker_global_cidr = '{}.0.0.0/8'.format(tokens[0])

        if 'cableDriver' not in spec:
            error_message += 'not found items.spec.cableDriver'
            return False, error_message
        cable_driver = spec['cableDriver']

        broker_role = MultiClusterRole.UNKNOWN.value
        endpoints = []

        if 'gateways' not in stat:
            error_message += 'not found items.status.gateways'
            return False, error_message

        if len(stat['gateways']) > 0:
            gateway = stat['gateways'][0]  # only support single gateway for a cluster

            if 'localEndpoint' not in gateway or 'private_ip' not in gateway['localEndpoint']:
                error_message += 'not found items.status.gateways.localEndpoint.private_ip'
                return False, error_message
            gateway_ip = gateway['localEndpoint']['private_ip']

            if 'brokerK8sApiServer' not in spec:
                error_message += 'not found items.spec.brokerK8sApiServer'
                return False, error_message
            broker_api_server = spec['brokerK8sApiServer']

            if gateway_ip in broker_api_server:
                broker_role = MultiClusterRole.LOCAL.value
            else:
                broker_role = MultiClusterRole.REMOTE.value

            """ local gateway connections """
            endpoint = EndpointNetwork(stat['clusterID'])
            try:
                endpoint.set_role(MultiClusterRole.LOCAL.value)
                endpoint.set_public_ip(gateway['localEndpoint']['public_ip'])
                endpoint.set_gateway_ip(gateway_ip)
                endpoint.set_hostname(gateway['localEndpoint']['hostname'])
                endpoint.set_service_cidr(stat['serviceCIDR'])
                endpoint.set_cluster_cidr(stat['clusterCIDR'])
                endpoint.set_global_cidr(stat['globalCIDR'])
            except Exception as exc:
                return False, 'set() TypeError in local EndpointNetwork(), caused by ' + get_exception_traceback(exc)

            endpoints.append(endpoint)

            """ remote gateway connections """
            if len(gateway['connections']) > 0:
                if 'connections' not in gateway:
                    error_message += 'not found item.spec.gateway.connections'
                    return False, error_message

                for connection in gateway['connections']:
                    service_cidr = None
                    cluster_cidr = None
                    global_cidr = None

                    for cluster in clusters:
                        if cluster['cluster_id'] == connection['endpoint']['cluster_id']:
                            service_cidr = cluster['service_cidr']
                            cluster_cidr = cluster['cluster_cidr']
                            global_cidr = cluster['global_cidr']

                    endpoint = EndpointNetwork(name=connection['endpoint']['cluster_id'])

                    try:
                        endpoint.set_role(MultiClusterRole.REMOTE.value)
                        endpoint.set_public_ip(connection['endpoint']['public_ip'])
                        endpoint.set_gateway_ip(connection['endpoint']['private_ip'])
                        endpoint.set_hostname(connection['endpoint']['hostname'])
                        endpoint.set_status(connection['status'])
                        endpoint.set_status_message(connection['statusMessage'])
                        endpoint.set_service_cidr(service_cidr)
                        endpoint.set_cluster_cidr(cluster_cidr)
                        endpoint.set_global_cidr(global_cidr)
                    except Exception as exc:
                        return False, 'set() TypeError in remote EndpointNetwork(), caused by ' + get_exception_traceback(exc)

                    try:
                        latency = connection['latencyRTT']['average']
                        divider = 1

                        if 'µs' in latency:
                            divider = 1000
                            latency = latency.replace('µs', '')
                        elif 'ms' in latency:
                            latency = latency.replace('ms', '')
                        elif 's' in latency:
                            latency = latency.replace('s', '')
                            divider = 0.001
                        else:
                            self._logger.error('Invalid latency value. latency=' + latency)

                        # unit: ms, µs
                        if Validator.is_enable_cast_to_float(latency):
                            latency = float(latency) / divider
                    except KeyError:
                        latency = float(0)

                    try:
                        MetricRepository().set_mc_network_latency(
                            name=connection['endpoint']['cluster_id'],
                            latency=latency,
                            timestamp=time.time())
                    except Exception as exc:
                        return False, 'set() TypeError in MetricRepository().set_mc_network_latency(), ' \
                                      'caused by ' + get_exception_traceback(exc)

                    endpoints.append(endpoint)

        """
        PARSE broker info.
        - API group: submariner.io
        - API version: v1alpha1
        - name: servicediscovery
        - plural: ServiceDiscoveries
        """
        try:
            result = self._custom_obj.list_cluster_custom_object(
                group='submariner.io',
                plural='servicediscoveries',
                version='v1alpha1',
                _request_timeout=settings.REST_REQUEST_TIMEOUT)
        except Exception as exc:  # not exist ApiService resource
            error_message = 'Failed in list_cluster_custom_object(submariner.io.servicediscoveries.v1alpha1) ' \
                            'request, caused by ' + get_exception_traceback(exc)
            return False, error_message

        error_message = 'Failed in list_cluster_custom_object(submariner.io.servicediscoveries.v1alpha1) response, ' \
                        'caused by '

        if 'items' not in result:
            error_message += 'not found items'
            return False, error_message
        items = result['items']

        if len(items) <= 0:
            error_message += 'not found items'
            return False, error_message

        if 'spec' not in items[0]:
            error_message += 'not found items.spec'
            return False, error_message
        spec = items[0]['spec']

        if 'globalnetEnabled' not in spec:
            error_message += 'not found items.spec.globalnetEnabled'
            return False, error_message
        globalnet = spec['globalnetEnabled']

        if Validator.is_enable_cast_to_bool(globalnet):
            try:
                globalnet = Validator.cast_to_bool(globalnet)
            except ValueError:
                globalnet = True

        try:
            mc_network = MultiClusterNetwork(name=cluster_id)
            mc_network.set_broker_role(broker_role)
            mc_network.set_global_cidr(broker_global_cidr)
            mc_network.set_cable_driver(cable_driver)
            mc_network.set_globalnet(globalnet)
        except Exception as exc:
            error_message = 'set() TypeError in local MultiClusterNetwork(name=cluster_id), ' \
                            'caused by ' + get_exception_traceback(exc)
            return False, error_message

        # set multi-cluster network status
        try:
            NetworkStatusRepository().set_mc_network(mc_network)
        except Exception as exc:
            error_message = 'Failed in NetworkStatusRepository().set_mc_network(mc_network), ' \
                            'caused by ' + get_exception_traceback(exc)
            return False, error_message

        # set multi-cluster network's endpoints status
        if len(endpoints) > 0:
            try:
                NetworkStatusRepository().set_mc_network_endpoints(endpoints)
            except Exception as exc:
                error_message = 'Failed in NetworkStatusRepository().set_mc_network_endpoints(endpoints), ' \
                                'caused by ' + get_exception_traceback(exc)
                return False, error_message

        # send multi-cluster network status event
        event = EventObject(Event.MODIFIED.value,
                            NetStat.MULTI_CLUSTER_NETWORK.value,
                            NetworkStatusRepository().get_mc_network())

        Notifier().put_event(event)

        """
        PARSE service imports/exports
        - API group: multicluster.x-k8s.io
        - API version: v1alpha1
        - plural: serviceimports
        """
        try:
            result = self._custom_obj.list_cluster_custom_object(
                group='multicluster.x-k8s.io',
                plural='serviceimports',
                version='v1alpha1',
                _request_timeout=settings.REST_REQUEST_TIMEOUT)
        except Exception as exc:  # not exist ApiService resource
            error_message = 'Failed in list_cluster_custom_object(multicluster.x-k8s.io.serviceimports.v1alpha1) ' \
                            'request, caused by ' + get_exception_traceback(exc)
            return False, error_message

        if 'items' not in result:
            error_message += 'not found items'
            return False, error_message
        items = result['items']

        service_exports = []
        service_imports = []

        error_message = 'Failed in list_cluster_custom_object(multicluster.x-k8s.io.serviceimports.v1alpha1) ' \
                        'response, caused by '

        if len(items) > 0:
            for item in items:
                if 'metadata' not in item:
                    error_message += 'not found items.metadata'
                    return False, error_message

                metadata = item['metadata']
                if metadata['namespace'] != 'submariner-operator':
                    continue

                if 'spec' not in item:
                    error_message += 'not found items.spec'
                    return False, error_message

                spec = item['spec']

                if 'labels' not in metadata:
                    error_message += 'not found items.spec.labels'
                    self._logger.debug(error_message)
                    continue

                if 'lighthouse.submariner.io/sourceCluster' not in metadata['labels']:
                    error_message += 'not found items.spec.labels.lighthouse.submariner.io/sourceCluster'
                    self._logger.debug(error_message)
                    continue
                source_cluster = metadata['labels']['lighthouse.submariner.io/sourceCluster']

                if 'lighthouse.submariner.io/sourceNamespace' not in metadata['labels']:
                    error_message += 'not found items.spec.labels.lighthouse.submariner.io/sourceNamespace'
                    self._logger.debug(error_message)
                    continue
                source_namespace = metadata['labels']['lighthouse.submariner.io/sourceNamespace']

                if 'lighthouse.submariner.io/sourceName' not in metadata['labels']:
                    error_message += 'not found items.spec.labels.lighthouse.submariner.io/sourceName'
                    self._logger.debug(error_message)
                source_name = metadata['labels']['lighthouse.submariner.io/sourceName']

                if 'ips' not in spec:
                    error_message += 'not found items.spec.ips'
                    self._logger.debug(error_message)
                    continue
                source_ip = spec['ips'][0]

                if 'ports' not in spec or 'port' not in spec['ports'][0]:
                    error_message += 'not found items.spec.ports.port'
                    self._logger.debug(error_message)
                    continue
                source_port = spec['ports'][0]['port']

                if 'ports' not in spec or 'protocol' not in spec['ports'][0]:
                    error_message += 'not found items.spec.ports.protocol'
                    self._logger.debug(error_message)
                    continue
                source_protocol = spec['ports'][0]['protocol']

                dns = '{name}.{namespace}.svc.clusterset.local'.format(
                    name=source_name,
                    namespace=source_namespace)

                if source_cluster == cluster_id:
                    try:
                        svc_export = ServiceExport()
                        svc_export.set_cluster_id(source_cluster)
                        svc_export.set_namespace(source_namespace)
                        svc_export.set_name(source_name)
                        svc_export.set_ip(source_ip)
                        svc_export.set_port(source_port)
                        svc_export.set_protocol(source_protocol)
                        svc_export.set_dns(dns)
                        service_exports.append(svc_export)
                    except Exception as exc:
                        error_message = 'set() TypeError in ServiceExport(), caused by ' + \
                                        get_exception_traceback(exc)
                        self._logger.debug(error_message)
                        continue
                else:
                    try:
                        svc_import = ServiceImport()
                        svc_import.set_cluster_id(source_cluster)
                        svc_import.set_namespace(source_namespace)
                        svc_import.set_name(source_name)
                        svc_import.set_ip(source_ip)
                        svc_import.set_port(source_port)
                        svc_import.set_protocol(source_protocol)
                        svc_import.set_dns(dns)
                        service_imports.append(svc_import)
                    except Exception as exc:
                        error_message = 'set() TypeError in ServiceImport(), caused by ' + get_exception_traceback(exc)
                        self._logger.debug(error_message)
                        continue

        """ 
        NOTIFY event for service export 
        """
        NetworkStatusRepository().set_mc_network_service_exports(service_exports)
        Notifier().put_event(EventObject(event_type=Event.MODIFIED.value,
                                         object_type=NetStat.SERVICE_EXPORTS.value,
                                         object_value=service_exports))

        """ 
        NOTIFY event for service import 
        """
        NetworkStatusRepository().set_mc_network_service_imports(service_imports)
        Notifier().put_event(EventObject(event_type=Event.MODIFIED.value,
                                         object_type=NetStat.SERVICE_IMPORTS.value,
                                         object_value=service_imports))
        return True, None
