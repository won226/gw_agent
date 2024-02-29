from django.urls import path
from .views import *

api_version = 'v1'

urlpatterns = [
    #
    # # POST /api/v1/resource/manifest/apply (file transfer), kubectl apply -f <filename>
    # path(api_version + "/resource/manifest/apply", apply_resource_manifest),
    #
    # # POST /api/v1/resource/manifest/delete (file transfer), kubectl delete -f <filename>
    # path(api_version + "/resource/manifest/delete", delete_resource_manifest),
    #
    # # POST /api/v1/resource/manifest/validate
    # path(api_version + "/resource/manifest/validate", validate_resource_manifest),
    #
    # # POST /api/v1/resource/namespace/<str:name>/delete
    # path(api_version + "/resource/namespace/<str:name>/delete", delete_namespace),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/pod/<str:name>/delete
    # path(api_version + "/resource/namespace/<str:namespace>/pod/<str:name>/delete", delete_pod),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/pod/<str:name>/migrate
    # path(api_version + "/resource/namespace/<str:namespace>/pod/<str:name>/migrate", migrate_pod),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/service/<str:name>/delete
    # path(api_version + "/resource/namespace/<str:namespace>/service/<str:name>/delete", delete_service),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/service/<str:name>/export
    # path(api_version + "/resource/namespace/<str:namespace>/service/<str:name>/export", export_service),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/service/<str:name>/unexport
    # path(api_version + "/resource/namespace/<str:namespace>/service/<str:name>/unexport", unexport_service),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/deployment/<str:name>/delete
    # path(api_version + "/resource/namespace/<str:namespace>/deployment/<str:name>/delete", delete_deployment),
    #
    # # POST /api/v1/resource/namespace/<str:namespace>/daemonset/<str:name>/delete
    # path(api_version + "/resource/namespace/<str:namespace>/daemonset/<str:name>/delete", delete_daemonset),
    #
    # # POST /api/v1/resource/monitoring/apply
    # path(api_version + "/resource/monitoring/apply", create_monitoring_resource),
    #
    # # POST /api/v1/resource/monitoring/delete
    # path(api_version + "/resource/monitoring/delete", delete_monitoring_resource),
    #
    # # command status
    # # GET /api/v1/command/<str:command_id>
    # path(api_version + "/command/<str:command_id>", get_command_status),
    #
    # # Multi-cluster network create/delete/connect
    # #
    # # GET /api/v1/mc/network/status
    # path(api_version + "/mc/network/status", get_mc_network_status),
    #
    # # POST /api/v1/mc/network/broker/apply
    # path(api_version + "/mc/network/broker/apply", create_mc_network_broker),
    #
    # # POST /api/v1/mc/network/broker/delete
    # path(api_version + "/mc/network/broker/delete", delete_mc_network_broker),
    #
    # # POST /api/v1/mc/network/broker/disconnect
    # path(api_version + "/mc/network/broker/disconnect", disconnect_mc_network_broker),
    #
    # # POST /api/v1/mc/network/broker/local/connect
    # path(api_version + "/mc/network/broker/local/connect", connect_mc_network_local_broker),
    #
    # # POST /api/v1/mc/network/broker/remote/connect
    # path(api_version + "/mc/network/broker/remote/connect", connect_mc_network_remote_broker),
    #
    # # POST /api/v1/mc/network/broker/remote/update
    # path(api_version + "/mc/network/broker/remote/update", update_remote_broker),
    #
    # # POST /api/v1/mc/volume/local/create
    # path(api_version + "/mc/volume/local/create", create_mc_volume_local),
    #
    # # DELETE /api/v1/mc/volume/local/delete
    # path(api_version + "/mc/volume/local/delete", delete_mc_volume_local),
    #
    # # POST /api/v1/mc/volume/remote/create
    # path(api_version + "/mc/volume/remote/create", create_mc_volume_remote),
    #
    # # DELETE /api/v1/mc/volume/remote
    # path(api_version + "/mc/volume/remote/delete", delete_mc_volume_remote),
    #
    # # GET /api/v1/mc/network/throughput
    # path(api_version + "/mc/network/throughput", get_mc_network_throughput),
    #
    # # POST /api/v1/mc/network/throughput/server/restart
    # path(api_version + "/mc/network/throughput/server/restart", restart_mc_network_benchmark_server),
    #
    # #
    # # test API
    # #
    # # (test) GET /api/v1/hello
    # path(api_version + "/hello/", hello),
    #
    # # (test) POST /api/v1/watch/resource/stop
    # path(api_version + "/watch/resource/stop", stop_watch_resource),
    #
    # # (test) POST /api/v1/watch/resource/start
    # path(api_version + "/watch/resource/start", start_watch_resource),
    #
    # # (test) POST /api/v1/consumer/stop
    # path(api_version + "/mqtt/consumer/stop", stop_mqtt_consumer)

]
