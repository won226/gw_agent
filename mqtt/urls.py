from mqtt.controller import *

base_url = '/cluster/:cluster'

urlpatterns = [
    (base_url + '/namespace/:namespace', control_namespace),
    (base_url + '/namespace/:namespace/pod/:pod', control_pod),
    (base_url + '/namespace/:namespace/service/:service', control_service),
    (base_url + '/namespace/:namespace/deployment/:deployment', control_deployment),
    (base_url + '/namespace/:namespace/daemonset/:daemonset', control_daemonset),
    (base_url + '/manifest/validate', validate_resource_manifest),
    (base_url + '/manifest/apply', apply_resource_manifest),
    (base_url + '/manifest/delete', delete_resource_manifest),
    (base_url + '/mcn/broker', get_broker_info),
    (base_url + '/mcn/broker/status', get_broker_status),
    (base_url + '/mcn/broker/connect', connect_multi_cluster_network),
    (base_url + '/mcn/broker/disconnect', disconnect_multi_cluster_network),
    (base_url + '/namespace/:namespace/service/:service/export', export_service),
    (base_url + '/namespace/:namespace/service/:service/unexport', unexport_service),
    (base_url + '/namespace/:namespace/pod/:pod/migrate/snapshot', create_snapshot),
    (base_url + '/namespace/:namespace/pod/:pod/migrate/validate_snapshot', validate_snapshot),
    (base_url + '/namespace/:namespace/pod/:pod/migrate/restore', restore_snapshot),
    (base_url + '/namespace/:namespace/pod/:pod/migrate/validate_restore', validate_restored_snapshot),
    (base_url + '/namespace/:namespace/pod/:pod/migrate/delete_migration_source', delete_migration_source),

    (base_url, remove_agent),
]
