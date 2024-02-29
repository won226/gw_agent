import os
import time
import yaml

from cluster.command.localhost import LocalHostCommand
from cluster.command.submariner import SubmarinerCommand
from gw_agent.common.error import get_exception_traceback
from cluster.command.kubernetes import KubeCommand
from cluster.data_access_object import ClusterDAO
from gwlink_migration.common.type import MigrationError, MigrationOperation
from mqtt.model.content import Content
from repository.cache.resources import ResourceRepository
from repository.common.type import MultiClusterRole, MultiClusterConfigState
from restclient.api import RestClient
from repository.cache.components import ComponentRepository
from gw_agent import settings
from utils.fileutils import FileUtil

logger = settings.get_logger(__name__)
temp_dir_path = settings.TEMP_DIRECTORY

def error_response(cluster_id:str, request_id: str, error:str):
    """
    error response
    :param cluster_id: (str) cluster id
    :param request_id:  (str) request id
    :param error: (str) error text
    :return:
    """
    ok, err = RestClient.push_response(cluster_id=cluster_id,
                                       request_id=request_id,
                                       success=False,
                                       error=error,
                                       result=None)
    if not ok:
        logger.error(err)

def success_response(cluster_id: str, request_id: str, result: str):
    """
    success response
    :param cluster_id: (str) cluster id
    :param request_id: (str) request id
    :param result: (str) result
    :return:
    """
    ok, err = RestClient.push_response(cluster_id=cluster_id,
                                       request_id=request_id,
                                       success=True,
                                       error=None,
                                       result=result)
    if not ok:
        logger.error(err)

class K8sResourceService:
    @staticmethod
    def delete_namespace(cluster_id: str,
                         request_id: str,
                         namespace: str):
        """
        delete namespace
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param namespace: (str) namespace
        :return:
        """
        # run delete namespace
        ok, stdout, stderr = KubeCommand().delete_namespace(namespace)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def delete_pod(cluster_id: str,
                   request_id: str,
                   namespace: str,
                   pod: str):
        """
        delete pod
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param namespace: (str) namespace
        :param pod: (str) pod name
        :return:
        """
        # run delete pod
        ok, stdout, stderr = KubeCommand().delete_pod(namespace, pod)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def delete_service(cluster_id: str,
                       request_id: str,
                       namespace: str,
                       service: str):
        """
        delete service
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param namespace: (str) namespace
        :param service: (str) service name
        :return:
        """
        # run delete service
        ok, stdout, stderr = KubeCommand().delete_service(namespace, service)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def delete_deployment(cluster_id: str,
                          request_id: str,
                          namespace: str,
                          deployment: str):
        """
        delete deployment
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param namespace: (str) namespace
        :param deployment: (str) deployment name
        :return:
        """
        # run delete deployment
        ok, stdout, stderr = KubeCommand().delete_deployment(namespace, deployment)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def delete_daemonset(cluster_id: str,
                         request_id: str,
                         namespace: str,
                         daemonset: str):
        """
        delete daemonset
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param namespace: (str) namespace
        :param daemonset: (str) daemonset name
        :return:
        """
        # run delete daemonset
        ok, stdout, stderr = KubeCommand().delete_daemonset(namespace, daemonset)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def validate_resource_manifest(cluster_id: str,
                                   request_id: str,
                                   manifest: Content):
        """
        validate resource manifest file(yaml)
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param manifest: (mqtt.model.content.Content)
        :return:
        """

        try:
            manifest_file = manifest.get_content()[0]
            file_path = os.path.join(temp_dir_path, '{}.{}'.format(manifest_file.get_filename(),
                                                                   time.time()))
            manifest_file.save(file_path)
        except Exception as exc:
            error = get_exception_traceback(exc)
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        # run validate manifest file
        ok, stdout, stderr = KubeCommand().validate_manifest(file_path)
        FileUtil.delete_file(file_path)
        stderr = stderr.replace(file_path, manifest_file.get_filename())

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def apply_resource_manifest(cluster_id: str,
                                request_id: str,
                                manifest: Content):
        """
        apply resource manifest file(yaml)
        :param cluster_id: (str) cluster id
        :param request_id: (str) request id
        :param manifest: (mqtt.model.content.Content)
        :return:
        """
        try:
            manifest_file = manifest.get_content()[0]
            file_path = os.path.join(temp_dir_path, '{}.{}'.format(manifest_file.get_filename(), time.time()))
            manifest_file.save(file_path)
        except Exception as exc:
            error = get_exception_traceback(exc)
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        # run apply manifest file
        ok, stdout, stderr = KubeCommand().apply_manifest_file(file_path)
        FileUtil.delete_file(file_path)
        stderr = stderr.replace(file_path, manifest_file.get_filename())

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    @staticmethod
    def delete_resource_manifest(cluster_id: str,
                                 request_id: str,
                                 manifest: Content):
        """
        delete resource manifest file(yaml)
        :param cluster_id: (str) cluster id
        :param request_id:  (str) request id
        :param manifest: (mqtt.model.content.Content)
        :return:
        """
        manifest_file = manifest.get_content()[0]
        file_path = os.path.join(temp_dir_path, '{}.{}'.format(manifest_file.get_filename(), time.time()))
        manifest_file.save(file_path)

        # run delete manifest file
        ok, stdout, stderr = KubeCommand().delete_manifest_file(file_path)
        FileUtil.delete_file(file_path)
        stderr = stderr.replace(file_path, manifest_file.get_filename())

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)


