import six
from repository.common.type import Kubernetes


class ServicePort:
    fields = {
        'kind': 'str',
        'name': 'str',
        'port': 'str',
        'node_port': 'str',
        'target_port': 'str',
        'protocol': 'str',
    }

    def __init__(self, name):
        """
        ServicePort()
        :param name: (str) ; port name
        """
        self.kind = Kubernetes.SERVICE_PORT.value
        self.name = name
        self.port = 0
        self.node_port = 0
        self.protocol = None
        self.target_port = 0

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind

    def get_name(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.name

    def set_port(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None:
            val = '{}'.format(val)
        self.port = val

    def get_port(self):
        """
        getter
        :return: (str)
        """
        return self.port

    def set_node_port(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None:
            val = '{}'.format(val)

        self.node_port = val

    def get_node_port(self):
        """
        getter
        :return: (str)
        """
        return self.node_port

    def set_target_port(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None:
            val = '{}'.format(val)

        self.target_port = val

    def get_target_port(self):
        """
        getter
        :return: (str)
        """
        return self.target_port

    def set_protocol(self, val):
        """
        setter
        :return: (str) i.e., 'TCP', 'UDP'
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.protocol = val

    def get_protocol(self):
        """
        getter
        :return: (str) i.e., 'TCP', 'UDP'
        """
        return self.protocol

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

        instance = cls(_dict['name'])
        for key, value in _dict.items():
            setattr(instance, key, value)

        return instance
