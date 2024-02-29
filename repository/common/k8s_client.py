from kubernetes import client, config
from gw_agent import settings
from gw_agent.settings import get_logger


# API reference
# https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md
class Connector(object):
    """
    kubernetes API global
    """

    _core_v1_api = None                # CoreApi
    _app_v1_api = None                 # AppsApi
    _node_v1_api = None                # NodeV1alpha1Api, NodeV1beta1Api
    _events_v1_api = None              # EventsApi, EventsV1beta1Api
    _custom_objects_api = None
    _crd_list_v1_api = None
    _authentication_v1_api = None      # AuthenticationApi
    _authorization_v1_api = None       # AuthorizationApi
    _certificates_v1_api = None        # CertificatesApi
    _rbac_authorization_v1_api = None  # RbacAuthorizationApi
    _networking_v1_api = None          # NetworkingApi
    _logger = None


    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._connect()
            cls._instance._logger = get_logger(__name__)

        return cls._instance

    def _connect(self):
        """
        connect to kube-api-server
        :return:
        """
        config.load_kube_config(config_file=settings.KUBECONFIG_FILE)
        self._core_v1_api = client.CoreV1Api()
        self._app_v1_api = client.AppsV1Api()
        self._node_v1_api = client.NodeV1Api()
        self._custom_objects_api = client.CustomObjectsApi()
        self._events_v1_api = client.EventsV1Api()

    def reconnect(self):
        self._connect()

    def core_v1_api(self):
        return self._core_v1_api

    def app_v1_api(self):
        return self._app_v1_api

    def node_v1_api(self):
        return self._node_v1_api

    def custom_objects_api(self):
        return self._custom_objects_api

    def events_v1_api(self):
        return self._events_v1_api