class MultiClusterNetworkService:

    SYSTEM_INTERNAL_ERROR = 'SystemInternalError'
    CONNECTION_EXIST_ERROR = 'ConnectionExistError'
    CONNECTION_NOT_EXIST_ERROR = 'ConnectionNotExistError'
    REQUEST_EXIST_ERROR = 'RequestExistError'
    BROKER_NOT_READY_ERROR = 'BrokerNotReady'
    BAD_REQUEST = 'BadRequest'

    @staticmethod
    def connect_local_broker(cluster_id: str,
                             request_id: str,
                             connect_id: str,
                             remote_cluster_id: str):
        """
        connect local submariner broker
        :param: cluster_id: (str) cluster name
        :param: request_id: (str) request id issued from center
        :param: connect_id: (str) multi-cluster connect id issued from CEdge-center
        :param: remote_cluster_id: (str) remote cluster id connecting
        :return:
        """
        # get cluster table
        ok, cluster_dao, error_message = ClusterDAO.get_cluster()

        if not ok:
            logger.error('Failed in ClusterDAO.get_cluster(), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # get multi-cluster connect parameters in Cluster database
        cluster_name = cluster_dao.cluster_name
        mc_connect_id = cluster_dao.mc_connect_id

        # invalid cluster_name in Cluster database
        if not cluster_name:
            logger.error('Invalid cluster_name in Cluster database')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # invalid cluster_id requested from CEdge-center
        if cluster_name != cluster_id:
            logger.debug('Not found cluster_id. cluster_id=' + cluster_id)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.BAD_REQUEST)

        # if multi-cluster connection is already configured before,
        if mc_connect_id:
            logger.debug('Connection exist')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.CONNECTION_EXIST_ERROR)

        # get multi-cluster-config
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # if configuration is already exist in cluster
        mc_config_state = mc_config.mc_config_state

        if mc_config_state != MultiClusterConfigState.NONE.value:
            logger.debug('mc_config_state is not none')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.REQUEST_EXIST_ERROR)

        ok, error_message = \
            ClusterDAO.set_multi_cluster_config_request(
                multi_cluster_config_state=MultiClusterConfigState.CONNECT_REQUEST.value,
                mc_connect_id=connect_id,
                remote_cluster_name=remote_cluster_id,
                role=MultiClusterRole.LOCAL.value)

        if not ok:
            logger.error('Failed in ClusterDAO.set_multi_cluster_connection, caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result='')

    @staticmethod
    def connect_remote_broker(cluster_id: str,
                              request_id: str,
                              broker_info_content: str,
                              connect_id: str,
                              remote_cluster_id: str):
        """
        connect remote broker
        :param cluster_id: (str) cluster name
        :param request_id: (str) request id issued from center
        :param broker_info_content: (str) remote broker info file(broker-info.subm) content
        :param connect_id: (str) multi-cluster connect id issued from CEdge-center
        :param remote_cluster_id: (str) remote cluster id(name) connecting
        :return:
        """
        # get cluster table
        ok, cluster_dao, error_message = ClusterDAO.get_cluster()

        if not ok:
            logger.error('Failed in ClusterDAO.get_cluster(), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # get multi-cluster connect parameters in Cluster database
        cluster_name = cluster_dao.cluster_name
        mc_connect_id = cluster_dao.mc_connect_id

        # invalid cluster_name in Cluster database
        if not cluster_name:
            logger.error('Invalid cluster_name in Cluster database')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # invalid cluster_id requested from CEdge-center
        if cluster_name != cluster_id:
            logger.debug('Not found cluster_id. cluster_id=' + cluster_id)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.BAD_REQUEST)

        # if multi-cluster connection is already configured before,
        if mc_connect_id:
            logger.debug('Connection exist')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.CONNECTION_EXIST_ERROR)

        # get multi-cluster-config
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # if configuration is already exist in cluster
        mc_config_state = mc_config.mc_config_state

        if mc_config_state != MultiClusterConfigState.NONE.value:
            logger.debug('mc_config_state is not none')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.REQUEST_EXIST_ERROR)

        ok, error_message = \
            ClusterDAO.set_multi_cluster_config_request(
                multi_cluster_config_state=MultiClusterConfigState.CONNECT_REQUEST.value,
                mc_connect_id=connect_id,
                remote_cluster_name=remote_cluster_id,
                role=MultiClusterRole.REMOTE.value)

        if not ok:
            logger.error('Failed in ClusterDAO.set_multi_cluster_connection, caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # save remote broker-info.subm file
        broker_info_file = os.path.join(settings.REMOTE_BROKER_INFO, 'broker-info.subm')

        try:
            FileUtil.write_text_file(broker_info_file, broker_info_content)
        except Exception as exc:
            # fail to save broker-info.subm
            error_message = get_exception_traceback(exc)
            logger.error('Failed in FileUtil.write_text_file(), caused by ' + error_message)

            # rollback multi-cluster-config
            ok, error_message = ClusterDAO.reset_multi_cluster_config_request()
            if not ok:
                logger.error('Failed in ClusterDAO.reset_multi_cluster_config_request(), caused by ' + error_message)

            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result='')

    # deprecated
    @staticmethod
    def disconnect_broker(cluster_id: str,
                          request_id: str,
                          connect_id: str):
        """
        disconnect broker(LOCAL or REMOTE)
        :param cluster_id: (str) cluster name
        :param request_id: (str) request id
        :param connect_id: (str) multi-cluster connect id issued from CEdge-center
        :return:
        """
        # get cluster table
        ok, cluster_dao, error_message = ClusterDAO.get_cluster()

        if not ok:
            logger.error('Failed in ClusterDAO.get_cluster(), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # get multi-cluster connect parameters in Cluster database
        cluster_name = cluster_dao.cluster_name
        mc_connect_id = cluster_dao.mc_connect_id

        # invalid cluster_name in Cluster database
        if not cluster_name:
            logger.error('Invalid cluster_name in Cluster database')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # invalid cluster_id requested from CEdge-center
        if cluster_name != cluster_id:
            logger.debug('Not found cluster_id. cluster_id=' + cluster_id)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.BAD_REQUEST)

        # if multi-cluster connection is not exist,
        if not mc_connect_id:
            logger.debug('Connection not exist')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.CONNECTION_NOT_EXIST_ERROR)

        # if requested mc_connect_id is not same with cluster's one
        if mc_connect_id != connect_id:
            logger.debug('Invalid mc_connect_id is requested')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.BAD_REQUEST)

        # get multi-cluster-config
        ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

        if not ok:
            logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        # if configuration is already exist in cluster
        mc_config_state = mc_config.mc_config_state

        if mc_config_state != MultiClusterConfigState.NONE.value:
            logger.debug('mc_config_state is not none')
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.REQUEST_EXIST_ERROR)

        ok, error_message = \
            ClusterDAO.set_multi_cluster_config_request(
                multi_cluster_config_state=MultiClusterConfigState.DISCONNECT_REQUEST.value,
                mc_connect_id=connect_id,
                remote_cluster_name=None,
                role=MultiClusterRole.NONE.value)

        if not ok:
            logger.error('Failed in ClusterDAO.set_multi_cluster_connection, caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result='')

    @staticmethod
    def get_local_broker_info(cluster_id: str,
                              request_id: str):
        """
        get local broker info
        :param cluster_id: (str) cluster name
        :param request_id: (str) request id
        :return:
        """
        # check submariner_state
        if not ComponentRepository().is_submariner_broker_ready():
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.BROKER_NOT_READY_ERROR)

        # check whether local broker info file is exist
        broker_info_file = os.path.join(settings.LOCAL_BROKER_INFO, 'broker-info.subm')
        if not os.path.isfile(broker_info_file):
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.BROKER_NOT_READY_ERROR)

        try:
            broker_info_content = FileUtil.read_text_file(broker_info_file)
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            logger.error('Failed in FileUtil.read_text_file(broker_info_file), caused by ' + error_message)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MultiClusterNetworkService.SYSTEM_INTERNAL_ERROR)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=broker_info_content)

    @staticmethod
    def get_broker_status(cluster_id: str,
                          request_id: str):
        """
        get local broker info
        :param cluster_id: (str) cluster name
        :param request_id: (str) request id
        :return:
        """
        # get submariner_state
        submariner_status = ComponentRepository().get_submariner_state()

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=submariner_status.value)


    @staticmethod
    def create_snapshot(cluster_id: str,
                        request_id: str,
                        migration_id: str,
                        source_cluster_role: str,
                        target_cluster_name: str,
                        source_namespace: str,
                        source_pod: str):
        """
        create snapshot for namespaced pod
        :param cluster_id: (str) source cluster name
        :param request_id: (str) request ID
        :param migration_id: (str) migration request ID
        :param source_cluster_role: (str) multi-cluster role (defined in MultiClusterRole)
        :param target_cluster_name: (str) target cluster name
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :return:
        """
        if source_cluster_role == MultiClusterRole.LOCAL.value:
            local_cluster = cluster_id
        else:
            local_cluster = target_cluster_name

        # check whether shared directory is ready.
        migrate_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=local_cluster)
        ok, error_message = LocalHostCommand.is_directory_accessible(path=migrate_path,
                                                                     timeout=settings.SHARED_DIRECTORY_ACCESS_WAIT)

        template_directory = os.path.join(migrate_path, 'template')

        if not os.path.isdir(template_directory):
            FileUtil.create_directory(template_directory)

        if not ok:
            error = 'Failed in LocalHostCommand.is_directory_accessible({}, timeout=2), ' \
                    'caused by {}'.format(migrate_path, error_message)
            logger.error(error)

            if 'No such file or directory' in error_message:
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SHARED_DIRECTORY_NOT_FOUND.value)

            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.SHARED_DIRECTORY_NOT_READY.value)

        # find service for migrating pod, and create {migrating_pod}_service.yaml
        services = ResourceRepository().get_namespace_services_by_pod(namespace=source_namespace,
                                                                      pod=source_pod)

        if services:
            try:
                ok, services_yaml, error_message = KubeCommand.get_services_yaml(services)
            except Exception as exc:
                error = 'Failed in KubeCommand.get_services_yaml(), caused by ' + get_exception_traceback(exc)
                logger.error(error)
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SERVICE_TEMPLATE_FILE_CREATE_ERROR.value)

            if not ok:
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=error_message)

            service_yaml_file = '{}_service_template.yaml'.format(source_pod)
            save_file = os.path.join(template_directory, service_yaml_file)

            try:
                FileUtil.write_text_file(save_file, services_yaml)
            except Exception as exc:
                error = 'Failed in FileUtil.write_text_file({}, {}), ' \
                        'caused by {}'.format(save_file, source_pod, get_exception_traceback(exc))
                logger.error(error)
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SERVICE_TEMPLATE_FILE_WRITE_ERROR.value)

        # check namespaced pod
        ok, pod_yaml, error_message = \
            KubeCommand.get_namespaced_pod_yaml(pod=source_pod,
                                                namespace=source_namespace)
        if not ok:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error_message)

        # create namespaced pod template to (/mnt/migrate/gedge-cls1/template/{pod name}_template.yaml)
        pod_yaml_file = '{}_template.yaml'.format(source_pod)
        save_file = os.path.join(template_directory, pod_yaml_file)

        try:
            FileUtil.write_text_file(save_file, pod_yaml)
        except Exception as exc:
            error = 'Failed in FileUtil.write_text_file({}, {}), ' \
                    'caused by {}'.format(save_file, source_pod, get_exception_traceback(exc))
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.POD_TEMPLATE_FILE_WRITE_ERROR.value)

        # create snapshot to (/mnt/migrate/gedge-cls1/{pod name}/{pod name}/{container name}/)
        # From above path, secondary pod name is split after '-'
        try:
            snapshot_manifest_temp = FileUtil.read_text_file(settings.SNAPSHOT_MANIFEST_TEMPLATE)
        except Exception as exc:
            error = 'Failed in FileUtil.read_text_file({}), ' \
                    'caused by '.format(settings.SNAPSHOT_MANIFEST_TEMPLATE, get_exception_traceback(exc))
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.MIGRATION_TEMPLATE_FILE_IO_ERROR.value)

        snapshot_manifest = snapshot_manifest_temp.format(migration_id=migration_id,
                                                          namespace=source_namespace,
                                                          local_cluster=local_cluster,
                                                          source_pod=source_pod)
        snapshot_manifest_filename = 'snapshot-{}.yaml'.format(migration_id)

        # save manifest file to temporary directory
        save_file = os.path.join(settings.TEMP_DIRECTORY, snapshot_manifest_filename)

        try:
            FileUtil.write_text_file(save_file, snapshot_manifest)
        except Exception as exc:
            error = 'Failed in FileUtil.write_text_file({}, {}), ' \
                    'caused by {}'.format(save_file, 'snapshot_manifest', get_exception_traceback(exc))
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.MIGRATION_TEMPLATE_FILE_IO_ERROR.value)

        # apply migration(snapshot)
        ok, stdout, stderr = KubeCommand.apply_manifest_file(save_file)

        if not ok:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.SNAPSHOT_MANIFEST_APPLY_ERROR.value)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=None)

    @staticmethod
    def validate_snapshot(cluster_id: str,
                          request_id: str,
                          migration_id: str,
                          source_cluster_role: str,
                          target_cluster_name: str,
                          source_namespace: str,
                          source_pod: str):
        """
        validate snapshot for namespaced pod
        :param cluster_id: (str) source cluster name
        :param request_id: (str) request ID
        :param migration_id: (str) migration request ID
        :param source_cluster_role: (str) multi-cluster role (defined in MultiClusterRole)
        :param target_cluster_name: (str) target cluster name
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :return:
        """
        if source_cluster_role == MultiClusterRole.LOCAL.value:
            local_cluster = cluster_id
        else:
            local_cluster = target_cluster_name

        # check whether shared directory is ready.
        migrate_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=local_cluster)
        ok, error_message = LocalHostCommand.is_directory_accessible(path=migrate_path,
                                                                     timeout=settings.SHARED_DIRECTORY_ACCESS_WAIT)

        if not ok:
            error = 'Failed in LocalHostCommand.is_directory_accessible({}, timeout=2), ' \
                    'caused by {}'.format(migrate_path, error_message)
            logger.error(error)

            if 'No such file or directory' in error_message:
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SHARED_DIRECTORY_NOT_FOUND.value)

            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.SHARED_DIRECTORY_NOT_READY.value)

        # validate migration crd(checkpoint)
        ok, error_message = KubeCommand.validate_livmigration_cro(migration_id=migration_id,
                                                                  operation=MigrationOperation.CHECKPOINT.value,
                                                                  source_pod=source_pod,
                                                                  source_namespace=source_namespace,
                                                                  snapshot_path=migrate_path)
        if not ok:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error_message)

        # check pod and get container name list
        ok, container_name_list, error_message = \
            KubeCommand.get_namespace_pod_container_name_list(pod=source_pod,
                                                              namespace=source_namespace)
        if not ok:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error_message)

        if not container_name_list:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.CONTAINER_NAME_NOT_FOUND.value)

        # check description file
        # create snapshot to (/mnt/migrate/gedge-cls1/{pod name}/{pod name}/{container name}/)
        # From above path, secondary pod name is split after '-'
        split_source_pod_name = source_pod.split('-')[0]

        for container_name in container_name_list:
            check_file = os.path.join(migrate_path,
                                      source_pod,
#                                    split_source_pod_name,
                                      container_name,
                                      'descriptors.json')
            
            time.sleep(2)
            if not os.path.isfile(check_file):
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.DESCRIPTION_FILE_NOT_FOUND.value)

        # delete snapshot resource object and temporary manifest file
        snapshot_manifest_filename = 'snapshot-{}.yaml'.format(migration_id)
        save_file = os.path.join(settings.TEMP_DIRECTORY, snapshot_manifest_filename)

        if os.path.isfile(save_file):
            ok, stdout, stderr = KubeCommand.delete_manifest_file(save_file)

            if not ok:
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SNAPSHOT_MANIFEST_DELETE_ERROR.value)

            FileUtil.delete_file(save_file)
        else:
            error = 'Not found file, file= ' + save_file
            logger.error('Failed to do KubeCommand.delete_manifest_file(save_file), caused by ' + error)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=None)

    @staticmethod
    def restore_snapshot(cluster_id: str,
                         request_id: str,
                         migration_id: str,
                         source_cluster_name: str,
                         source_cluster_role: str,
                         target_node_name: str,
                         source_namespace: str,
                         source_pod: str):
        """
        validate snapshot for namespaced pod
        :param cluster_id: (str) target cluster name
        :param request_id: (str) request ID
        :param migration_id: (str) migration request ID
        :param source_cluster_name: (str) target cluster name
        :param source_cluster_role: (str) multi-cluster role (defined in MultiClusterRole)
        :param target_node_name: (str) target cluster name
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :return:
        """
        if source_cluster_role == MultiClusterRole.LOCAL.value:
            local_cluster = source_cluster_name
        else:
            local_cluster = cluster_id

        # check whether shared directory is ready.
