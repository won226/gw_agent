import six
from repository.common.type import Kubernetes


class Condition:
    # Namespace: []
    # Node: [ 'DiskPressure', 'MemoryPressure', 'NetworkUnavailable', 'PIDPressure', 'Ready' ]
    # Pod: [ 'ContainersReady', 'Initialized', 'PodScheduled', 'Ready' ]
    # Daemonset: []
    # Deployment: [ 'Available', 'Progressing' ]
    # Service: []

    fields = {
        'kind': 'str',
        'condition': 'str',
        'status': 'str',
        'message': 'str',
        'updated': 'str',
    }

    def __init__(self):
        """
        Condition()
        """
        self.kind = Kubernetes.CONDITION.value
        self.condition = None
        self.status = False
        self.message = None
        self.updated = None

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind

    def set_condition(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val(value={}). Must input val as str type'.format(val))
        self.condition = val

    def get_condition(self):
        """
        getter
        :return:
        """
        return self.condition

    @staticmethod
    def bool_to_str(val):
        if val is True:
            return "True"
        elif val is False:
            return "False"
        else:
            raise ValueError('Invalid val({}). Must input boolean type.')

    def set_status(self, val):
        """
        setter
        :param val: (str) 'True' or 'False'
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.status = val

    def get_status(self):
        """
        getter
        :return: (str)
        """
        return self.status

    def set_message(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.message = val

    def get_message(self):
        """
        getter
        :return:
        """
        return self.message

    def set_updated(self, val):
        """
        setter
        :param val: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.updated = val

    def get_update(self):
        """
        getter
        :return:
        """
        return self.updated

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
