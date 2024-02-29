from gw_agent.settings import get_logger
from cluster.command.localhost import LocalHostCommand
from cluster.command.submariner import SubmarinerCommand
from mqtt.model.common.type import Method
from mqtt.model.request import Request
from mqtt.service import error_response, success_response, K8sResourceService, MultiClusterNetworkService
from repository.cache.network import NetworkStatusRepository
from repository.cache.resources import ResourceRepository
from repository.common.type import MultiClusterRole

logger = get_logger(__name__)


def control_namespace(request):
    """
    control namespace
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body() # body parameters

    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.DELETE.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        return K8sResourceService.delete_namespace(cluster_id=cluster_id,
                                                   request_id=request_id,
                                                   namespace=namespace)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

def control_pod(request):
    """
    control pod
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body() # body parameters

    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.DELETE.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        if 'pod' not in arguments:
            error = 'Not found argument \'pod\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        pod = arguments['pod']

        return K8sResourceService.delete_pod(cluster_id=cluster_id,
                                             request_id=request_id,
                                             namespace=namespace,
                                             pod=pod)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def control_service(request):
    """
    control service
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body() # body parameters

    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.DELETE.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        if 'service' not in arguments:
            error = 'Not found argument \'service\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        service = arguments['service']

        return K8sResourceService.delete_service(cluster_id=cluster_id,
                                                 request_id=request_id,
                                                 namespace=namespace,
                                                 service=service)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def control_deployment(request):
    """
    control deployment
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body() # body parameters

    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.DELETE.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        if 'deployment' not in arguments:
            error = 'Not found argument \'service\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        deployment = arguments['deployment']

        return K8sResourceService.delete_deployment(cluster_id=cluster_id,
                                                    request_id=request_id,
                                                    namespace=namespace,
                                                    deployment=deployment)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def control_daemonset(request):
    """
    control daemonset
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body() # body parameters

    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.DELETE.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        if 'daemonset' not in arguments:
            error = 'Not found argument \'daemonset\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        daemonset = arguments['daemonset']

        return K8sResourceService.delete_daemonset(cluster_id=cluster_id,
                                                   request_id=request_id,
                                                   namespace=namespace,
                                                   daemonset=daemonset)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def validate_resource_manifest(request):
    """
    validate resource manifest file
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body() # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster = arguments['cluster']

        if body is None:
            error = 'Not found body'
            logger.error(error)
            return error_response(cluster_id=cluster,
                                  request_id=request_id,
                                  error=error)

        if 'manifest' not in body:
            error = 'Not found body param(\'manifest\')'
            return error_response(cluster_id=cluster,
                                  request_id=request_id,
                                  error=error)

        manifest = body['manifest']

        return K8sResourceService.validate_resource_manifest(cluster_id=cluster,
                                                             request_id=request_id,
                                                             manifest=manifest)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def apply_resource_manifest(request: Request):
    """
    apply resource manifest file
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body() # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster = arguments['cluster']

        if body is None:
            error = 'Not found body'
            logger.error(error)
            return error_response(cluster_id=cluster,
                                  request_id=request_id,
                                  error=error)

        if 'manifest' not in body:
            error = 'Not found body param(\'manifest\')'
            return error_response(cluster_id=cluster,
                                  request_id=request_id,
                                  error=error)

        manifest = body['manifest']

        return K8sResourceService.apply_resource_manifest(cluster_id=cluster,
                                                          request_id=request_id,
                                                          manifest=manifest)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def delete_resource_manifest(request):
    """
    apply resource manifest file
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body() # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster = arguments['cluster']

        if body is None:
            error = 'Not found body'
            logger.error(error)
            return error_response(cluster_id=cluster,
                                  request_id=request_id,
                                  error=error)

        if 'manifest' not in body:
            error = 'Not found body param(\'manifest\')'
            return error_response(cluster_id=cluster,
                                  request_id=request_id,
                                  error=error)

        manifest = body['manifest']

        return K8sResourceService.delete_resource_manifest(cluster_id=cluster,
                                                           request_id=request_id,
                                                           manifest=manifest)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def export_service(request):
    """
    export service
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body() # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        if 'service' not in arguments:
            error = 'Not found argument \'service\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        service = arguments['service']

        if not NetworkStatusRepository().is_mc_network_connected():
            stderr = 'Multi cluster network is not connected'
            logger.debug(stderr)
            return error_response(cluster_id, request_id, stderr)

        ok, stdout, stderr = SubmarinerCommand().export_service(namespace, service)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def unexport_service(request: Request):
    """
    unexport service
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        namespace = arguments['namespace']

        if 'service' not in arguments:
            error = 'Not found argument \'service\' in path'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        service = arguments['service']

        if not NetworkStatusRepository().is_mc_network_connected():
            stderr = 'Multi cluster network is not connected'
            logger.debug(stderr)
            return error_response(cluster_id, request_id, stderr)

        ok, stdout, stderr = SubmarinerCommand().unexport_service(namespace, service)

        if not ok:
            return error_response(cluster_id, request_id, stderr)

        return success_response(cluster_id, request_id, stdout)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def connect_multi_cluster_network(request):
    """
    connect multi-cluster network
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if not cluster_id or type(cluster_id) != str:
            error = 'Invalid \'cluster\' value in path. cluster={}'.format(cluster_id)
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        if not body:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        # get multi-cluster connect id from body
        if 'mc_connect_id' not in body:
            error = 'Not found body param(\'mc_connect_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        content = body['mc_connect_id'].get_content()

        if not content:
            error = 'Not found body param(\'mc_connect_id\') value'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        mc_connect_id = content[0]

        if not mc_connect_id or len(mc_connect_id) <= 0:
            error = 'Invalid \'mc_connect_id\' value in body. mc_connect_id={}'.format(mc_connect_id)
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        # get role from body
        if 'role' not in body:
            error = 'Not found body param(\'role\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        content = body['role'].get_content()

        if not content:
            error = 'Not found body param(\'role\') value'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        role = content[0]

        if not role or not MultiClusterRole.validate(role):
            error = 'Invalid \'role\' value in path. role={}'.format(role)
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        # get remote_cluster_id from body
        if 'remote_cluster_id' not in body:
            error = 'Not found body param(\'remote_cluster_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        content = body['remote_cluster_id'].get_content()

        if not content:
            error = 'Not found body param(\'remote_cluster_id\') value'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        remote_cluster_id = content[0]

        # in cased of joining local broker
        if role == MultiClusterRole.LOCAL.value:
            return MultiClusterNetworkService.connect_local_broker(
                cluster_id=cluster_id,
                request_id=request_id,
                connect_id=mc_connect_id,
                remote_cluster_id=remote_cluster_id)

        # in cased of joining remote broker
        elif role == MultiClusterRole.REMOTE.value:
            # get join broker-info.subm file from body
            if 'broker_info' not in body:
                error = 'Not found body param(\'broker_info\')'
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=error)

            content = body['broker_info'].get_content()

            broker_info_content = content[0]

            if not broker_info_content or len(broker_info_content) <= 0:
                error = 'Invalid \'broker_info\' value'
                return error_response(cluster_id=cluster_id,
                                      request_id=request_id,
                                      error=error)

            # join to remote broker
            return MultiClusterNetworkService.connect_remote_broker(
                cluster_id=cluster_id,
                request_id=request_id,
                broker_info_content=broker_info_content,
                connect_id=mc_connect_id,
                remote_cluster_id=remote_cluster_id)

        else:
            error = 'Invalid role value in body. role={}. role must be Local or Remote'.format(role)
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


def disconnect_multi_cluster_network(request):
    """
    disconnect multi-cluster network
    POST /cluster/:cluster/mcn/broker/disconnect
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if not cluster_id or type(cluster_id) != str:
            error = 'Invalid \'cluster\' value in path. cluster={}'.format(cluster_id)
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        if body is None:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        if 'mc_connect_id' not in body:
            error = 'Not found body param(\'mc_connect_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        content = body['mc_connect_id'].get_content()

        if not content:
            error = 'Not found body param(\'mc_connect_id\') value'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        mc_connect_id = content[0]

        if not mc_connect_id or len(mc_connect_id) <= 0:
            error = 'Invalid \'mc_connect_id\' value in body. mc_connect_id={}'.format(mc_connect_id)
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        # disconnect submariner broker
        return MultiClusterNetworkService.disconnect_broker(cluster_id=cluster_id,
                                                            request_id=request_id,
                                                            connect_id=mc_connect_id)

    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

