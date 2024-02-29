from typing import List

from cluster.data_access_object import ClusterDAO
from gw_agent import settings
from repository.common.type import ConnectionStatus, MultiClusterRole, ClusterSessionStatus, \
    ClusterNetworkConnectionStatus, CommandResult
from repository.model.netstat.center import CenterNetwork
from repository.model.netstat.endpoint import EndpointNetwork
from repository.model.netstat.multi_cluster import MultiClusterNetwork
from repository.model.netstat.service import MultiClusterService, ServiceExport, ServiceImport


class NetworkStatusRepository:
    """
    Network Status repository for caching center, cluster, multi-cluster network connection
    """
    _logger = None
    _mc_network_status_watcher = None
    _mc_network_metric_watcher = None
    _mc_network = None
    _center_network = None
    _mc_network_service = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._mc_network_service = MultiClusterService()
            cls._instance._logger = settings.get_logger(__name__)

        return cls._instance

    def clear(self):
        """
        clear entire cache
        :return:
        """
        self._mc_network = None
        self._center_network = None

    def clear_mc_network(self):
        """
        clear multi-cluster network
        :return:
        """
        self._mc_network = None

    def set_center_network(self, name: str):
        """
        set center network status
        :param name: (str) center network name(http access url)
        :return:
        """
        if self._center_network is None:
            self._center_network = CenterNetwork(name=name)
            return

        if self._center_network.name != name:
            self._center_network = CenterNetwork(name=name)
            return

    def set_center_network_object(self, val: CenterNetwork):
        """
        set center network object
        :param val: (CenterNetwork)
        :return:
        """
        if type(val) != CenterNetwork:
            raise TypeError('Invalid input type(val={}). Must input CenterNetwork as obj'.format(val))

        if val.name is None:
            raise ValueError('Invalid input value. CenterNetwork.name is None')

        if self._center_network.name != val.name:
            self._center_network = val

        else:
            self._center_network.set_network_connection_status(val.get_network_connection_status())
            self._center_network.set_cluster_session_status(val.get_cluster_session_status())
            self._center_network.set_http(val.get_http())
            self._center_network.set_https(val.get_https())
            self._center_network.set_amqp(val.get_amqp())

    def get_center_network(self) -> CenterNetwork:
        """
        get center network object
        :return: (CenterNetwork) center network status object
        """
        return self._center_network

    def get_center_network_name(self) -> str:
        """
        get center network name
        :return:
        """
        if self._center_network is None:
            return None

        if self._center_network.name is None:
            return None

        return self._center_network.name

    def get_cluster_session_status(self) -> str:
        """
        get center's cluster session status
        :return: (ClusterSessionStatus(Enum))
        """
        if self._center_network is None:
            return ClusterSessionStatus.UNAVAILABLE.value

        return self._center_network.get_cluster_session_status()

    def set_cluster_session_status(self, name: str, status: str):
        """
        set center's cluster session status
        :param name: (str) gedge-center access '/' url(http or https)
        :param status: (str) ClusterSessionStatus(Enum)
        :return:
        """
        if self._center_network is None:
            raise LookupError('Not exist center network. name={}'.format(name))

        if self._center_network.name != name:
            raise LookupError('Not exist center network. name={}'.format(name))

        self._center_network.set_cluster_session_status(status)

    def get_center_network_connection_status(self) -> str:
        """
        get center's cluster session status
        :return: (ClusterNetworkConnectionStatus(Enum))
        """
        if self._center_network is None:
            return ClusterNetworkConnectionStatus.UNAVAILABLE.value

        return self._center_network.get_network_connection_status()

    def set_center_network_connection_status(self, name: str, status: str):
        """
        set center network connection status
        :param name: (str) gedge-center access '/' url(http or https)
        :param status: (str) NetworkConnectionStatus(Enum)
        :return:
        """
        if self._center_network is None:
            raise LookupError('Not exist center network. name={}'.format(name))

        if self._center_network.name != name:
            raise LookupError('Not exist center network. name={}'.format(name))

        self._center_network.set_network_connection_status(status)

    def set_center_network_http(self, name: str, url: str):
        """
        set center network http access url
        :param name: (str) gedge-center access '/' url(http or https)
        :param url: (str) http access '/' url
        :return:
        """
        if self._center_network is None:
            raise LookupError('Not exist center network. name={}'.format(name))

        if self._center_network.name != name:
            raise LookupError('Not exist center network. name={}'.format(name))

        self._center_network.set_http(url)

    def set_center_network_https(self, name: str, url: str):
        """
        set center network https access url
        :param name: (str) gedge-center access '/' url(http or https)
        :param url: (str) https access '/' url
        :return:
        """
        if self._center_network is None:
            raise LookupError('Not exist center network. name={}'.format(name))

        if self._center_network.name != name:
            raise LookupError('Not exist center network. name={}'.format(name))

        self._center_network.set_https(url)

    def set_center_network_ampq(self, name: str, url: str):
        """
        set center network amqp access url
        :param name: (str) gedge-center access '/' url(http or https)
        :param url: (str) amqp access url
        :return:
        """
        if self._center_network is None:
            raise LookupError('Not exist center network. name={}'.format(name))

        if self._center_network.name != name:
            raise LookupError('Not exist center network. name={}'.format(name))

        self._center_network.set_amqp(url)

    def set_center_network_token(self, name: str, token: str):
        """
        set center network http/https access token
        :param name: (str) gedge-center access '/' url(http or https)
        :param token: (str) http/https access token
        :return:
        """
        if self._center_network is None:
            raise LookupError('Not exist center network. name={}'.format(name))

        if self._center_network.name != name:
            raise LookupError('Not exist center network. name={}'.format(name))

        self._center_network.set_token(token)

    def set_mc_network_status_watcher(self, watcher):
        """
        set multi-cluster network status watcher
        :param watcher: (cluster.watcher.networks.NetworkWatcher)
        :return:
        """
        self._mc_network_status_watcher = watcher

    def set_mc_network_metric_watcher(self, watcher):
        """
        set multi-cluster network metric watcher
        :param watcher: (cluster.watcher.metrics.MetricWatcher)
        :return:
        """
        self._mc_network_metric_watcher = watcher

    def start_mc_network_monitor(self) -> bool:
        """
        start multi-cluster network status and metric monitor
        :return:
        (bool) True - success, False - fail
        """
        # start multi-cluster network status monitor
        self._logger.debug('Start multi-cluster network status monitor.')

        if self._mc_network_status_watcher:
            self._mc_network_status_watcher.start_multi_cluster_network_monitor()

        else:
            self._logger.error('Fail to start multi-cluster network status monitor, caused by '
                               '_mc_network_status_watcher is None.')

        # start multi-cluster network metric monitor
        self._logger.debug('Start multi-cluster network metric monitor.')

        if self._mc_network_metric_watcher:
            self._mc_network_metric_watcher.start_multi_cluster_network_metric_monitor()

        else:
            self._logger.error('Fail to start multi-cluster network metric monitor, caused by '
                               '_mc_network_metric_watcher is None.')
            return False

        return True

    def stop_mc_network_monitor(self):
        """
        stop multi-cluster network status and metric monitor
        :return:
        """
        # stop multi-cluster network status monitor
        self._logger.info('Stop multi-cluster network status monitor.')

        if self._mc_network_status_watcher:
            self._mc_network_status_watcher.stop_multi_cluster_network_monitor()

        else:
            self._logger.error('Fail to stop multi-cluster network status monitor, caused by '
                               '_mc_network_status_watcher is None')
            return False

        # stop multi-cluster network metric monitor
        self._logger.debug('Stop multi-cluster network metric monitor.')

        if self._mc_network_metric_watcher:
            self._mc_network_metric_watcher.stop_multi_cluster_network_metric_monitor()

        else:
            self._logger.error('Fail to stop multi-cluster network metric monitor, caused by '
                               '_mc_network_metric_watcher is None')
            return False

        return True

    def get_mc_network(self) -> MultiClusterNetwork:
        """
        get multi cluster status object
        :return: (MultiClusterNetwork) mc network status object
        """
        return self._mc_network

    def get_mc_network_name(self) -> str:
        """
        get mc network name
        :return: (str)
        """
        if self._mc_network is None:
            return None

        if self._mc_network.name is None:
            return None

        return self._mc_network.name

    def get_remote_mc_network_name(self) -> str:
        """
        get remote multi-cluster cluster_id
        :return:
        """
        ok, remote_cluster_name, error_message = ClusterDAO.get_remote_cluster_name()

        if not ok:
            self._logger.error('Failed in ClusterDAO.get_remote_cluster_name(), caused by ' + error_message)
            return None

        return remote_cluster_name

    def set_mc_network(self, obj: MultiClusterNetwork):
        """
        set multi cluster status
        :param obj: (MultiClusterNetwork)
        :return:
        """
        if obj is None:
            raise ValueError('obj is None')

        if type(obj) != MultiClusterNetwork:
            raise ValueError('Invalid obj(type={}) type. Must input MultiClusterNetwork type as val'.format(type(obj)))

        self._mc_network = obj

    def set_mc_network_broker_role(self, role: str):
        """
        set multi cluster status
        :param role: MultiClusterRole.LOCAL.value or ConnectionStatus.REMOTE.value
        :return:
        """
        if self._mc_network is None:
            return

        self._mc_network.set_broker_role(role)

    def get_mc_network_broker_role(self) -> str:
        """
        get multi cluster network role
        :return:
        """
        if self._mc_network is None:
            return MultiClusterRole.UNKNOWN.value

        return self._mc_network.get_broker_role()

    def set_mc_network_globalnet(self, enabled: bool):
        """
        set multi cluster globalnet enabled
        :param enabled: (bool) True - enabled, False - disabled
        :return:
        """
        self._mc_network.set_globalnet(enabled)

    def set_mc_network_global_cidr(self, val: str):
        """
        set multi cluster global cidr
        :param val: (str) global vpn(i.e., '244.0.0.0/8')
        :return:
        """
        self._mc_network.set_global_cidr(val)

    def set_mc_network_cable_driver(self, val: str):
        """
        set multi cluster global cidr
        :param val: (str) tunneling driver(i.e., 'wireguard' or 'libswan' or 'ipsec')
        :return:
        """
        self._mc_network.set_cable_driver(val)

    def set_mc_network_endpoints(self, endpoints: List[EndpointNetwork]):
        """
        set multi cluster endpoints
        :param endpoints: (List[EndpointNetwork])
        :return:
        """
        return self._mc_network.set_endpoints(endpoints)

    def get_mc_network_endpoints(self) -> List[EndpointNetwork]:
        """
        get multi cluster endpoints
        :return:
        """
        return self._mc_network.get_endpoints()

    def get_mc_network_connection_status(self) -> str:
        """
        get mc network connection status
        :return:
        (ConnectionStatus(Enum)) connection status
        """
        if self._mc_network is None:
            return ConnectionStatus.UNAVAILABLE.value

        endpoints = self._mc_network.get_remote_endpoints()

        if len(endpoints) <= 0:
            return ConnectionStatus.UNAVAILABLE.value

        return endpoints[0].get_status()

    def is_mc_network_connected(self) -> bool:
        """
        check whether multi-cluster network is connected each other
        :return:
        """
        if self._mc_network is None:
            return False

        endpoints = self._mc_network.get_remote_endpoints()

        if not endpoints or len(endpoints) <= 0:
            return False

        self._logger.debug('remote endpoints: {}'.format(len(endpoints)))

        if endpoints[0].get_status() == ConnectionStatus.CONNECTED.value:
            self._logger.debug('submariner gateway status: connected.')
            return True

        self._logger.debug('submariner gateway status: {}'.format(endpoints[0].get_status()))

        return False

    def get_mc_network_service(self) -> MultiClusterService:
        """
        get multi cluster service(exports, imports)
        :return:
        """
        return self._mc_network_service

    def set_mc_network_service_exports(self, val: List[ServiceExport]):
        """
        synchronize multi cluster service exports
        :param val: (list(ServiceExport))
        :return:
        """
        return self._mc_network_service.set_service_exports(val)

    def get_mc_network_service_exports(self) -> List[ServiceExport]:
        """
        get multi cluster service exports
        :return: (list(ServiceExport))
        """
        return self._mc_network_service.get_service_exports()

    def get_mc_network_service_imports(self) -> List[ServiceImport]:
        """
        get multi cluster service exports
        :return: (list(ServiceImport))
        """
        return self._mc_network_service.get_service_imports()

    def set_mc_network_service_imports(self, val: List[ServiceImport]):
        """
        synchronize multi cluster service imports
        :param val: (list(ServiceImport)
        :return:
        """
        return self._mc_network_service.set_service_imports(val)

    def is_service_exported(self, namespace: str, name: str):
        """
        check whether service is exported or not
        :param namespace: (str) namespace
        :param name: (str) service name
        :return:
        """
        exports = self.get_mc_network_service_exports()

        for item in exports:
            if item.get_name() == name and item.get_namespace() == namespace:
                return True

        return False

    def is_service_imported(self, namespace: str, name: str) -> bool:
        """
        check whether service is imported or not
        :param namespace: (str) namespace
        :param name: (str) service name
        :return:
        """

        imports = self.get_mc_network_service_imports()

        for item in imports:
            if item.get_name() == name and item.get_namespace() == namespace:
                return True

        return False

    def get_imported_service(self, namespace, name) -> ServiceImport:
        """
        get imported service for namespace and name
        :param namespace: (str) namespace
        :param name: (str) name
        :return: (ServiceImport)
        """
        imports = self.get_mc_network_service_imports()

        for item in imports:
            if item.get_name() == name and item.get_namespace() == namespace:
                return item

        return None
