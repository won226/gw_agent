import json
import yaml
import time
import os

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from repository.common.type import MultiClusterRole
from repository.cache.network import NetworkStatusRepository
from repository.cache.resources import ResourceRepository
from repository.model.k8s.service import Service
from utils.fileutils import FileUtil
from utils.run import RunCommand
from cluster.watcher.commands import CommandExecutor
from repository.common import nfs_server_client
from repository.common import k8s_client
from utils.validate import Validator
from typing import List
from gwlink_migration.common.type import MigrationError, MigrationOperation

KUBECTL = ' '.join(settings.CEDGE_BINS['kubectl'])
MANIFEST_PATH = settings.MANIFEST_DIRECTORY
TEMP_PATH = settings.TEMP_DIRECTORY
logger = settings.get_logger(__name__)


class KubeCommand:
    """
    kube-system resources checklist
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def execute_shell_nowait(cmdline):
        executor = CommandExecutor()
        executor.put_command(cmdline)

    @staticmethod
    def apply_manifest_file(manifest):
        """
        apply kubernetes manifest file
        :param manifest: (str) manifest file path
        :return:
        """
        if not os.path.isfile(manifest):
            return False, None, 'Not found {}'.format(manifest)

        cmdline = ' '.join([KUBECTL, 'apply', '-f', manifest])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_manifest_file(manifest):
        """
        delete kubernetes manifest file
        :param manifest: (str) manifest file path
        :return:
        """
        if not os.path.isfile(manifest):
            return False, 'Not found {} file'.format(manifest)

        cmdline = ' '.join([KUBECTL, 'delete', '-f', manifest])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def validate_manifest(manifest):
        """
        kubectl dry run to validate kubectl resource manifest(*.yaml)
        :param manifest: (str) manifest file path
        :return:
        """
        if manifest is None or type(manifest) != str:
            return False, None, 'Invalid value. You must input manifest as str'

        if not os.path.isfile(manifest):
            return False, None, 'Not found {}'.format(manifest)

        cmdline = ' '.join([KUBECTL, 'apply', '-f', manifest, '--dry-run=client'])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_namespace(namespace):
        """
        delete kubernetes namespace
        :param namespace: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'delete', 'namespace', namespace, '--force'])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_namespace_deployed(namespace: str):
        """
        check whether namespace deployed
        :param namespace: (str)
        :return:
        (bool) success
        (str) stdout
        (str) stderr
        """
        cmdline = ' '.join([KUBECTL, 'get', 'namespace', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_pod(namespace, pod):
        """
        delete kubernetes pod
        :param namespace: (str)
        :param pod: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'delete', 'pod', pod, '-n', namespace, '--force'])
        # cmdline = ' '.join([KUBECTL, 'delete', 'pod', pod, '-n', namespace])
        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_pod_deployed(namespace: str, pod: str):
        """
        check whether pod is deployed
        :param namespace: (str)
        :param pod: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'get', 'pod', pod, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_pod_running(namespace: str, pod: str):
        """
        check whether pod is running
        :param namespace:
        :param pod:
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'get', 'pod', pod,
                            '-n', namespace, '-o', 'json'])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        if not ok:
            return ok, stdout, stderr

        result = json.loads(stdout)
        if result is None:
            return False, '', ''
        if 'status' not in result:
            return False, '', ''
        if 'phase' not in result['status']:
            return False, '', ''

        phase = result['status']['phase']
        if phase == 'Running':
            return True, '', ''

    @staticmethod
    def delete_service(namespace, service):
        """
        delete kubernetes service
        :param namespace: (str)
        :param service: (str)
        :return:
        """
        # cmdline = ' '.join([KUBECTL, 'delete', 'service', service, '-n', namespace, '--force'])
        cmdline = ' '.join([KUBECTL, 'delete', 'service', service, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_service_deployed(namespace: str, service: str):
        """
        check whether service deployed
        :param namespace: (str)
        :param service: (str)
        :return:
        (bool) success
        (str) stdout
        (str) stderr
        """
        cmdline = ' '.join([KUBECTL, 'get', 'service', service, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_deployment(namespace, deployment):
        """
        delete kubernetes deployment
        :param namespace: (str)
        :param deployment: (str)
        :return:
        """
        # cmdline = ' '.join([KUBECTL, 'delete', 'deployment', deployment, '-n', namespace, '--force'])
        cmdline = ' '.join([KUBECTL, 'delete', 'deployment', deployment, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_deployment_deployed(namespace: str, deployment: str):
        """
        check whether deployment deployed
        :param namespace: (str)
        :param deployment: (str)
        :return:
        (bool) success
        (str) stdout
        (str) stderr
        """
        cmdline = ' '.join([KUBECTL, 'get', 'deployment', deployment, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_all_deployment_replicas_ready(namespace: str, deployment: str):
        """
        check whether all deployment replicas are ready
        :param namespace: (str)
        :param deployment: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'get', 'deployment', deployment, '-n', namespace, '-o', 'json'])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)
        if not ok:
            return ok, stdout, stderr

        result = json.loads(stdout)
        if result is None:
            return False, '', ''
        if 'status' not in result:
            return False, '', ''
        if 'readyReplicas' not in result['status']:
            return False, '', ''
        if 'replicas' not in result['status']:
            return False, '', ''

        ready = result['status']['readyReplicas']
        desired = result['status']['replicas']

        if ready == desired:
            return True, '', ''

        return False, '', 'All pod are not ready'

    @staticmethod
    def adjust_scale_deployment(namespace, deployment, replicas):
        """
        adjust replicas for deployment
        :param namespace: (str)
        :param deployment: (str)
        :param replicas: (int)
        :return:
        """
        if type(replicas) != int or replicas < 0:
            return False, None, 'Invalid replicas({})'.format(replicas)

        cmdline = ' '.join([KUBECTL, 'scale', 'deployment', deployment,
                            '--replicas', str(replicas),
                            '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_daemonset_deployed(namespace: str, daemonset: str) -> (bool, str, str):
        """
        check whether daemonset deployed
        :param namespace: (str)
        :param daemonset: (str)
        :return:
        (bool) success
        (str) stdout
        (str) stderr
        """
        cmdline = ' '.join([KUBECTL, 'get', 'daemonset', daemonset, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_all_daemonset_replicas_ready(namespace: str, daemonset: str):
        """
        check whether all daemonset replicas are ready
        :param namespace: (str)
        :param daemonset: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'get', 'daemonset', daemonset, '-n', namespace, '-o', 'json'])
        # '--no-headers',
        # '-o', 'custom-columns=":status.numberReady,:status.desiredNumberScheduled""'])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)
        if not ok:
            return ok, stdout, stderr

        result = json.loads(stdout)
        if result is None:
            return False, '', ''
        if 'status' not in result:
            return False, '', ''
        if 'numberReady' not in result['status']:
            return False, '', ''
        if 'desiredNumberScheduled' not in result['status']:
            return False, '', ''

        numberReady = result['status']['numberReady']
        desiredNumberScheduled = result['status']['desiredNumberScheduled']

        if numberReady == desiredNumberScheduled:
            return True, '', ''

        return False, '', 'All pod are not ready'

    @staticmethod
    def restart_daemonset(namespace, daemonset):
        """
        restart kubernetes daemonset
        :param namespace: (str)
        :param daemonset: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'rollout', 'restart', 'daemonset', daemonset, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_daemonset(namespace, daemonset):
        """
        delete kubernetes daemonset
        :param namespace: (str)
        :param daemonset: (str)
        :return:
        """
        # cmdline = ' '.join([KUBECTL, 'delete', 'daemonset', daemonset, '-n', namespace, '--force'])
        cmdline = ' '.join([KUBECTL, 'delete', 'daemonset', daemonset, '-n', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_namespace_nowait(name):
        """
        delete namespace nowait
        :param name: (str) namespace name
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'delete', 'namespace', name, '--ignore-not-found'])
        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_crd(group, plural):
        """
        delete custom resource definition
        :param group: (str)
        :param plural: (str)
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'delete', 'crd', '.'.join([plural, group]), '--ignore-not-found'])

        return RunCommand.execute_shell_wait(cmdline)
        # path = '/metadata/finalizers'
        # return KubeCommand.delete_finalizer(None, 'crd', path, '.'.join([plural, group]))

    @staticmethod
    def delete_path(namespace, kind, path, name):
        """
        delete path in resource
        :param namespace: (str)
        :param kind: (str)
        :param path: (str) json path in resource
        :param name: (str)
        :return:
        """
        allow_kinds = ['service', 'pod', 'daemonset', 'deployment', 'crd', 'apiservice', 'namespace']

        if kind not in allow_kinds:
            return False, None, 'kind({}) is not in {}'.format(kind, allow_kinds)

        if not Validator.is_str(name):
            return False, None, 'Invalid name({})'.format(name)

        patch_format = '--patch="[{"op": "remove", "path": "{path}"}]"'
        patch = patch_format.replace('{path}', path)

        cmdline = ' '.join([KUBECTL, 'patch', kind, name, '--type', 'json', patch])

        if namespace is not None:
            cmdline = ' '.join([cmdline, '-n', namespace])

        return RunCommand.execute_bash_wait(cmdline)

    @staticmethod
    def delete_finalizer(namespace, kind, path, name):
        """
        delete finalizer for resource
        :param namespace: (str) Nullable
        :param kind: (str) crd
        :param path: (str)
        :param name: (str)
        :return:
        """
        allow_kinds = ['service', 'pod', 'daemonset', 'deployment', 'crd', 'apiservice', 'namespace']

        if kind not in allow_kinds:
            return False, None, 'kind({}) is not in {}'.format(kind, allow_kinds)

        if not Validator.is_str(name):
            return False, None, 'Invalid name({})'.format(name)

        patch_format = '--patch="[{"op": "remove", "path": "{path}"}]"'
        patch = patch_format.replace('{path}', path)

        cmdline = ' '.join([KUBECTL, 'patch', kind, name, '--type', 'json', patch])

        if namespace is not None:
            cmdline = ' '.join([cmdline, '-n', namespace])

        return RunCommand.execute_bash_wait(cmdline)

    """    
    prometheus and node, k8s exporters 
    - deployment order
        1) apply_prometheus()
        2) apply_node_exporter()
        3) apply_k8s_state_metric()
    - deletion order
        1) delete_prometheus()
        2) delete_node_exporter()
        3) delete_k8s_state_metric()
    """

    @staticmethod
    def apply_prometheus():
        """
        deploy prometheus resources
        :return:
            (bool) True - success, False - failure
            (str) error message
        """
        if ResourceRepository().is_service_deployed(settings.PROM_NAMESPACE, settings.PROM_SERVICE):
            if ResourceRepository().is_deployment_deployed(settings.PROM_NAMESPACE, settings.PROM_DEPLOYMENT):
                return True, None, None

        filename = os.path.join(MANIFEST_PATH, 'prometheus', 'prometheus.yaml')

        return KubeCommand.apply_manifest_file(filename)

    @staticmethod
    def delete_prometheus():
        """
        delete prometheus resources
        :return:
            (bool) True - success, False - failure
            (str) error message
        """
        filename = os.path.join(MANIFEST_PATH, 'prometheus', 'prometheus.yaml')

        return KubeCommand.delete_manifest_file(filename)

    @staticmethod
    def apply_node_exporter():
        """
        deploy node-exporter resources
        :return:
            (bool) True - success, False - failure
            (str) error message
        """
        if ResourceRepository().is_service_deployed(settings.NODE_EXPORTER_NAMESPACE,
                                                    settings.NODE_EXPORTER_SERVICE):
            if ResourceRepository().is_deployment_deployed(settings.NODE_EXPORTER_NAMESPACE,
                                                           settings.NODE_EXPORTER_DAEMONSET):
                return True, None, None

        filename = os.path.join(MANIFEST_PATH, 'prometheus', 'node-exporter.yaml')

        return KubeCommand.apply_manifest_file(filename)

    @staticmethod
    def delete_node_exporter():
        """
        delete node-exporter resources
        :return:
            (bool) True - success, False - failure
            (str) error message
        """
        filename = os.path.join(MANIFEST_PATH, 'prometheus', 'node-exporter.yaml')

        return KubeCommand.delete_manifest_file(filename)

    @staticmethod
    def apply_k8s_state_metric():
        """
        deploy kubernetes-state-metric-exporter resources
        :return:
            (bool) True - success, False - failure
            (str) error message
        """
        filename = os.path.join(MANIFEST_PATH, 'prometheus', 'k8s-state-metric.yaml')

        if ResourceRepository().is_service_deployed(settings.K8S_STATE_METRIC_NAMESPACE,
                                                    settings.K8S_STATE_METRIC_SERVICE):
            if ResourceRepository().is_deployment_deployed(settings.K8S_STATE_METRIC_NAMESPACE,
                                                           settings.K8S_STATE_METRIC_DEPLOYMENT):
                return True, None, None

        return KubeCommand.apply_manifest_file(filename)

    @staticmethod
    def apply_gedge_namespace():
        """
        deploy gedge namespace
        :return:
            (bool) True - success, False - failure
            (str) stdout
            (str) stderr: error message
        """
        filename = os.path.join(MANIFEST_PATH, 'namespace', 'gedge.yaml')

        return KubeCommand.apply_manifest_file(filename)

    @staticmethod
    def delete_k8s_state_metric():
        """
        delete kubernetes-state-metric-exporter resources
        :return:
            (bool) True - success, False - failure
            (str) error message
        """
        filename = os.path.join(MANIFEST_PATH, 'prometheus', 'k8s-state-metric.yaml')

        return KubeCommand.delete_manifest_file(filename)

    @staticmethod
    def check_kubernetes():
        """
        check whether kubectl is exist or not
        :return: (bool) exist - True, otherwise - False
        """
        # todo: modify to return condition(checklist)
        if not os.path.isfile(KUBECTL):
            return False

        return True

    @staticmethod
    def get_custom_resource_definitions():
        """
        get all custom resource definitions
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'get', 'crds', '-o', 'json'])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        if not ok:
            return None

        result = json.loads(stdout)
        if 'items' not in result:
            return None

        return result['items']

    @staticmethod
    def delete_cluster_role(cluster_role):
        """
        delete cluster role
        :param cluster_role: (str) cluster role name
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'delete', 'clusterrole', cluster_role])
        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def delete_role(namespace, role):
        """
        delete role
        :param namespace: (str) namespace
        :param role: (str) role name
        :return:
        """
        cmdline = ' '.join([KUBECTL, 'delete', 'role', '-n', namespace, role])
        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def is_master_schedulable():
        """
        check whether schedule pods to master node
        :return: (bool) True - enable, False - disable
        """
        nodes = ResourceRepository().get_nodes()
        master_node = None

        for node in nodes:
            if node.get_role() == 'Master':
                master_node = node
                break

        if master_node is None:
            logger.warning('Not found master node')
            return False

        taints = master_node.get_taints()
        if 'node-role.kubernetes.io/master:NoSchedule' in taints:
            return False

        return True

    @staticmethod
    def get_master_name():
        """
        get master node's name
        :return:
        """
        nodes = ResourceRepository().get_nodes()
        master_node = None

        for node in nodes:
            if node.get_role() == 'Master':
                master_node = node
                break

        if master_node is None:
            logger.warning('Not found master node')
            return None

        return master_node.get_name()

    @staticmethod
    def enable_master_schedulable():
        """
        enable schedulable for master node
        :return:
        """
        if KubeCommand.is_master_schedulable():  # already set to schedulable
            return True, None, None

        master_node = KubeCommand.get_master_name()

        if master_node is None:
            return False, None, 'Not found master node'

        cmdline = ' '.join([KUBECTL, 'taint',
                            'nodes', master_node,
                            'node-role.kubernetes.io/master-'])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def disable_master_schedulable() -> (bool, str, str):
        """
        disable schedulable for master node
        :return:
        """
        if not KubeCommand.is_master_schedulable():  # already set to NoSchedule
            return

        master_node = KubeCommand.get_master_name()
        if master_node is None:
            return False, None, 'Not found master node'

        cmdline = ' '.join([KUBECTL, 'taint',
                            'nodes', master_node,
                            'node-role.kubernetes.io/master:NoSchedule'])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def set_node_label(node, label):
        """
        set label to node
        :param node: (str) node name
        :param label: (str) label
        :return:
        """
        if node is None or len(node) <= 0 or type(node) != str:
            return False, None, 'Invalid node name({})'.format(node)
        if label is None or len(label) <= 0 or type(label) != str:
            return False, None, 'Invalid label({})'.format(label)

        cmdline = ' '.join([KUBECTL, 'label', 'node', node, label, '--overwrite'])
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        if not ok:
            return False, None, 'Fail to set label to node({}) caused by {}'.format(node, stderr)

        return True, None, None

    @staticmethod
    def deploy_namespace(namespace: str):
        """
        deploy namespace
        :param namespace: (str) namespace
        :return:
        """
        if not namespace:
            return False, None, "Invalid namespace, namespace=" + namespace

        cmdline = ' '.join([KUBECTL, 'create', 'ns', namespace])

        return RunCommand.execute_shell_wait(cmdline)

    @staticmethod
    def deploy_gedge_namespace():
        """
        check whether namespace is deployed
        :return:
        """
        if not ResourceRepository().is_namespace_deployed('gedge'):
            return KubeCommand.apply_gedge_namespace()

        return True, None, None

    @staticmethod
    def is_nfs_server_deployed():
        """
        check whether nfs server deployed or not
        :return: (bool) True - deployed, False - not deployed
        """
        cluster_id = ResourceRepository().get_cluster_id()
        service = 'nfs-server-' + cluster_id
        deployment = 'nfs-server-' + cluster_id

        if ResourceRepository().is_service_deployed('gedge', service):
            if ResourceRepository().is_all_deployment_replicas_ready('gedge', deployment):
                return True

        return False

    @staticmethod
    def apply_nfs_server():
        """
        apply nfs server
        :return:
        ok: (bool) True - success, False - fail
        stdout: (str) stdout message
        stderr: (str) error message
        """
        if KubeCommand().is_nfs_server_deployed():
            return True, None, None

        master_node_name = KubeCommand().get_master_name()
        cluster_id = ResourceRepository().get_cluster_id()

        filename = os.path.join(MANIFEST_PATH, 'nfs', 'template-nfs-server.yaml')
        manifest = FileUtil.read_text_file(filename)
        manifest = manifest.format(cluster_id=cluster_id, node_name=master_node_name)

        # save local nfs-client manifest with cluster_id and nfs-server address
        save_file = os.path.join(MANIFEST_PATH, 'nfs', 'nfs-server-{}.yaml'.format(cluster_id))
        FileUtil.write_text_file(save_file, manifest)

        ok, stdout, stderr = KubeCommand.apply_manifest_file(save_file)
        if not ok:
            return ok, stdout, stderr

        # wait until nfs-server is startup
        time.sleep(settings.NFS_SERVER_STARTUP_TIMEOUT)

        return ok, stdout, stderr

    @staticmethod
    def delete_nfs_server():
        """
        delete nfs server
        :return:
        ok: (bool) True - success, False - fail
        stdout: (str) stdout message
        stderr: (str) error message
        """
        if not KubeCommand.is_nfs_server_deployed():
            return True, None, None

        cluster_id = ResourceRepository().get_cluster_id()
        filename = os.path.join(MANIFEST_PATH, 'nfs', 'nfs-server-{}.yaml'.format(cluster_id))

        if not os.path.isfile(filename):
            return False, None, 'Not found {} file'.format(filename)

        nfs_server_client.Connector().set_endpoint_none(MultiClusterRole.LOCAL.value)

        return KubeCommand.delete_manifest_file(filename)

    @staticmethod
    def is_nfs_client_deployed(cluster_id):
        """
        check whether local nfs-client is deployed or not
        :param cluster_id: (str) multi-cluster id
        :return: (bool) True - deployed, False - not deployed
        """
        name = 'nfs-client-{}'.format(cluster_id)

        if ResourceRepository().is_all_daemonset_replicas_ready('gedge', name):
            return True

        return False

    @staticmethod
    def apply_nfs_client(role):
        """
        apply nfs-client manifest
        :param role: MultiClusterRole(Enum) value; 'Local' or 'Remote'
        :return:
        ok: (bool) True - success, False - fail
        stdout: (str) stdout message
        stderr: (str) error message
        """
        if not MultiClusterRole.validate(role):
            return False, None, 'Invalid role({}). Must input "Local" or "Remote"'.format(role)

        if role == MultiClusterRole.LOCAL.value:
            cluster_id = ResourceRepository().get_cluster_id()
            nfs_server_domain = settings.LOCAL_NFS_SERVER_DOMAIN.format(cluster_id=cluster_id)
        else:
            cluster_id = NetworkStatusRepository().get_remote_mc_network_name()
            nfs_server_domain = settings.REMOTE_NFS_SERVER_DOMAIN.format(cluster_id=cluster_id)

        if not cluster_id:
            return False, None, 'Not found cluster name'

        if KubeCommand.is_nfs_client_deployed(cluster_id):
            return True, None, None

        # check cluster migration directory from nfs-client
        # when cluster migration directory is not exist, request nfs-server to create volume
        try:
            ok, stdout, stderr = nfs_server_client.Connector().publish_volume(role, cluster_id)
        except SystemError as exc:
            ok = False
            stdout = None
            error_message = get_exception_traceback(exc)
            stderr = 'Fail to request nfs-server, caused by ' + error_message

        if not ok:
            return ok, stdout, stderr

        # set nfs-client manifest
        filename = os.path.join(MANIFEST_PATH, 'nfs', 'template-nfs-client.yaml')
        manifest = FileUtil.read_text_file(filename)
        manifest = manifest.format(cluster_id=cluster_id,
                                   nfs_server_domain=nfs_server_domain)

        # save local nfs-client manifest with cluster_id and nfs-server address
        save_file = os.path.join(MANIFEST_PATH, 'nfs', 'nfs-client-{}.yaml'.format(cluster_id))
        FileUtil.write_text_file(save_file, manifest)

        # apply local nfs-client manifest
        ok, stdout, stderr = KubeCommand.apply_manifest_file(save_file)
        FileUtil.delete_file(save_file)

        if not ok:
            return ok, stdout, stderr

        return ok, stdout, stderr

    @staticmethod
    def umount_nfs_client(cluster_id):
        """
        umount nfs-client volume
        :param cluster_id: (str) multi-cluster cluster id
        :return:
        ok: (bool) True - success, False - fail
        stdout: (str) stdout message
        stderr: (str) error message
        """
        if cluster_id is None or type(cluster_id) != str:
            return False, None, 'Invalid value for cluster_id({}). Must input not None, str type'.format(cluster_id)

        nodes = ResourceRepository().get_nodes()
        for node in nodes:
            name = node.get_name()
            KubeCommand.delete_pod('gedge', 'nsenter-' + name)
            filepath = os.path.join(MANIFEST_PATH, 'nfs', 'template-nsenter-umount.yaml')
            manifest = FileUtil.read_text_file(filepath)
            manifest = manifest.format(node=name, volume=cluster_id)
            filepath = os.path.join(MANIFEST_PATH, 'nfs', 'template-nsenter-umount-{}.yaml'.format(name))
            FileUtil.write_text_file(filepath, manifest)
            ok, stdout, stderr = KubeCommand.apply_manifest_file(filepath)
            if not ok:
                return ok, stdout, stderr

        return True, None, None

    @staticmethod
    def delete_nfs_client_by_cluster_id(cluster_id):
        """
        delete nfs-client
        :param cluster_id: (str) cluster_id
        :return:
        """
        if cluster_id is None:
            return False, None, 'cluster_id is None'

        if not KubeCommand.is_nfs_client_deployed(cluster_id):
            return True, None, None

        # set nfs-client manifest
        ok, stdout, stderr = KubeCommand().delete_daemonset('gedge', 'nfs-client-' + cluster_id)

        nfs_server_client.Connector().set_endpoint_none(MultiClusterRole.REMOTE.value)

        return ok, stdout, stderr

    @staticmethod
    def delete_nfs_client(role):
        """
        delete nfs client for local cluster
        :param role: (str) 'Local' or 'Remote'
        :return:
        ok: (bool) True - success, False - fail
        stdout: (str) stdout message
        stderr: (str) error message
        """
        if not MultiClusterRole.validate(role):
            return False, None, 'Invalid role({}). Must input \'Local\' or \'Remote\''.format(role)

        if role == MultiClusterRole.LOCAL.value:
            cluster_id = ResourceRepository().get_cluster_id()
            if not cluster_id:
                return False, None, 'Not found \'Local\' cluster_id'

            nfs_server_domain = settings.LOCAL_NFS_SERVER_DOMAIN.format(cluster_id=cluster_id)

        else:
            cluster_id = NetworkStatusRepository().get_remote_mc_network_name()
            if not cluster_id:
                return False, None, 'Not found \'Remote\' cluster_id'

            nfs_server_domain = settings.REMOTE_NFS_SERVER_DOMAIN.format(cluster_id=cluster_id)

        ok, stdout, stderr = KubeCommand.umount_nfs_client(cluster_id)
        if not ok:
            return ok, stdout, stderr

        if not KubeCommand.is_nfs_client_deployed(cluster_id):
            return True, None, None

        # set nfs-client manifest
        filename = os.path.join(MANIFEST_PATH, 'nfs', 'template-nfs-client.yaml')
        manifest = FileUtil.read_text_file(filename)
        manifest = manifest.format(cluster_id=cluster_id,
                                   nfs_server_domain=nfs_server_domain)

        # save local nfs-client manifest with cluster_id and nfs-server address
        save_file = os.path.join(MANIFEST_PATH, 'nfs', 'nfs-client-{}.yaml'.format(cluster_id))
        FileUtil.write_text_file(save_file, manifest)

        # apply local nfs-client manifest
        ok, stdout, stderr = KubeCommand.delete_manifest_file(save_file)
        FileUtil.delete_file(save_file)

        nfs_server_client.Connector().set_endpoint_none('remote')

        return ok, stdout, stderr

    def delete_resources(self, resources):
        """
        delete resources
        :param resources: (list(dict)) see 'static/checklist.json' file
        :return:
        """
        if type(resources) is not list:
            return False, '', 'Invalid resources type({})'.format(type(resources))

        if len(resources) == 0:
            return True, '', ''

        for resource in resources:
            if 'kind' not in resource:
                return False, '', 'Not found \'kind\' in resource object'

            if 'name' not in resource:
                return False, '', 'Not found \'name\' in resource object'

            if 'namespace' not in resource:
                continue

            kind = resource['kind']
            namespace = resource['namespace']
            name = resource['name']

            if kind == 'service':
                self.delete_service(namespace=namespace, service=name)
                continue
            if kind == 'daemonset':
                self.delete_daemonset(namespace=namespace, daemonset=name)
                continue
            if kind == 'deployment':
                self.delete_deployment(namespace=namespace, deployment=name)
                continue
            if kind == 'pod':
                self.delete_pod(namespace=namespace, pod=name)
                continue

        for resource in resources:
            kind = resource['kind']
            name = resource['name']

            if kind == 'namespace':
                self.delete_namespace(namespace=name)

        return True, '', ''

    @staticmethod
    def get_namespaced_prefix_named_pod(pod_name_prefix, namespace: str) -> (bool, List[str], str):
        """
        get namespaced and prefix named pod
        :param pod_name_prefix: (str) pod name prefix
        :param namespace: (str) namespace
        :return:
        (bool) True - success, False - fail
        (str) List[str]; matched pod name list
        (str) error message
        """
        api_client = k8s_client.Connector().core_v1_api()
        found_pods = []

        try:
            result = api_client.list_namespaced_pod(namespace=namespace,
                                                    _request_timeout=settings.KUBE_API_REQUEST_TIMEOUT)
        except Exception as exc:
            logger.error('Pod Not found, caused by ' + get_exception_traceback(exc))
            return False, None, MigrationError.POD_NOT_FOUND.value

        if not result or not hasattr(result, "items"):
            return False, found_pods, 'Not found pod'

        for item in result.items:
            if pod_name_prefix in item.metadata.name:
                found_pods.append(item.metadata.name)

        if not found_pods:
            return False, found_pods, 'Not found pod'
        return True, found_pods, None

    @staticmethod
    def get_namespaced_pod_yaml(pod: str, namespace: str) -> (bool, str, str):
        """
        get namespaced pod with yaml format
        :param pod: (str) pod name
        :param namespace: (str) namespace
        :return:
        (bool) True - success, False - fail
        (str) yaml formatted namespace pod
        (str) error message
        """
        api_client = k8s_client.Connector().core_v1_api()

        try:
            pod_resource = api_client.read_namespaced_pod(name=pod,
                                                          namespace=namespace,
                                                          _request_timeout=settings.KUBE_API_REQUEST_TIMEOUT)
        except Exception as exc:
            logger.error('Pod Not found, caused by ' + get_exception_traceback(exc))
            return False, None, MigrationError.POD_NOT_FOUND.value

        containers_json = []

        for container in pod_resource.spec.containers:
            # refer to https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Container.md

            ports_json = []
            if container.ports:
                for port in container.ports:
                    port_json = {}
                    if port.name:
                        port_json['name'] = port.name
                    if port.container_port:
                        port_json['container_port'] = port.container_port
                    if port.host_ip:
                        port_json['host_ip'] = port.host_ip
                    if port.host_port:
                        port_json['host_port'] = port.host_port
                    if port.protocol:
                        port_json['protocol'] = port.protocol
                    ports_json.append(port_json)

            envs_json = []
            if container.env:
                env_json = {}
                for e in container.env:
                    if e.name:
                        env_json['name'] = e.name
                    if e.value:
                        env_json['value'] = e.value
                    if e.value_from:
                        env_json['value_from'] = e.value_from
                    envs_json.append(env_json)

            env_froms_json = []
            if container.env_from:
                env_from_json = {}
                for e in container.env_from:
                    if e.name:
                        env_from_json['name'] = e.name
                    if e.value:
                        env_from_json['value'] = e.value
                    if e.value_from:
                        env_from_json['value_from'] = e.value_from
                    env_froms_json.append(env_from_json)

            container_json = {}

            if container.name:
                container_json['name'] = container.name
            if container.image:
                container_json['image'] = container.image
            if container.image_pull_policy:
                container_json['image_pull_policy'] = container.image_pull_policy
            if ports_json:
                container_json['port'] = ports_json
            if envs_json:
                container_json['env'] = envs_json
            if env_froms_json:
                container_json['env_from'] = env_froms_json
            if container.args:
                container_json['args'] = container.args
            if container.command:
                container_json['command'] = container.command

            containers_json.append(container_json)

        pod_resource_json = {'apiVersion': pod_resource.api_version,
                             'kind': pod_resource.kind,
                             'metadata': {},
                             'spec': {}}

        if pod_resource.metadata.name:
            pod_resource_json['metadata']['name'] = pod_resource.metadata.name
        if pod_resource.metadata.labels:
            pod_resource_json['metadata']['labels'] = pod_resource.metadata.labels
        if pod_resource.metadata.namespace:
            pod_resource_json['metadata']['namespace'] = pod_resource.metadata.namespace
        if pod_resource.spec.node_selector:
            pod_resource_json['spec']['node_selector'] = pod_resource.spec.node_selector
        if containers_json:
            pod_resource_json['spec']['containers'] = containers_json

        # print(pod_resource_json)
        pod_resource_yaml = yaml.dump(pod_resource_json)
        # print(pod_resource_yaml)

        return True, pod_resource_yaml, None

    @staticmethod
    def get_services_yaml(services: List[Service]) -> str:
        """
        get services yaml manifest stream
        :param services: (List[Service])
        :return:
        (bool) True - success, False - fail
        (str) service resource yaml
        (str) error message
        """
        service_resource_jsons = []

        for service in services:
            service_resource_json = {'apiVersion': 'v1',
                                     'kind': 'Service',
                                     'metadata': {},
                                     'spec': {}}
            # spec.ports
            ports_json = []
            for port in service.ports:
                port_json = {}
                if port.name:
                    port_json['name'] = port.name
                if port.protocol:
                    port_json['protocol'] = port.protocol
                if port.target_port:
                    port_json['targetPort'] = int(port.target_port)
                if port.port:
                    port_json['port'] = int(port.port)
                if port.node_port:
                    port_json['nodePort'] = int(port.node_port)
                ports_json.append(port_json)

            # spec.selector
            selector_json = {}
            for selector in service.selector:
                items = selector.split('=')
                if items[0]:
                    selector_json[items[0]] = None
                    if items[1]:
                        selector_json[items[0]] = items[1]

            service_resource_json['metadata']['name'] = service.name
            service_resource_json['metadata']['namespace'] = service.namespace

            if service.service_type:
                service_resource_json['spec']['type'] = service.service_type

            service_resource_json['spec']['selector'] = selector_json
            service_resource_json['spec']['ports'] = ports_json

            service_resource_jsons.append(service_resource_json)

        # print(service_resource_jsons)
        services_resource_yaml = yaml.dump_all(service_resource_jsons)
        # print(services_resource_yaml)

        return True, services_resource_yaml, None

    @staticmethod
    def get_namespace_pod_container_name_list(pod: str, namespace: str) -> (bool, List[str], str):
        """
        get container name list for namespaced pod'
        :param pod: (str) pod name
        :param namespace: (str) namespace
        :return:
        (bool) True - success, False - fail
        (str) yaml formatted namespace pod
        (str) error message
        """
        api_client = k8s_client.Connector().core_v1_api()

        try:
            pod_resource = api_client.read_namespaced_pod(name=pod,
                                                          namespace=namespace,
                                                          _request_timeout=settings.KUBE_API_REQUEST_TIMEOUT)
        except Exception as exc:
            logger.error('Pod Not found, caused by ' + get_exception_traceback(exc))
            return False, None, MigrationError.POD_NOT_FOUND.value

        container_name_list = []
        for container in pod_resource.spec.containers:
            if container.name:
                container_name_list.append(container.name)

        return True, container_name_list, None

    @staticmethod
    def validate_livmigration_cro(migration_id: str,
                                  operation: str,
                                  source_namespace: str,
                                  source_pod: str,
                                  snapshot_path: str,
                                  target_node: str = None) -> (bool, str):
        """
        validate live migration custom resource object
        :param migration_id: (str) migration ID
        :param operation: (str) operation
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :param snapshot_path: (str) snapshot path
        :param target_node: (str) target node
        :return:
        (bool) True - success, False - fail
        (str) error message
        """
        api_client = k8s_client.Connector().custom_objects_api()

        """
        - API group: gedgemig.gedge.etri.kr
        - API version: v1
        - name: livmigration
        - plural: livmigrations
        """
        try:
            result = api_client.list_cluster_custom_object(
                group='gedgemig.gedge.etri.kr',
                plural='livmigrations',
                version='v1',
                _request_timeout=settings.KUBE_API_REQUEST_TIMEOUT)
        except Exception as exc:
            logger.error('Migration CRO not found, caused by ' + get_exception_traceback(exc))
            return False, MigrationError.LIVMIGRATION_CRD_NOT_FOUND.value

        if not 'items' in result:
            return False, MigrationError.LIVMIGRATION_CRD_NOT_FOUND.value

        if operation == MigrationOperation.CHECKPOINT.value:
            cro_name = 'checkpoint-{}'.format(migration_id)
        elif operation == MigrationOperation.RESTORE.value:
            cro_name = 'restore-{}'.format(migration_id)
        else:
            return False, MigrationError.INVALID_LIVMIGRATION_OPERATION.value

        for item in result['items']:
            if item['spec']['operation'] != operation:
                continue
            if item['metadata']['name'] == cro_name:
                if item['metadata']['namespace'] == source_namespace:
                    if not 'sourcePod' in item['spec']:
                        continue
                    if not 'snapshotPath' in item['spec']:
                        continue
                    if item['spec']['sourcePod'] == source_pod and item['spec']['snapshotPath'] == snapshot_path:
                        if operation == MigrationOperation.RESTORE.value:
                            if 'destaddr' in item['spec']:
                                if item['spec']['destaddr'] == target_node:
                                    return True, None
                        else:
                            return True, None

        return False, MigrationError.LIVMIGRATION_CRD_NOT_FOUND.value
