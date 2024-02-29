import time

import os
import shutil

import kubernetes

from gw_agent.common.error import get_exception_traceback

from gw_agent import settings
from cluster.command.kubernetes import KubeCommand
from repository.cache.network import NetworkStatusRepository
from repository.cache.resources import ResourceRepository
from repository.common.k8s_client import Connector
from repository.common.type import MultiClusterRole
from utils.run import RunCommand

SUBCTL = ' '.join(settings.CEDGE_BINS['subctl'])
KUBECTL = ' '.join(settings.CEDGE_BINS['kubectl'])
CURL = ' '.join(settings.CEDGE_BINS['curl'])


# noinspection PyTypeChecker
class SubmarinerCommand:
    """
    SubmarinerCommand class
    """

    ''' After submariner broker deployed, check below resource's status. '''
    submariner_operator_resource = {
        'namespaces': [
            'submariner-k8s-broker',
            'submariner-operator'
        ],
        'apiservices': [
            'v1.submariner.io',
            'v1alpha1.submariner.io',
            'v1alpha1.multicluster.x-k8s.io'
        ],
        # kubectl get crds | grep -iE 'submariner|multicluster.x-k8s.io'
        'customresourceobjects': [
            {
                'group': 'submariner.io',
                'plural': 'brokers',
                'version': 'v1alpha1'
            },
            {
                'group': 'submariner.io',
                'plural': 'clusterglobalegressips',
                'version': 'v1'
            },
            {
                'group': 'submariner.io',
                'plural': 'clusters',
                'version': 'v1'
            },
            {
                'group': 'submariner.io',
                'plural': 'endpoints',
                'version': 'v1'
            },
            {
                'group': 'submariner.io',
                'plural': 'gateways',
                'version': 'v1'
            },
            {
                'group': 'submariner.io',
                'plural': 'globalegressips',
                'version': 'v1'
            },
            {
                'group': 'submariner.io',
                'plural': 'globalingressips',
                'version': 'v1'
            },
            {
                'group': 'submariner.io',
                'plural': 'servicediscoveries',
                'version': 'v1alpha1'
            },
            {
                'group': 'submariner.io',
                'plural': 'submariners',
                'version': 'v1alpha1'
            },
            {
                'group': 'multicluster.x-k8s.io',
                'plural': 'serviceexports',
                'version': 'v1alpha1'
            },
            {
                'group': 'multicluster.x-k8s.io',
                'plural': 'serviceimports',
                'version': 'v1alpha1'
            },
        ],
    }

    ''' 
    After submariner broker joined, check below resource's status.
    And remote endpoint connection status whether it is 'connected' or not. 
    '''
    submariner_component_resource = {
        'deployments': [
            'submariner-operator',
            'submariner-lighthouse-agent',
            'submariner-lighthouse-coredns'
        ],
        'daemonsets': [
            'submariner-gateway',
            'submariner-globalnet',
            'submariner-routeagent',
        ],
        'services': [
            'submariner-operator-metrics',
            'submariner-gateway-metrics',
            'submariner-globalnet-metrics',
            'submariner-lighthouse-agent-metrics',
            'submariner-lighthouse-coredns',
            'submariner-lighthouse-coredns-metrics',
        ],
    }
    logger = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()
        return cls._instance

    def _config(self):
        self.logger = settings.get_logger(__name__)

    @staticmethod
    def deploy_subctl():
        """
        deploy subctl
        :return:
        """
        ''' remove subctl '''
        if os.path.isfile('/root/.local/bin/subctl'):
            os.remove('/root/.local/bin/subctl')
        if os.path.isfile('/sbin/subctl'):
            os.remove('/sbin/subctl')

        ''' install subctl '''
        cmdline = ' '.join([CURL, '-Ls', 'https://get.submariner.io', '|', 'VERSION=0.13.1', 'bash'])
        ok, stdout, stderr = RunCommand.execute_bash_wait(cmdline)
        if not ok:
            return ok, stdout, stderr

        ''' create subctl symbolic link to "/sbin/" '''
        cmdline = ' '.join(['ln', '-s', '/root/.local/bin/subctl', '/sbin'])

        return RunCommand.execute_shell_wait(cmdline)

    def create_broker(self):
        """
        deploy submariner broker_info
        :return:
        (bool) True - success, False - fail
        (str) stdout
        (str) stderr
        """
        self.logger.info('subctl deploy-broker --version {} --globalnet'.format(settings.SUBMARINER_VERSION))

        # broker-info.subm creating path
        broker_info_file = os.path.join(os.getcwd(), 'broker-info.subm')

        # delete broker-info.subm file in current directory
        if os.path.isfile(broker_info_file):
            os.remove(broker_info_file)

        cmdline = ' '.join([SUBCTL,
                            'deploy-broker',
                            '--version', settings.SUBMARINER_VERSION,
                            '--globalnet'])

        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        if not ok:
            return ok, stdout, stderr

        # remove old broker-info.subm files in local broker directory
        for path in os.listdir(settings.LOCAL_BROKER_INFO):
            if os.path.isfile(os.path.join(settings.LOCAL_BROKER_INFO, path)):
                if 'broker-info.subm.' in path:
                    os.remove(os.path.join(settings.LOCAL_BROKER_INFO, path))

        # If fail to create broker-info.subm file,
        if not os.path.isfile(broker_info_file):
            self.logger.error('Fail to create broker-info.subm')
            return False, stdout, 'File not created, file=broker-info.subm'

        # move new broker-info.subm file to local broker directory
        shutil.move(broker_info_file, os.path.join(settings.LOCAL_BROKER_INFO, 'broker-info.subm'))

        return ok, stdout, stderr

    def delete_submariner(self):
        """
        delete submariner (broker, broker-join components)
        :return:
        (bool) True - success, False - fail
        (str) stdout
        (str) stderr
        """
        self.delete_submariner_crds()
        self.delete_submariner_components()
        self.delete_submariner_namespaces()
        # self.replace_finalizer_for_submariner_namespaces()

        return True, None, None

    def delete_submariner_namespaces(self):
        """
        delete submariner namespace
        :return:
        """
        core_v1_api = Connector().core_v1_api()
        errors = []
        namespaces = self.submariner_operator_resource['namespaces']

        for namespace in namespaces:
            try:
                # core_v1_api.delete_namespace(namespace, grace_period_seconds=10)
                core_v1_api.delete_namespace(namespace)
            except Exception as exc:
                if type(exc) == kubernetes.client.exceptions.ApiException:
                    if exc.reason == 'Not Found':
                        continue
                else:
                    error = get_exception_traceback(exc)
                    errors.append(error)
                    self.logger.error(error)
        if len(errors) > 0:
            return False, '', ';'.join(errors)

        return True, '', ''

    def replace_finalizer_for_submariner_namespaces(self):
        """
        delete submariner namespaces
        :return:
        (bool) success
        (str) stdout
        (str) stderr
        """
        api_client = Connector().core_v1_api()
        namespaces = self.submariner_operator_resource['namespaces']
        errors = []
        for namespace in namespaces:
            try:
                resource = api_client.read_namespace(namespace)
                if resource.spec.finalizers is not None:
                    resource.spec.finalizers = []
                    api_client.replace_namespace_finalize(namespace, resource)
            except Exception as exc:
                if type(exc) == kubernetes.client.exceptions.ApiException:
                    if exc.reason == 'Not Found':
                        continue
                else:
                    error = get_exception_traceback(exc)
                    self.logger.error(error)
                    errors.append(error)

        if len(errors) > 0:
            return False, '', ';'.join(errors)

        return True, '', ''

    def delete_submariner_crds(self):
        """
        delete submariner crds
        :return:
        """
        crds = self.submariner_operator_resource['customresourceobjects']
        errors = []

        for crd in crds:
            ok, stdout, stderr = KubeCommand().delete_crd(crd['group'], crd['plural'])

            if not ok:
                errors.append(errors)

        if len(errors) > 0:
            return False, '', ';'.join(errors)

        return True, '', ''

    def delete_submariner_components(self):
        """
        delete submariner broker join components
        :return:
        """
        namespace = 'submariner-operator'
        errors = []

        ''' delete submariner join components '''
        for key, value in self.submariner_component_resource.items():
            for name in value:
                if key == 'services':
                    if ResourceRepository().is_service_deployed(namespace, name):
                        ok, stdout, stderr = KubeCommand.delete_service(namespace, name)
                        if not ok:
                            self.logger.error('Fail to delete service({}) '
                                              'caused by {}'.format(name, stderr))
                    continue
                if key == 'daemonsets':
                    if ResourceRepository().is_daemonset_deployed(namespace, name):
                        # # apply patch
                        # path = '/spec/template/spec/nodeSelector'
                        # ok, stdout, stderr = KubeCommand().delete_path(namespace, 'daemonset', path, name)
                        # if not ok:
                        #     self.logger.error('Fail to delete path({}) '
                        #                       'caused by {}'.format(name, stderr))
                        # pods = ResourceRepository().get_pods_for_deployment(namespace, name)
                        ok, stdout, stderr = KubeCommand.delete_daemonset(namespace, name)
                        if not ok:
                            self.logger.error('Fail to delete daemonset({}) '
                                              'caused by {}'.format(name, stderr))
                        # for pod in pods:
                        #     ok, stdout, stderr = KubeCommand.delete_pod(namespace, pod)
                        #     if not ok:
                        #         self.logger.error('Fail to delete pod({}) '
                        #                           'caused by {}'.format(pod, stderr))
                    continue
                if key == 'deployments':
                    if ResourceRepository().is_deployment_deployed(namespace, name):
                        # apply scale to zero
                        # KubeCommand().adjust_scale_deployment(namespace, name, 0)
                        # pods = ResourceRepository().get_pods_for_deployment(namespace, name)
                        ok, stdout, stderr = KubeCommand.delete_deployment(namespace, name)
                        if not ok:
                            self.logger.error('Fail to delete deployment({}) '
                                              'caused by {}'.format(name, stderr))
                        # for pod in pods:
                        #     ok, stdout, stderr = KubeCommand.delete_pod(namespace, pod)
                        #     if not ok:
                        #         self.logger.error('Fail to delete pod({}) '
                        #                           'caused by {}'.format(pod, stderr))
                    continue

        if len(errors) > 0:
            return False, '', ';'.join(errors)

        return True, '', ''

    def restart_gateway(self):
        """
        restart gateway
        :return:
        """
        ok, _, stderr = KubeCommand().enable_master_schedulable()
        if not ok:
            self.logger.error(stderr)
            return ok, None, stderr

        ''' set label('submariner.io/gateway=true') to master node to assign gateway in master node '''
        master_node = KubeCommand().get_master_name()

        if not master_node:
            return False, None, 'Not found master node'

        KubeCommand().set_node_label(master_node, 'submariner.io/gateway=true')

        cmdline = ' '.join([KUBECTL,
                            'rollout', 'restart', 'daemonset', 'submariner-gateway', '-n', 'submariner-operator'])

        self.logger.info(cmdline)
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        if not ok:
            self.logger.error(stderr)

        KubeCommand().disable_master_schedulable()

        return True, None, None

    def join_broker(self, role, cluster_id, broker_info_file):
        """
        join broker
        :param role: (str) 'Local' or 'Remote'
        :param cluster_id: (str) cluster_id
        :param broker_info_file: (str) broker info file path
        :return:
        (bool) True - success, False - fail
        (str) stdout
        (str) stderr
        """
        if cluster_id is None or len(cluster_id) <=0 or type(cluster_id) != str:
            return False, None, 'Invalid cluster_id. Must input str as cluster_id'

        if not MultiClusterRole.validate(role):
            return False, None, 'Invalid role. Must input "Local" or "Remote" as role'

        if not os.path.isfile(broker_info_file):
            return False, None, 'broker-info.subm file is not existed'

        ''' set taint to enable to schedule submariner gateway to master node '''
        ok, _, stderr = KubeCommand().enable_master_schedulable()
        if not ok:
            self.logger.error(stderr)
            return ok, None, stderr

        ''' set label('submariner.io/gateway=true') to master node to assign gateway in master node '''
        master_node = KubeCommand().get_master_name()

        if not master_node:
            return False, None, 'Not found master node'

        KubeCommand().set_node_label(master_node, 'submariner.io/gateway=true')

        cmdline = ' '.join([SUBCTL,
                            'join', broker_info_file,
                            '--version', settings.SUBMARINER_VERSION,
                            '--clusterid', cluster_id,
                            '--cable-driver', settings.SUBMARINER_CABLE_DRIVER,
                            '--natt=false'])

        self.logger.info(cmdline)
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)
        if not ok:
            self.logger.error(stderr)

        ''' # set taint to disable to schedule submariner gateway to master node '''
        KubeCommand().disable_master_schedulable()


        return ok, stdout, stderr

    @staticmethod
    def export_service(namespace, name):
        """
        export service
        :param namespace: (str) service namespace
        :param name: (str) service name
        :return:
        (bool) True - success, False - fail
        (str) stdout
        (str) stderr
        """
        is_exported = NetworkStatusRepository().is_service_exported(namespace, name)
        if is_exported:
            return True, None, None

        if not ResourceRepository().is_service_deployed(namespace, name):
            return False, None, 'Not found service(ns={}, service={})'.format(namespace, name)

        cmdline = ' '.join([SUBCTL, 'export', 'service', '-n', namespace, name])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)
        time.sleep(0.5)

        return ok, stdout, stderr

    @staticmethod
    def export_service_nowait(namespace, name):
        """
        export service
        :param namespace: (str) service namespace
        :param name: (str) service name
        :return:
        (bool) True - success, False - fail
        (str) stdout
        (str) stderr
        """
        is_exported = NetworkStatusRepository().is_service_exported(namespace, name)
        if is_exported:
            return True, None, None

        if not ResourceRepository().is_service_deployed(namespace, name):
            return False, None, 'Not found service(ns={}, service={})'.format(namespace, name)

        cmdline = ' '.join([SUBCTL, 'export', 'service', '-n', namespace, name])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        return ok, stdout, stderr

    @staticmethod
    def unexport_service(namespace, name):
        """
        unexport service
        :param namespace: (str) service namespace
        :param name: (str) service name
        :return:
        """
        if not NetworkStatusRepository().is_service_exported(namespace, name):  # already unexported service
            return True, None, None

        cmdline = ' '.join([SUBCTL, 'unexport', 'service', '-n', namespace, name])

        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)
        time.sleep(0.5)

        return ok, stdout, stderr
