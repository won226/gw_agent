import six
from repository.common.type import ConnectionStatus, NetStat, MultiClusterRole


class EndpointNetwork:
    """
    Multi-cluster connected endpoint model class
    """

    fields = {
        'kind': 'str',
        'name': 'str',  # cluster_id
        'role': 'str',  # network role ('Local', 'Remote')
        'status': 'str',  # endpoint status(i.e., 'connected' or 'error' or 'unavailable')
        'hostname': 'str', # endpoint hostname
        'public_ip': 'str',  # public ip(i.e., '211.237.16.76')
        'gateway_ip': 'str',  # gateway ip(i.e., '10.0.0.206')
        'service_cidr': 'str',  # service network(i.e., '10.55.0.0/16')
        'cluster_cidr': 'str',  # pod network(i.e., '10.244.0.0/16')
        'global_cidr': 'str',   # global cidr(i.e., '242.0.0.0/16')
        'status_message': 'str' # status message
    }

    def __init__(self, name):
        """
        MultiClusterNetwork()
        :param name: (str) cluster name created from center (i.e., west-cls)
        """
        self.kind = NetStat.ENDPOINT_NETWORK.value
        self.name = name
        self.role = MultiClusterRole.UNKNOWN
        self.status = ConnectionStatus.UNAVAILABLE.value
        self.status_message = None
        self.hostname = None
        self.public_ip = None
        self.gateway_ip = None
        self.service_cidr = None
        self.cluster_cidr = None
        self.global_cidr = None

    @classmethod
    def validate_dict(cls, _dict) -> None:
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

    def to_dict(self) -> dict:
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

    def get_name(self) -> str:
        """
        getter
        :return: (str) name
        """
        return self.name

    def set_status(self, val: str):
        """
        setter
        :param val: (str)
        :return:
        """
        status = ConnectionStatus.to_enum_str(val)

        if status == ConnectionStatus.UNKNOWN.value:
            raise TypeError('Invalid val. val={}' + val)

        self.status = status

    def get_status(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.status

    def set_status_message(self, val: str):
        """
        setter
        :param val: (str)
        :return:
        """
        self.status_message = val

    def get_status_message(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.status_message

    def set_hostname(self, val: str):
        """
        setter
        :param val: (str)
        :return:
        """
        self.hostname = val

    def get_hostname(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.hostname

    def set_role(self, val: str):
        """
        setter
        :param val: (MultiClusterRole(Enum)) LOCAL or REMOTE or UNKNOWN
        :return:
        """
        if not MultiClusterRole.validate(val):
            raise TypeError('Invalid Enum type(value={}). '
                            'Must input val as str type in MultiClusterRole(Enum)'.format(val))

        self.role = val

    def get_role(self) -> str:
        """
        getter
        :return: (MultiClusterRole(Enum)) LOCAL or REMOTE or UNKNOWN
        """
        return self.role

    def set_public_ip(self, val: str):
        """
        setter
        :param val: (str) public ip(i.e., '211.237.16.76'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.public_ip = val

    def get_public_ip(self) -> str:
        """
        getter
        :return: (str) public ip(i.e., '211.237.16.76')
        """
        return self.public_ip

    def set_gateway_ip(self, val: str):
        """
        setter
        :param val: (str) gateway ip(i.e., '10.0.0.206'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.gateway_ip = val

    def get_gateway_ip(self) -> str:
        """
        getter
        :return: (str) gateway ip(i.e., '10.0.0.206')
        """
        return self.gateway_ip

    def set_service_cidr(self, val: str):
        """
        setter
        :param val: (str) service network(i.e., '10.55.0.0/16'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.service_cidr = val

    def get_service_cidr(self) -> str:
        """
        getter
        :return: (str) service network(i.e., '10.55.0.0/16')
        """
        return self.service_cidr

    def set_cluster_cidr(self, val: str):
        """
        setter
        :param val: (str) pod network(i.e., '10.244.0.0/16'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))

        self.cluster_cidr = val

    def get_cluster_cidr(self) -> str:
        """
        getter
        :return: (str) pod network(i.e., '10.244.0.0/16')
        """
        return self.cluster_cidr

    def set_global_cidr(self, val: str):
        """
        setter
        :param val: (str) globalnet network(i.e., '10.244.0.0/16'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))

        self.global_cidr = val

    def get_global_cidr(self) -> str:
        """
        getter
        :return: (str) globalnet network(i.e., '10.244.0.0/16'); nullable
        """
        return self.global_cidr