#        migrate_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=local_cluster)
        # check whether shared directory is ready. (modified by KDW)
        temp_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=local_cluster)
        source_pod_exists = os.path.isdir(os.path.join(temp_path, source_pod))
        if source_pod_exists:
          migrate_path = temp_path
          print(migrate_path) 
        else:
          temp_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=source_cluster_name)
          source_pod_exists = os.path.isdir(os.path.join(temp_path, source_pod))
          if source_pod_exists:
             migrate_path = temp_path
             print(migrate_path) 
          else:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.POD_SNAPSHOT_DIRECTORY_NOT_FOUND) 
        print(migrate_path) 

        ok, error_message = LocalHostCommand.is_directory_accessible(path=migrate_path,
                                                                     timeout=settings.SHARED_DIRECTORY_ACCESS_WAIT)

        if not ok:
            error = 'Failed in LocalHostCommand.is_directory_accessible({}, timeout=2), ' \
                    'caused by {}'.format(migrate_path, error_message)
            logger.error(error)

            if 'No such file or directory' in error_message:
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SHARED_DIRECTORY_NOT_FOUND.value)

            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.SHARED_DIRECTORY_NOT_READY.value)

        migrate_pod_path = os.path.join(migrate_path, source_pod)
        ok, error_message = LocalHostCommand.is_directory_accessible(path=migrate_pod_path,
                                                                     timeout=settings.SHARED_DIRECTORY_ACCESS_WAIT)

        if not ok:
            error = 'Failed in LocalHostCommand.is_directory_accessible({}, timeout=2), ' \
                    'caused by {}'.format(migrate_pod_path, error_message)
            logger.error(error)

            if 'No such file or directory' in error_message:
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.POD_SNAPSHOT_DIRECTORY_NOT_FOUND.value)

        service_yaml_file = '{}_service_template.yaml'.format(source_pod)
        template_directory = os.path.join(migrate_path, 'template')
        service_template_file = os.path.join(template_directory, service_yaml_file)

        # create services with service manifest file, if service template is exist
        if os.path.isfile(service_template_file):
            ok, stdout, stderr = KubeCommand.apply_manifest_file(service_template_file)
            if not ok:
                logger.error(stderr)
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SERVICE_MANIFEST_APPLY_ERROR.value)

            # export service(namespace, name) by parse {}_service_template.yaml file
            try:
                service_yaml = FileUtil.read_text_file(service_template_file)
            except Exception as exc:
                error = 'Failed in FileUtil.read_text_file({}), ' \
                        'caused by '.format(service_yaml_file, get_exception_traceback(exc))
                logger.error(error)
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.SERVICE_MANIFEST_READ_ERROR.value)

            service_jsons = yaml.safe_load_all(service_yaml)

            # export services
            for service_json in service_jsons:
                name = service_json['metadata']['name']
                namespace = service_json['metadata']['namespace']
                ok, stdout, stderr = SubmarinerCommand().export_service_nowait(namespace=namespace,
                                                                               name=name)

                if not ok:
                    logger.error('Failed in SubmarinerCommand().export_service(), namespace={}, name={}, '
                                 'caused by {}'.format(namespace, name, stderr))
        # restore snapshot
        try:
            restore_manifest_temp = FileUtil.read_text_file(settings.RESTORE_MANIFEST_TEMPLATE)
        except Exception as exc:
            error = 'Failed in FileUtil.read_text_file({}), ' \
                    'caused by '.format(settings.SNAPSHOT_MANIFEST_TEMPLATE, get_exception_traceback(exc))
            logger.error(error)

            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.MIGRATION_TEMPLATE_FILE_IO_ERROR.value)

        restore_manifest = restore_manifest_temp.format(migration_id=migration_id,
                                                        namespace=source_namespace,
                                                        local_cluster=local_cluster,
                                                        source_pod=source_pod,
                                                        target_node=target_node_name)

        snapshot_manifest_filename = 'restore-{}.yaml'.format(migration_id)

        # save manifest file to temporary directory
        save_file = os.path.join(settings.TEMP_DIRECTORY, snapshot_manifest_filename)

        try:
            FileUtil.write_text_file(save_file, restore_manifest)
        except Exception as exc:
            error = 'Failed in FileUtil.write_text_file({}, {}), ' \
                    'caused by {}'.format(save_file, 'restore_manifest', get_exception_traceback(exc))
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.MIGRATION_TEMPLATE_FILE_IO_ERROR.value)

        # check namespace
        ok, stdout, error = KubeCommand.is_namespace_deployed(source_namespace)

        if not ok:
            ok, stdout, error = KubeCommand.deploy_namespace(source_namespace)
            if not ok:
                logger.error(error)
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=MigrationError.NAMESPACE_NOT_FOUND.value)

        # apply migration(snapshot)
        ok, stdout, stderr = KubeCommand.apply_manifest_file(save_file)
        
        if not ok:
             return error_response(cluster_id=cluster_id,
                                   request_id=request_id,
                                   error=MigrationError.RESTORE_MANIFEST_APPLY_ERROR.value)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=None)

    @staticmethod
    def validate_restored_snapshot(cluster_id: str,
                                   request_id: str,
                                   migration_id: str,
                                   target_node_name: str,
                                   source_cluster_name: str,
                                   source_cluster_role: str,
                                   source_namespace: str,
                                   source_pod: str):
        """
        validate snapshot for namespaced pod
        :param cluster_id: (str) target cluster name
        :param request_id: (str) request ID
        :param migration_id: (str) migration request ID
        :param target_node_name: (str) target cluster name
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :return:
        """
        if source_cluster_role == MultiClusterRole.LOCAL.value:
            local_cluster = source_cluster_name
        else:
            local_cluster = cluster_id

        # check whether shared directory is ready. ( Modified by KDW)
        temp_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=local_cluster)
        source_pod_exists = os.path.isdir(os.path.join(temp_path, source_pod))
        if source_pod_exists:
          migrate_path = temp_path
        else:
          temp_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=source_cluster_name)
          source_pod_exists = os.path.isdir(os.path.join(temp_path, source_pod))
          if source_pod_exists:
             migrate_path = temp_path
          else:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.POD_SNAPSHOT_DIRECTORY_NOT_FOUND)    
                      
        # validate migration crd(restore)
        ok, error_message = KubeCommand.validate_livmigration_cro(migration_id=migration_id,
                                                                  operation=MigrationOperation.RESTORE.value,
                                                                  source_pod=source_pod,
                                                                  source_namespace=source_namespace,
                                                                  snapshot_path=migrate_path,
                                                                  target_node=target_node_name)
        if not ok:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error_message)

        # validate migrate pod is running
        pod_name_prefix = '{source_pod}-migration-'.format(source_pod=source_pod)
        ok, pod_list, error = KubeCommand.get_namespaced_prefix_named_pod(pod_name_prefix, source_namespace)

        if not ok:
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=MigrationError.POD_NOT_FOUND)

        # delete restore resource object manifest file
        # * caution:
        #   - do not delete
        #   - if restore resource object is deleted, restored pod is deleted also.
        snapshot_manifest_filename = 'restore-{}.yaml'.format(migration_id)
        save_file = os.path.join(settings.TEMP_DIRECTORY, snapshot_manifest_filename)

        if os.path.isfile(save_file):
            # ok, stdout, stderr = KubeCommand.delete_manifest_file(save_file)
            #
            # if not ok:
            #     return error_response(cluster_id=cluster_id,
            #                           request_id=request_id,
            #                           error=MigrationError.RESTORE_MANIFEST_DELETE_ERROR.value)
            FileUtil.delete_file(save_file)
        else:
            error = 'Not found file, file= ' + save_file
            logger.error('Failed to do KubeCommand.delete_manifest_file(save_file), caused by ' + error)

        # delete snapshot and template in shared directory
