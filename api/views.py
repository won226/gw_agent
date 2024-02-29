# import logging
# import os
# import traceback
#
# # Create your views here.
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
#
# from api.upload import Upload
# from gw_agent import settings
# from gw_agent.common.error import get_exception_traceback
# from cluster.watcher.resources import ResourceWatcher
# from cluster.command.kubernetes import KubeCommand
# from cluster.command.submariner import SubmarinerCommand
# from mqtt.consumer import Consumer
# from repository.cache.components import ComponentRepository
# from repository.cache.network import NetworkStatusRepository
# from repository.common.type import MultiClusterRole, CommandResult, ExecutionStatus
# from utils.fileutils import FileUtil
# from utils.http_response import HttpResponse
#
# logger = logging.getLogger('gw_agent')
#
#
# @api_view(['POST'])
# def delete_namespace(request, name):
#     """
#     POST /api/v1/resource/namespace/<str:name>/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         ok, stdout, stderr = KubeCommand().delete_namespace(name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def delete_pod(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/pod/<str:name>/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_pod(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def migrate_pod(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/pod/<str:name>/migrate
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_pod(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def delete_service(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/service/<str:name>/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         ok, stdout, stderr = KubeCommand().delete_service(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def export_service(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/service/<str:name>/export
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#     if namespace is None or len(namespace) <= 0:
#         HttpResponse.http_return_400_bad_request('Invalid namespace({})'.format(namespace))
#     if name is None or len(name) <= 0:
#         HttpResponse.http_return_400_bad_request('Invalid namespace({})'.format(name))
#
#     try:
#         ok, stdout, stderr = SubmarinerCommand().export_service(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def unexport_service(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/service/<str:name>/unexport
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#
#     if namespace is None or len(namespace) <= 0:
#         HttpResponse.http_return_400_bad_request('Invalid namespace({})'.format(namespace))
#     if name is None or len(name) <= 0:
#         HttpResponse.http_return_400_bad_request('Invalid namespace({})'.format(name))
#
#     try:
#         ok, stdout, stderr = SubmarinerCommand().unexport_service(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# @api_view(['POST'])
# def delete_deployment(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/deployment/<str:name>/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_deployment(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# @api_view(['POST'])
# def delete_daemonset(request, namespace, name):
#     """
#     POST /api/v1/resource/namespace/<str:namespace>/daemonset/<str:name>/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :param namespace: (str)
#     :param name: (str)
#     :return: <class 'rest_framework.response.Response'>
#     """
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_daemonset(namespace, name)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def validate_resource_manifest(request):
#     """
#     validate kubernetes manifest file
#     POST /api/v1/resource/manifest/validate
#     :param request:
#     :return:
#     """
#     attrs = ['yaml'] # file upload attributes in http body
#     ok = True
#     stderr = None
#     uploaded_file = None
#
#     try:
#         uploaded = Upload().http_upload_files(request, attrs)
#         # you can get filename path with http body's attributes
#         uploaded_file = uploaded['yaml']
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if uploaded_file is None:
#         return HttpResponse.http_return_409_conflict('File not found for yaml attr')
#
#     try:
#         ok, stdout, stderr = KubeCommand().validate_manifest(uploaded_file)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# @api_view(['POST'])
# def apply_resource_manifest(request):
#     """
#     POST /api/v1/resource/manifest
#     header
#       - multipart/form-data
#     :param request:
#     :return: <Response>
#     """
#     # file upload attributes in http body
#     attrs = ['yaml']
#     uploaded_file = None
#     ok = True
#     stderr = None
#
#     try:
#         uploaded = Upload().http_upload_files(request, attrs)
#         uploaded_file = uploaded['yaml']
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if uploaded_file is None:
#         return HttpResponse.http_return_409_conflict('File not found for yaml attr')
#
#     # you can get filename path with http body's attributes
#     try:
#         ok, stdout, stderr = KubeCommand().apply_manifest_file(uploaded_file)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# @api_view(['POST'])
# def delete_resource_manifest(request):
#     """
#     DELETE /api/v1/resource/manifest
#     :param request:
#     :return: <Response>
#     """
#     # file upload attributes in http body
#     attrs = ['yaml']
#     ok = True
#     stderr = None
#     uploaded_file = None
#
#     try:
#         uploaded = Upload().http_upload_files(request, attrs)
#         uploaded_file = uploaded['yaml']
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if uploaded_file is None:
#         return HttpResponse.http_return_409_conflict('File not found for yaml attr')
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_manifest_file(uploaded_file)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
#
# # experimental
# @api_view(['POST'])
# def create_monitoring_resource(request):
#     """
#     create cluster monitoring resource
#     POST /api/v1/resource/monitoring/apply
#     :return:
#     """
#
#     try:
#         ok, stdout, stderr = KubeCommand().apply_prometheus()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     try:
#         ok, stdout, stderr = KubeCommand().apply_node_exporter()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     try:
#         ok, stdout, stderr = KubeCommand().apply_k8s_state_metric()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# # experimental
# @api_view(['POST'])
# def delete_monitoring_resource(request):
#     """
#     create cluster monitoring resource
#     POST /api/v1/resource/monitoring/delete
#     :return:
#     """
#     try:
#         ok, stdout, stderr = KubeCommand().delete_k8s_state_metric()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_node_exporter()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     try:
#         ok, stdout, stderr = KubeCommand().delete_prometheus()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# # experimental
# @api_view(['GET'])
# def get_mc_network_status(request):
#     """
#     retrieve submariner network status
#     GET /api/v1/mc/network/status
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     stderr = None
#     ok = True
#     content = None
#
#     try:
#         mc_network = NetworkStatusRepository().get_mc_network()
#         content = mc_network.to_dict()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(content)
#
# # experimental
# @api_view(['POST'])
# def create_mc_network_broker(request):
#     """
#     deploy submariner broker
#     POST /api/v1/mc/network/broker/apply
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     content = None
#     ok = True
#     command_id = None
#     ret = CommandResult.UNKNOWN
#
#     try:
#         ret, command_id, stderr = ComponentRepository().create_submariner_broker()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok or ret == CommandResult.UNKNOWN:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if ret == CommandResult.BUSY:
#         return HttpResponse.http_return_409_conflict(stderr)
#
#     if ret == CommandResult.ACCEPT:
#         return HttpResponse.http_return_202_accepted({'command_id': command_id})
#
#     return HttpResponse.http_return_200_ok(content)
#
# # experimental
# @api_view(['POST'])
# def delete_mc_network_broker(request):
#     """
#     uninstall submariner
#     POST /api/v1/mc/network/broker/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     content = None
#     ok = True
#     command_id = None
#     ret = CommandResult.UNKNOWN
#
#     try:
#         ret, command_id, stderr = ComponentRepository().cleanup_submariner_broker()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok or ret == CommandResult.UNKNOWN:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if ret == CommandResult.BUSY:
#         return HttpResponse.http_return_409_conflict(stderr)
#
#     if ret == CommandResult.ACCEPT:
#         return HttpResponse.http_return_202_accepted({'command_id': command_id})
#
#     return HttpResponse.http_return_200_ok(content)
#
#
# @api_view(['POST'])
# def connect_mc_network_local_broker(request):
#     """
#     join submariner broker(local)
#     POST /api/v1/mc/network/broker/local/connect
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         if MultiClusterConfig().get_enabled():
#             return HttpResponse.http_return_409_conflict('Already exist multi-cluster connection')
#
#         if ComponentRepository().is_submariner_running():
#             return HttpResponse.http_return_503_service_unavailable('submariner is busy')
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     ok = True
#     content = None
#     command_id = None
#     ret = CommandResult.UNKNOWN
#
#     # check whether broker is installed or not
#     broker_info_file = os.path.join(settings.LOCAL_BROKER_INFO, 'broker-info.subm')
#
#     if not os.path.isfile(broker_info_file):
#         return HttpResponse.http_return_409_conflict('Not found broker-info file')
#
#     try:
#         ret, command_id, stderr = \
#             ComponentRepository().join_submariner_broker(MultiClusterRole.LOCAL.value,
#                                                          broker_info_file)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok or ret == CommandResult.UNKNOWN:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if ret == CommandResult.BUSY:
#         return HttpResponse.http_return_409_conflict(stderr)
#
#     if ret == CommandResult.ACCEPT:
#         MultiClusterConfig().set_enabled(True)
#         MultiClusterConfig().set_role(MultiClusterRole.LOCAL.value)
#         MultiClusterConfig().set_remote_broker_updated(False)
#         return HttpResponse.http_return_202_accepted({'command_id': command_id})
#
#     return HttpResponse.http_return_200_ok(content)
#
# @api_view(['GET'])
# def get_command_status(request, command_id):
#     """
#     get command status
#     GET /api/v1/command/<str:command_id>
#     :param request:
#     :param command_id: (str)
#     :return:
#     """
#     stderr = None
#     ret = None
#     ok = True
#
#     if command_id is None:
#         return HttpResponse.http_return_400_bad_request('Invalid command_id')
#
#     try:
#         ret = ComponentRepository().get_command_status(command_id=command_id)
#
#         if ret is None:
#             return HttpResponse.http_return_400_bad_request('Not found command status for {}'.format(command_id))
#
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(ret)
#
# @api_view(['POST'])
# def update_remote_broker(request):
#     """
#     update remote broker
#     POST /api/v1/mc/network/broker/remote/update
#     :param request:
#     :return:
#     """
#     if not MultiClusterConfig().get_enabled():
#         return HttpResponse.http_return_400_bad_request('Not exist multi-cluster connection')
#
#     # file upload attributes in http body
#     attrs = ['broker_info_file']
#     ok = True
#     uploaded_file = None
#     stderr = None
#     content = None
#
#     try:
#         uploaded = Upload().http_upload_files(request, attrs)
#         uploaded_file = uploaded['broker_info_file']
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     # move upload file to remote broker info directory
#     broker_info_file = os.path.join(settings.REMOTE_BROKER_INFO, 'broker-info.subm')
#     try:
#         FileUtil.move_file(uploaded_file, broker_info_file)
#         MultiClusterConfig().set_remote_broker_updated(True)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(content)
#
#
# @api_view(['POST'])
# def connect_mc_network_remote_broker(request):
#     """
#     join submariner broker(remote)
#     POST /api/v1/mc/network/broker/remote/connect
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         if MultiClusterConfig().get_enabled():
#             return HttpResponse.http_return_400_bad_request('Already exist multi-cluster connection')
#
#         if ComponentRepository().is_submariner_running():
#             return HttpResponse.http_return_503_service_unavailable('submariner is busy')
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     # file upload attributes in http body
#     attrs = ['broker_info_file']
#     ok = True
#     uploaded_file = None
#     stderr = None
#     command_id = None
#     content = None
#     ret = CommandResult.UNKNOWN
#
#     try:
#         uploaded = Upload().http_upload_files(request, attrs)
#         uploaded_file = uploaded['broker_info_file']
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     # move upload file to remote broker info directory
#     broker_info_file = os.path.join(settings.REMOTE_BROKER_INFO, 'broker-info.subm')
#     FileUtil.move_file(uploaded_file, broker_info_file)
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if uploaded_file is None:
#         return HttpResponse.http_return_409_conflict('File not found for yaml attr')
#     try:
#         ret, command_id, stderr = ComponentRepository().join_submariner_broker('remote', broker_info_file)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok or ret == CommandResult.UNKNOWN:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if ret == CommandResult.BUSY:
#         return HttpResponse.http_return_409_conflict(stderr)
#
#     if ret == CommandResult.ACCEPT:
#         MultiClusterConfig().set_enabled(True)
#         MultiClusterConfig().set_role(MultiClusterRole.REMOTE.value)
#         MultiClusterConfig().set_remote_broker_updated(False)
#         return HttpResponse.http_return_202_accepted({'command_id': command_id})
#
#     return HttpResponse.http_return_200_ok(content)
#
# @api_view(['POST'])
# def disconnect_mc_network_broker(request):
#     """
#     join submariner broker(remote)
#     POST /api/v1/mc/network/broker/disconnect
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     command_id = None
#     content = None
#     ret = CommandResult.UNKNOWN
#     ok = True
#     stderr = None
#
#     try:
#         if not MultiClusterConfig().get_enabled():  # already disconnected
#             return HttpResponse.http_return_200_ok(content)
#
#         if ComponentRepository().is_submariner_running():
#             return HttpResponse.http_return_503_service_unavailable('submariner is busy')
#     except Exception as exc:
#         ok = False
#         stderr = get_exception_traceback(exc)
#     if not ok:
#         logger.error('Fail to set broker config caused by {}'.format(stderr))
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     try:
#         ret, command_id, stderr = ComponentRepository().cleanup_submariner_join_components()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok or ret == CommandResult.UNKNOWN:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     if ret == CommandResult.BUSY:
#         return HttpResponse.http_return_409_conflict(stderr)
#
#     if ret == CommandResult.ACCEPT:
#         MultiClusterConfig().reset_config()
#         return HttpResponse.http_return_202_accepted({'command_id': command_id})
#
#     return HttpResponse.http_return_200_ok(content)
#
# # experimental
# @api_view(['POST'])
# def create_mc_volume_local(request):
#     """
#     deploy NFS server, client in local cluster
#     POST /api/v1/mc/volume/local/create
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         # apply nfs-server
#         ok, stdout, stderr = KubeCommand.apply_nfs_server()
#         if not ok:
#             return HttpResponse.http_return_500_internal_server_error(stderr)
#         # apply local nfs-client
#         ok, stdout, stderr = KubeCommand.apply_nfs_client(MultiClusterRole.LOCAL.value)
#         if not ok:
#             return HttpResponse.http_return_500_internal_server_error(stderr)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(stderr)
#
#
# # experimental
# @api_view(['POST'])
# def delete_mc_volume_local(request):
#     """
#     delete NFS server, client in local cluster
#     DELETE /api/v1/mc/volume/local/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         # delete nfs-server
#         ok, stdout, stderr = KubeCommand.delete_nfs_server()
#         if not ok:
#             return HttpResponse.http_return_500_internal_server_error(stderr)
#
#         # delete nfs-client local
#         ok, stdout, stderr = KubeCommand.delete_nfs_client(MultiClusterRole.LOCAL.value)
#         if not ok:
#             return HttpResponse.http_return_500_internal_server_error(stderr)
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(stderr)
#
#
# # experimental
# @api_view(['POST'])
# def create_mc_volume_remote(request):
#     """
#     deploy NFS client to connect remote cluster
#     POST /api/v1/mc/volume/remote/create
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         ok, stdout, stderr = KubeCommand.apply_nfs_client('remote')
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(stderr)
#
#
# # experimental
# @api_view(['POST'])
# def delete_mc_volume_remote(request):
#     """
#     delete NFS client to connect remote cluster
#     DELETE /api/v1/mc/volume/remote/delete
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     try:
#         ok, stdout, stderr = KubeCommand.delete_nfs_client('remote')
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(stderr)
#
# # experimental
# # todo: fix me!
# @api_view(['GET'])
# def get_mc_network_throughput(request):
#     """
#     get multi-cluster network throughput measured
#     GET /api/v1/mc/network/throughput
#     :param request: <class 'rest_framework.request.Request'>
#     :return: <class 'rest_framework.response.Response'>
#     """
#     http_body = {}
#
#     # implement get netstat throughput measure status
#     http_body['error'] = 'none'
#     return Response(data=http_body,
#                     status=status.HTTP_200_OK)
#
# # experimental
# @api_view(['POST'])
# def stop_watch_resource(request):
#     """
#     # POST /api/v1/watch/resource/stop
#     :param request:
#     :return:
#     """
#     ok = True
#     stderr = None
#
#     try:
#         ResourceWatcher().stop()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# # experimental
# @api_view(['POST'])
# def start_watch_resource(request):
#     """
#     POST /api/v1/watch/resource/start
#     :param request:
#     :return:
#     """
#     stderr = None
#     ok = True
#
#     try:
#         ResourceWatcher().start()
#     except Exception as exc:
#         stderr = get_exception_traceback(exc)
#         logger.error(stderr)
#         ok = False
#     if not ok:
#         return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok(None)
#
# @api_view(['POST'])
# def stop_mqtt_consumer(request):
#     """
#     POST /api/v1/consumer/stop
#     :param request:
#     :return:
#     """
#     try:
#         Consumer().stop()
#     except Exception as exc:
#         error = get_exception_traceback(exc)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     HttpResponse.http_return_200_ok('')
#
# @api_view(['GET'])
# def hello(request):
#     return Response('hello')