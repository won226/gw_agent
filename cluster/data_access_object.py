from django.apps import apps

from gw_agent.common.error import get_exception_traceback
from repository.common.type import MultiClusterRole, MultiClusterConfigState


class ClusterDAO:
    """
    Cluster data access object(DAO) class
    """

    @classmethod
    def initialize_cluster(cls, cluster_name: str) -> (bool, str):
        """
        initialize cluster
        :param cluster_name: (str) cluster name
        :return:
        (bool) success
        (str) error_message
        """
        if not cluster_name:
            raise ValueError('Invalid \'cluster_name\' param value. cluster_name=' + cluster_name)

        error_message = None
        Cluster = apps.get_model('cluster', 'Cluster')

        try:
            cluster_objects = Cluster.objects.all()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        if len(cluster_objects) <= 0:
            cluster = Cluster()
            cluster.cluster_name = cluster_name

            try:
                cluster.save()
            except Exception as exc:
                error_message = get_exception_traceback(exc)
                return False, error_message

        return True, error_message

    @classmethod
    def get_cluster(cls) -> (bool, object, str):
        """
        get cluster
        :return:
        (bool) success
        (object) cluster.models.Cluster
        (str) error message
        """
        error_message = 'no_error'
        Cluster = apps.get_model('cluster', 'Cluster')

        try:
            cluster_objects = Cluster.objects.all()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, None, error_message

        if not cluster_objects:
            return False, None, 'Not found cluster entry'

        return True, cluster_objects[0], error_message

    @classmethod
    def get_remote_cluster_name(cls) -> (bool, object, str):
        """
        get remote cluster name
        :return:
        (bool) success
        (str) remote cluster id connected
        (str) error message
        """
        ok, cluster_object, error_message = ClusterDAO.get_cluster()

        if not ok:
            return ok, None, error_message

        remote_cluster_name = cluster_object.remote_cluster_name

        return ok, remote_cluster_name, None

    @classmethod
    def set_multi_cluster_connection(cls,
                                     role: str,
                                     mc_connect_id: str,
                                     is_mc_provisioned: bool,
                                     remote_cluster_name: str) -> (bool, str):
        """
        set multi-cluster connection
        :param role: (str) "Local", "Remote"
        :param mc_connect_id: (str) uuid4
        :param is_mc_provisioned: (bool) True - provisioned, False - not provisioned
        :param remote_cluster_name: (str) remote cluster name
        :return:
        (bool) success
        (str) error_message
        """
        if not mc_connect_id or type(mc_connect_id) != str:
            raise ValueError('Invalid \'mc_connect_id\' param value. mc_connect_id='+mc_connect_id)

        if not role or type(role) != str or not MultiClusterRole.validate(role):
            raise ValueError('Invalid \'role\' param value. role='+role)

        if type(is_mc_provisioned) != bool:
            raise ValueError('Invalid value \'is_mc_provisioned\' param value. Input bool type')

        ok, cluster_object, error_message = cls.get_cluster()

        if not ok:
            return ok, cluster_object, error_message

        cluster_object.role = role
        cluster_object.mc_connect_id = mc_connect_id
        cluster_object.is_mc_provisioned = is_mc_provisioned
        cluster_object.remote_cluster_name = remote_cluster_name

        try:
            cluster_object.save()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        return True, error_message

    @classmethod
    def get_multi_cluster_provisioned(cls) -> (bool, bool, str):
        """
        get multi-cluster provisioned field
        :return:
        (bool) True - success, False - fail
        (bool) True - provisioned, False - not provisioned
        (str) error message
        """
        ok, cluster_object, error_message = cls.get_cluster()

        if not ok:
            return False, False, error_message

        return ok, cluster_object.is_mc_provisioned, error_message

    @classmethod
    def set_multi_cluster_provisioned(cls) -> (bool, bool, str):
        """
        set multi-cluster to provisioned
        :return:
        (bool) True - success, False - fail
        (str) error message
        """
        ok, cluster_object, error_message = cls.get_cluster()

        if not ok:
            return False, error_message

        cluster_object.is_mc_provisioned = True

        try:
            cluster_object.save()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        return True, error_message

    @classmethod
    def reset_multi_cluster_connection(cls) -> (bool, str):
        """
        reset multi-cluster connection
        :return:
        (bool) success
        (str) error_message
        """
        ok, cluster_object, error_message = cls.get_cluster()

        if not ok:
            return ok, error_message

        cluster_object.role = MultiClusterRole.NONE.value
        cluster_object.mc_connect_id = None
        cluster_object.remote_cluster_name = None
        cluster_object.is_mc_provisioned = False

        try:
            cluster_object.save()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        return True, error_message

    @classmethod
    def get_multi_cluster_config(cls) -> (bool, object, str):
        """
        get multi-cluster config
        :return:
        (bool) success
        (object) cluster.models.MultiClusterConfig
        (str) error message
        """
        error_message = None

        MultiClusterConfig = apps.get_model('cluster', 'MultiClusterConfig')

        try:
            mc_config_objects = MultiClusterConfig.objects.all()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message, None

        if len(mc_config_objects) <= 0:
            request_object = MultiClusterConfig()
            request_object.save()

            return True, request_object, error_message

        return True, mc_config_objects[0], error_message

    @classmethod
    def set_multi_cluster_config_request(cls,
                                         multi_cluster_config_state: str,
                                         mc_connect_id: str,
                                         remote_cluster_name: str,
                                         role: str) -> (bool, str):
        """
        set multi-cluster config request
        :param multi_cluster_config_state: (str) 'Connect' or 'Disconnect'
        :param mc_connect_id: (str) uuid4, multi-cluster connection ID issued from CEdge-center
        :param remote_cluster_name: (str) remote cluster name
        :param role: (str) 'Local', 'Remote'
        :return:
        (bool) success
        (str) error_message
        """
        if not multi_cluster_config_state or not MultiClusterConfigState.validate(multi_cluster_config_state):
            raise ValueError('Invalid \'multi_cluster_config_state\' param value. '
                             'multi_cluster_config_state='+multi_cluster_config_state)

        if not mc_connect_id or len(mc_connect_id) <= 0:
            raise ValueError('Invalid \'mc_connect_id\' param value. mc_connect_id=' + mc_connect_id)

        if not role or type(role) != str or not MultiClusterRole.validate(role):
            raise ValueError('Invalid \'role\' param value. role='+role)

        ok, request_object, error_message  = cls.get_multi_cluster_config()

        if not ok:
            return ok, error_message

        request_object.mc_config_state = multi_cluster_config_state
        request_object.role = role
        request_object.mc_connect_id = mc_connect_id
        request_object.remote_cluster_name = remote_cluster_name
        request_object.save()

        return ok, error_message

    @classmethod
    def set_mc_config_state_to_connecting(cls) -> (bool, str):
        """
        set multi-cluster-config-state to connecting
        :return:
        (bool) success
        (str) error_message
        """
        ok, request_object, error_message  = cls.get_multi_cluster_config()

        if not ok:
            return ok, error_message

        # update multi-cluster-config-state to "Connecting"
        request_object.mc_config_state = MultiClusterConfigState.CONNECTING.value
        request_object.save()

        return ok, error_message

    @classmethod
    def set_mc_config_state_to_disconnecting(cls) -> (bool, str):
        """
        set multi-cluster-config-state to connecting
        :return:
        (bool) success
        (str) error_message
        """
        ok, request_object, error_message  = cls.get_multi_cluster_config()

        if not ok:
            return ok, error_message

        request_object.mc_config_state = MultiClusterConfigState.DISCONNECTING.value
        request_object.save()

        return ok, error_message

    @classmethod
    def reset_multi_cluster_config_request(cls) -> (bool, str):
        """
        set multi-cluster config request
        :return:
        (bool) success
        (str) error_message
        """
        ok, request_object, error_message  = cls.get_multi_cluster_config()

        if not ok:
            return ok, error_message

        request_object.mc_config_state = MultiClusterConfigState.NONE.value
        request_object.role = MultiClusterRole.NONE.value
        request_object.mc_connect_id = None
        request_object.remote_cluster_name = None
        request_object.save()

        return ok, error_message
