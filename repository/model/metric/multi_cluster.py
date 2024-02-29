import six
from repository.common.type import Metric
from repository.model.metric.endpoint import EndpointNetworkMetric
from utils.validate import Validator


class MultiClusterMetric(object):
    """
    MultiClusterMetric model class
    """
    fields = {
        'kind': 'str',
        'endpoints': 'list(EndpointNetworkMetric)'
    }

    def __init__(self):
        """
        MultiClusterMetric()
        """
        self.kind = Metric.MULTI_CLUSTER_METRIC.value
        self.endpoints = []

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
        instance = cls()
        endpoints = []

        for key, value in _dict.items():
            if key == 'endpoints':
                for item in value:
                    endpoints.append(MultiClusterMetric.to_object(item))
                setattr(instance, key, endpoints)
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

    def _get_endpoint_index(self, val:str):
        """
        get endpoint index
        :param val: (str) EndpointNetwork.name (i.e., cluster_id)
        :return:
        """
        if len(self.endpoints) <= 0:
            return -1

        for index in range(0, len(self.endpoints)):
            if val == self.endpoints[index].get_name():
                return index
        return -1

    def delete_all_endpoints(self):
        """
        delete all endpoints
        :return:
        """
        for i in range(0, len(self.endpoints)):
            del self.endpoints[i]

        self.endpoints = None

    def delete_endpoint(self, val:str):
        """
        delete endpoint
        :param val: (str) name
        :return:
        """
        if not Validator.is_str(val):
            raise ValueError('Invalid val(type={}) type'.format(type(val)))

        index = self._get_endpoint_index(val)

        if index >= 0:
            del self.endpoints[index]

    def set_endpoint_latency(self, name:str, latency:float, timestamp:float):
        """
        set endpoint latency
        :param name: (str) endpoint network name(cluster_id)
        :param latency: (float) unit: ms
        :param timestamp: (float) time.time()
        :return:
        """
        index = self._get_endpoint_index(name)

        if index < 0:
            endpoint = EndpointNetworkMetric(name)
            endpoint.set_latency(latency=latency, timestamp=timestamp)
            self.endpoints.append(endpoint)

        self.endpoints[index].set_latency(latency=latency, timestamp=timestamp)

    def get_endpoint_latencies(self, name:str):
        """
        getter
        :param name:  (str) endpoint network name(cluster_id)
        :return:
        [[(float)timestamp, (float)latency],]
        """
        index = self._get_endpoint_index(name)
        if index >= 0:
            return self.endpoints[index].get_latency()

        return None

    def set_endpoint_tx_byte(self, name:str, tx_byte:int, timestamp:float):
        """
        set endpoint network TX byte
        :param name: (str) endpoint network name(cluster_id)
        :param tx_byte: (int) TX byte
        :param timestamp: (float) time.time()
        :return:
        """
        index = self._get_endpoint_index(name)

        if index < 0:
            endpoint = EndpointNetworkMetric(name)
            endpoint.set_tx_byte(tx_byte=tx_byte, timestamp=timestamp)
            self.endpoints.append(endpoint)
            return

        self.endpoints[index].set_tx_byte(tx_byte=tx_byte, timestamp=timestamp)

    def set_endpoint_rx_byte(self, name: str, rx_byte: int, timestamp: float):
        """
        set endpoint network RX byte
        :param name: (str) endpoint network name(cluster_id)
        :param rx_byte: (int) RX byte
        :param timestamp: (float) time.time()
        :return:
        """
        index = self._get_endpoint_index(name)

        if index < 0:
            endpoint = EndpointNetworkMetric(name)
            endpoint.set_rx_byte(rx_byte=rx_byte, timestamp=timestamp)
            self.endpoints.append(endpoint)

        self.endpoints[index].set_rx_byte(rx_byte=rx_byte, timestamp=timestamp)
