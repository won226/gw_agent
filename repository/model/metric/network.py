import six

from repository.common.type import Metric


class NetworkMetric:
    """
    NetworkMetric model class
    """

    fields = {
        'kind': 'kind',
        'device': 'str',
        'rx_bytes': 'list(list())', # [[int,int], [int,int], [int,int]]
        'tx_bytes': 'list(list())', # [[int,int], [int,int], [int,int]]
    }

    def __init__(self, device, rx_bytes, tx_bytes):
        """
        NetworkMetric()
        :param device: (str) device name('eth0')
        :param rx_bytes: (int) receive bytes
        :param tx_bytes: (int) send bytes
        """
        self.kind = Metric.NETWORK_METRIC.value
        self.device = device
        self.rx_bytes = rx_bytes
        self.tx_bytes = tx_bytes

    @classmethod
    def validate_dict(cls, _dict):
        """ validate _dict """
        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict):
        """
        Returns the model object
        """
        cls.validate_dict(_dict)
        return cls(device=_dict['device'],
                   rx_bytes=_dict['rx_bytes'],
                   tx_bytes=_dict['tx_bytes'])


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