def get_broker_info(request):
    """
    get local broker info(broker-info.subm)
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.GET.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        # get local submariner broker-info.subm
        return MultiClusterNetworkService.get_local_broker_info(cluster_id=cluster_id,
                                                                request_id=request_id)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

def get_broker_status(request):
    """
    get submariner status
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.GET.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        # get local submariner broker-info.subm
        return MultiClusterNetworkService.get_broker_status(cluster_id=cluster_id,
                                                            request_id=request_id)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)


# TODO: impl from here, test!!
def create_snapshot(request):
    """
    create snapshot
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        namespace = arguments['namespace']

        if 'pod' not in arguments:
            error = 'Not found argument \'pod\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        pod = arguments['pod']

        if body is None:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        if 'migration_id' not in body:
            error = 'Not found body param(\'migration_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['migration_id'].get_content()
        migration_id = content[0]

        if 'source_cluster_role' not in body:
            error = 'Not found body param(\'source_cluster_role\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['source_cluster_role'].get_content()
        source_cluster_role = content[0]

        if 'target_cluster_name' not in body:
            error = 'Not found body param(\'target_cluster_name\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['target_cluster_name'].get_content()
        target_cluster_name = content[0]

        # create snapshot
        return MultiClusterNetworkService.create_snapshot(cluster_id=cluster_id,
                                                          request_id=request_id,
                                                          migration_id=migration_id,
                                                          source_cluster_role=source_cluster_role,
                                                          target_cluster_name=target_cluster_name,
                                                          source_namespace=namespace,
                                                          source_pod=pod)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

# TODO: impl from here, test!!
def validate_snapshot(request):
    """
    validate snapshot
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        namespace = arguments['namespace']

        if 'pod' not in arguments:
            error = 'Not found argument \'pod\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        pod = arguments['pod']

        if body is None:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        if 'migration_id' not in body:
            error = 'Not found body param(\'migration_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['migration_id'].get_content()
        migration_id = content[0]

        if 'source_cluster_role' not in body:
            error = 'Not found body param(\'source_cluster_role\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['source_cluster_role'].get_content()
        source_cluster_role = content[0]

        if 'target_cluster_name' not in body:
            error = 'Not found body param(\'target_cluster_name\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['target_cluster_name'].get_content()
        target_cluster_name = content[0]

        # validate snapshot
        return MultiClusterNetworkService.validate_snapshot(cluster_id=cluster_id,
                                                            request_id=request_id,
                                                            migration_id=migration_id,
                                                            source_cluster_role=source_cluster_role,
                                                            target_cluster_name=target_cluster_name,
                                                            source_namespace=namespace,
                                                            source_pod=pod)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

