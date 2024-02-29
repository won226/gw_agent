import six
from repository.common.type import Metric
from repository.model.metric.cpu import CPUMetric
from repository.model.metric.memory import MemoryMetric
from repository.model.metric.network import NetworkMetric


class NodeMetric:
    """
    NodeMetric model class
    """
    MAX_KEEP_SECONDS = 60

    fields = {
        'kind': 'str',
        'name': 'str',
        'instance': 'str',  # node-exporter instance
        'cpu_metric': 'CPUMetric',
        'mem_metric': 'MemoryMetric',
        'net_metric': 'NetworkMetric'
    }

    def __init__(self, name):
        """
        NodeMetric()
        :param name: (str) node name(hostname)
        """
        self.kind = Metric.NODE_METRIC.value
        self.name = name
        self.instance = None

        # time-series metric
        self.cpu_metric = None
        self.mem_metric = None
        self.net_metric = None

    @classmethod
    def validate_dict(cls, _dict):
        """
        validate _dict
        """
        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict):
        """
        Returns the model object
        """
        cls.validate_dict(_dict)
        instance = cls(name=_dict['name'])
        for key, value in _dict.items():
            if key == 'cpu_metric':
                setattr(instance, key, CPUMetric.to_object(value))
            elif key == 'mem_metric':
                setattr(instance, key, MemoryMetric.to_object(value))
            elif key == 'net_metric':
                setattr(instance, key, NetworkMetric.to_object(value))
            else:
                setattr(instance, key, value)

        return instance

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in six.iteritems(self.fields):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind

    def get_name(self):
        """
        getter
        :return: (str) node's name
        """
        return self.name

    def set_instance(self, val):
        """
        setter
        :param val: (str) node-exporter instance (i.e., 10.244.0.73:9100)
        :return:
        """
        if val is None:
            raise ValueError('val is None')
        if type(val) is not str:
            raise TypeError('Invalid type for val({}). Must input str type as val'.format(type(val)))

        self.instance = val

    def get_instance(self):
        """
        getter
        :return:  (str) node-exporter instance (i.e., 10.244.0.73:9100)
        """
        return self.instance

    def set_cpu_metric(self, val):
        """
        setter
        :param val: (CPUMetric)
        :return:
        """

        if val is None:
            raise ValueError('val is None. Must input val as CPUMetric object')
        if type(val) != CPUMetric:
            raise TypeError('Invalid type for val({}) Must input val as CPUMetric object'.format(type(val)))
        self.cpu_metric = val

    def get_cpu_metric(self):
        """
        getter
        :return: (CPUMetric)
        """
        return self.cpu_metric

    def set_memory_metric(self, val):
        """
        setter
        :param val: (MemoryMetric)
        :return:
        """
        if val is None:
            raise ValueError('val is None. Must input val as MemoryMetric object')
        if type(val) != MemoryMetric:
            raise TypeError('Invalid type for val({}) Must input val as MemoryMetric object'.format(type(val)))
        self.mem_metric = val

    def get_memory_metric(self):
        """
        getter
        :return: (MemoryMetric)
        """
        return self.mem_metric

    def set_network_metric(self, val):
        """
        setter
        :param val: (NetworkMetric)
        :return:
        """
        if val is None:
            raise ValueError('val is None. Must input val as NetworkMetric object')
        if type(val) != NetworkMetric:
            raise TypeError('Invalid type for val({}) Must input val as NetworkMetric object'.format(type(val)))
        self.net_metric = val

    def get_network_metric(self):
        """
        getter
        :return: (NetworkMetric)
        """
        return self.net_metric