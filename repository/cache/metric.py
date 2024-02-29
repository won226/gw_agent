from gw_agent.settings import get_logger
from repository.model.metric.cpu import CPUMetric
from repository.model.metric.memory import MemoryMetric
from repository.model.metric.multi_cluster import MultiClusterMetric
from repository.model.metric.network import NetworkMetric
from repository.model.metric.node import NodeMetric


class MetricRepository(object):
    """
    Cluster Metric management class
    """
    _logger = None
    _nodes = []
    _mc_network = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._logger = get_logger(__name__)
            cls._instance._mc_network = MultiClusterMetric()
        return cls._instance

    def clear(self):
        """
        clear entire cache
        :return:
        """
        self._nodes = []
        self._mc_network.delete_all_endpoints()

    def _find_node_index(self, name:str):
        """
        find node index for name
        :param name: (str) node name
        :return: (int) registered node matrix index, not found: (int) -1, found: [0,]
        """
        index = -1

        for i in range(0, len(self._nodes)):
            if self._nodes[i].name == name:
                index = i
                break

        return index

    def set_node_object(self, obj:NodeMetric):
        """
        set node object
        :param obj: (NodeMetric)
        :return:
        """
        if type(obj) != NodeMetric:
            raise TypeError('Invalid input type. Must input NodeMetric as obj')
        if obj.name is None:
            raise ValueError('Invalid input value. NodeMetric.name is None')

        index = self._find_node_index(obj.name)

        if index < 0:
            self._nodes.append(obj)
        else:
            self._nodes[index].cpu_metric = obj.cpu_metric
            self._nodes[index].mem_metric = obj.mem_metric
            self._nodes[index].net_metric = obj.net_metric

    def set_node(self, name:str):
        """
        add node metric
        :return: (NodeMetric)
        """
        index = self._find_node_index(name)
        node = NodeMetric(name=name)

        if index < 0:
            self._nodes.append(node)

        return node

    def delete_node(self, name:str):
        """
        delete node metric
        :param name: (str) node name
        :return:
        """
        index = self._find_node_index(name)

        if index > 0:
            del self._nodes[index]

    def get_nodes(self):
        """
        get node metric object list
        :return: (list[NodeMetric])
        """
        return self._nodes

    def get_node(self, name:str):
        """
        get node metric for named node
        :param name: (str) node name
        :return: (NodeMetric); None - not exist
        """
        index = self._find_node_index(name)
        if index < 0:
            return None

        return self._nodes[index]

    def set_node_cpu_metric(self, name:str, obj:CPUMetric):
        """
        set node cpu metric
        :param name: (str) node name
        :param obj: (CPUMetric)
        :return:
        """
        index = self._find_node_index(name)
        if index < 0:
            raise LookupError('Not exist node name. name={}'.format(name))

        self._nodes[index].set_cpu_usage(obj)

    def set_node_mem_metric(self, name:str, obj:MemoryMetric):
        """
        set node mem metric
        :param name: (str) node name
        :param obj: (MemoryMetric)
        :return:
        """
        index = self._find_node_index(name)
        if index < 0:
            raise LookupError('Not exist node name. name={}'.format(name))

        self._nodes[index].set_mem_usage(obj)

    def set_node_net_metric(self, name:str, obj:NetworkMetric):
        """
        set node net metric
        :param name: (str) node name
        :param obj: (NetworkMetric)
        :return:
        """
        index = self._find_node_index(name)
        if index < 0:
            raise LookupError('Not exist node name. name={}'.format(name))

        self._nodes[index].set_net_usage(obj)

    def get_mc_network(self):
        """
        get mc network metric
        :return:
        """
        return self._mc_network

    def delete_mc_network(self):
        """
        delete mc network metric
        :return:
        """
        self._mc_network = None

    def delete_endpoint(self, name:str):
        """
        delete endpoint
        :param name: (str) endpoint network name(cluster_id)
        :return:
        """
        self._mc_network.delete_endpoint(name)

    def set_mc_network_latency(self, name:str, latency:float, timestamp:float):
        """
        set multi cluster latency
        :param name: (str) endpoint network name(cluster_id)
        :param latency: (int) unit: ms
        :param timestamp: (float) time.time()
        :return:
        """
        self._mc_network.set_endpoint_latency(name=name, latency=latency, timestamp=timestamp)

    def set_mc_network_tx_byte(self, name:str, tx_byte:int, timestamp:float):
        """
        set multi cluster TX byte
        :param name: (str) endpoint network name(cluster_id)
        :param tx_byte: (int) TX byte
        :param timestamp: (float) timestamp: time.time()
        :return:
        """
        self._mc_network.set_endpoint_tx_byte(name=name, tx_byte=tx_byte, timestamp=timestamp)

    def set_mc_network_rx_byte(self, name:str, timestamp:int, rx_byte:float):
        """
        set multi cluster RX byte
        :param name: (str) endpoint network name(cluster_id)
        :param timestamp: (int) timestamp: time.time()
        :param rx_byte: (float) RX byte
        :return:
        """
        self._mc_network.set_endpoint_rx_byte(name=name, rx_byte=rx_byte, timestamp=timestamp)