# todo: impl here, test!!
def restore_snapshot(request):
    """
    create snapshot
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        namespace = arguments['namespace']

        if 'pod' not in arguments:
            error = 'Not found argument \'pod\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        pod = arguments['pod']

        if body is None:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        if 'migration_id' not in body:
            error = 'Not found body param(\'migration_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['migration_id'].get_content()
        migration_id = content[0]

        if 'source_cluster_role' not in body:
            error = 'Not found body param(\'source_cluster_role\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['source_cluster_role'].get_content()
        source_cluster_role = content[0]

        if 'source_cluster_name' not in body:
            error = 'Not found body param(\'source_cluster_name\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['source_cluster_name'].get_content()
        source_cluster_name = content[0]

        if 'target_node_name' not in body:
            error = 'Not found body param(\'target_node_name\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['target_node_name'].get_content()
        target_node_name = content[0]

        # restore snapshot
        return MultiClusterNetworkService.restore_snapshot(cluster_id=cluster_id,
                                                           request_id=request_id,
                                                           migration_id=migration_id,
                                                           source_cluster_name=source_cluster_name,
                                                           source_cluster_role=source_cluster_role,
                                                           target_node_name=target_node_name,
                                                           source_namespace=namespace,
                                                           source_pod=pod)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

# todo: impl here, test!!
def validate_restored_snapshot(request):
    """
    create snapshot
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        namespace = arguments['namespace']

        if 'pod' not in arguments:
            error = 'Not found argument \'pod\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        pod = arguments['pod']

        if body is None:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        if 'migration_id' not in body:
            error = 'Not found body param(\'migration_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['migration_id'].get_content()
        migration_id = content[0]

        if 'target_node_name' not in body:
            error = 'Not found body param(\'target_node_name\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['target_node_name'].get_content()
        target_node_name = content[0]

        if 'source_cluster_name' not in body:
            error = 'Not found body param(\'source_cluster_name\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['source_cluster_name'].get_content()
        source_cluster_name = content[0]

        if 'source_cluster_role' not in body:
            error = 'Not found body param(\'source_cluster_role\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)
        content = body['source_cluster_role'].get_content()
        source_cluster_role = content[0]

        # validate restored snapshot
        return MultiClusterNetworkService.validate_restored_snapshot(cluster_id=cluster_id,
                                                                     request_id=request_id,
                                                                     migration_id=migration_id,
                                                                     target_node_name=target_node_name,
                                                                     source_cluster_name=source_cluster_name,
                                                                     source_cluster_role=source_cluster_role,
                                                                     source_namespace=namespace,
                                                                     source_pod=pod)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