#        migrate_path = settings.NFS_MOUNT_DIR_PATH.format(cluster_id=local_cluster)
        ok, error_message = LocalHostCommand.is_directory_accessible(path=migrate_path,
                                                                     timeout=settings.SHARED_DIRECTORY_ACCESS_WAIT)

        if not ok:
            error = 'Failed in LocalHostCommand.is_directory_accessible({}, timeout=2), ' \
                    'caused by {}'.format(migrate_path, error_message)
            logger.error(error)
            return success_response(cluster_id=cluster_id,
                                    request_id=request_id,
                                    result=None)

        snapshot_path = os.path.join(migrate_path, source_pod)
        template_directory = os.path.join(migrate_path, 'template')
        template_file = os.path.join(template_directory, '{}_template.yaml'.format(source_pod))

        # FileUtil.delete_directory(snapshot_path)
        FileUtil.delete_file(template_file)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=None)

    @staticmethod
    def delete_migration_source(cluster_id: str,
                                request_id: str,
                                source_namespace: str,
                                source_pod: str,
                                migration_id: str = None):
        """
        validate snapshot for namespaced pod
        :param cluster_id: (str) source cluster name
        :param request_id: (str) request ID
        :param migration_id: (str) migration request ID
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :return:
        """
        ok, stdout, stderr = KubeCommand.delete_pod(namespace=source_namespace, pod=source_pod)

        if not ok:
            logger.error('Failed in KubeCommand.delete_pod(namespace={}, pod={}), '
                         'caused by {}'.format(source_namespace, source_pod, stderr))

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=None)
