import six
from repository.common.type import Metric
from utils.validate import Validator


class EndpointNetworkMetric:
    """
    MultiClusterMetric model class
    """
    buffer_size = 60

    fields = {
        'kind': 'str',
        'name': 'str',
        'latencies': 'list',    # latency list: [[(float)timestamp, (float)latency_ms],]
        'tx_bytes': 'list',     # tx byte list: [[(float)timestamp, (int)tx_byte],]
        'rx_bytes': 'list',     # tx byte list: [[(float)timestamp, (int)rx_byte],]
    }

    def __init__(self, name):
        """
        EndpointNetworkMetric()
        """
        self.kind = Metric.ENDPOINT_NETWORK_METRIC.value
        self.name = name
        self.latencies = []
        self.tx_bytes = []
        self.rx_bytes = []

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
        :return: (str) name
        """
        return self.name

    def set_latency(self, latency: float, timestamp: float):
        """
        set latency
        :param latency: (float) ms
        :param timestamp: (float) time.time()
        :return:
        """
        if timestamp is None or type(timestamp) != float:
            raise ValueError('Invalid timestamp(({}){}). '
                             'Must input float as timestamp'.format(type(timestamp), timestamp))

        if not Validator.is_float(latency):
            raise ValueError('Invalid latency type(({}){}).'
                             'Must input float as latency'.format(type(latency), latency))

        if len(self.latencies) >= self.buffer_size:
            # del last item
            del self.latencies[0]

        self.latencies.append([timestamp, latency])

    def get_latencies(self):
        """
        getter
        :return:
        (int): list([(float)timestamp, (float)latency_ms])
        """
        return self.latencies

    def set_tx_byte(self, tx_byte:int, timestamp:float):
        """
        set network TX byte
        :param tx_byte: (int) TX byte
        :param timestamp: (float) time.time()
        :return:
        """
        if tx_byte is None or type(tx_byte) != int:
            raise ValueError('Invalid tx_byte(({}){}). '
                             'Must input int as tx_byte'.format(type(tx_byte), tx_byte))
        if timestamp is None or type(timestamp) != float:
            raise ValueError('Invalid timestamp(({}){}). '
                             'Must input float as timestamp'.format(type(timestamp), timestamp))

        if len(self.tx_bytes) >= self.buffer_size:
            # del last item
            del self.tx_bytes[0]

        self.tx_bytes.append([timestamp, tx_byte])

    def set_rx_byte(self, rx_byte:int, timestamp:float):
        """
        set network RX byte
        :param rx_byte: (int) RX byte
        :param timestamp: (float) time.time()
        :return:
        """
        if rx_byte is None or type(rx_byte) != int:
            raise ValueError('Invalid rx_byte(({}){}). '
                             'Must input int as rx_byte'.format(type(rx_byte), rx_byte))
        if timestamp is None or type(timestamp) != float:
            raise ValueError('Invalid timestamp(({}){}). '
                             'Must input float as timestamp'.format(type(timestamp), timestamp))

        if len(self.rx_bytes) >= self.buffer_size:
            # del last item
            del self.rx_bytes[0]

        self.rx_bytes.append([timestamp, rx_byte])