# todo: impl here
def delete_migration_source(request):
    """
    create snapshot
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.POST.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        if 'namespace' not in arguments:
            error = 'Not found argument \'namespace\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        namespace = arguments['namespace']

        if 'pod' not in arguments:
            error = 'Not found argument \'pod\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)
        pod = arguments['pod']

        if body is None:
            error = 'Not found body in message'
            logger.error(error)
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        if 'migration_id' not in body:
            error = 'Not found body param(\'migration_id\')'
            return error_response(cluster_id=cluster_id,
                                  request_id=request_id,
                                  error=error)

        content = body['migration_id'].get_content()
        migration_id = content[0]

        # delete migration source
        return MultiClusterNetworkService.delete_migration_source(cluster_id=cluster_id,
                                                                  request_id=request_id,
                                                                  migration_id=migration_id,
                                                                  source_namespace=namespace,
                                                                  source_pod=pod)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)

def remove_agent(request):
    """
    remove agent
    :param request: (mqtt.model.request.Request)
    :return:
    """
    request_id = request.get_request_id()
    arguments = request.get_arguments()  # path variables
    # query_params = request.get_query_params()
    method = request.get_method()  # GET, POST, PUT, DELETE
    # body = request.get_body()  # body parameters
    my_cluster_id = ResourceRepository().get_cluster_id()

    if method == Method.DELETE.value:
        if 'cluster' not in arguments:
            error = 'Not found argument \'cluster\' in path'
            logger.error(error)
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error)

        cluster_id = arguments['cluster']

        # todo: implement remove agent
        ok, error_message = LocalHostCommand.remove_agent()

        if not ok:
            return error_response(cluster_id=my_cluster_id,
                                  request_id=request_id,
                                  error=error_message)

        return success_response(cluster_id=cluster_id,
                                request_id=request_id,
                                result=None)
    else:
        error = 'Not supported method {}'.format(method)
        logger.error(error)
        return error_response(cluster_id=my_cluster_id,
                              request_id=request_id,
                              error=error)