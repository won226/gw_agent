import six
from repository.common.type import Kubernetes, ActiveStatus
from repository.model.k8s.condition import Condition


class Namespace:
    """
    Namespace model class
    - unit test:
      serialize test: success
      deserialize: success
    """

    fields = {
        'kind': 'str',
        'name': 'str',
        'state': 'str',
        'conditions': 'list[Condition]',
        'stime': 'str',
    }

    def __init__(self, name):
        """
        Namespace()
        :param name: (str)
        """
        self.kind = Kubernetes.NAMESPACE.value
        self.name = name
        self.state = ActiveStatus.UNKNOWN.value
        self.conditions = []
        self.stime = None

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind

    def get_name(self):
        """
        getter
        :return: (str) namespace's name
        """
        return self.name

    def set_state(self, val):
        """
        setter
        :param val: (str) in ActiveStatus(Enum)
        :return:
        """
        if not ActiveStatus.validate(val):
            raise TypeError('Invalid Enum type(value={}). '
                            'Must input val as str type in NodeStatus(Enum)'.format(val))
        self.state = val

    def get_state(self):
        """
        getter
        :return: (str) in ActiveStatus(Enum)
        """
        return self.state

    def set_conditions(self, val):
        """
        setter
        :param val: (list[Condition])
        :return:
        """
        if val is None:
            raise TypeError('val is None. Must input val as list[Condition] type')
        if type(val) != list:
            raise TypeError('Invalid val type({}). Must input val as list[Condition] type'.format(type(val)))
        for item in val:
            if type(item) != Condition:
                raise TypeError('Invalid val type({}). Must input val as list[Condition] type'.format(type(item)))
        self.conditions = val

    def get_conditions(self):
        """
        getter
        :return: (list[Condition])
        """
        return self.conditions

    def set_stime(self, val):
        """
        setter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.stime = val

    def get_stime(self):
        """
        getter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        return self.stime

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
        """ Returns the model object """
        cls.validate_dict(_dict)

        instance = cls(name=_dict['name'])
        conditions = []

        for key, value in _dict.items():
            if key == 'conditions':
                for item in value:  # list(Condition)
                    conditions.append(Condition.to_object(item))
                setattr(instance, key, conditions)
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

    def _find_condition_index(self, condition):
        """
        find index for condition
        :param condition: (str)
        :return:
        """

        for index in range(0, len(self.conditions)):
            if self.conditions[index].condition == condition:
                return index

        return -1

    def update_condition(self, condition, status, updated, message):
        """
        update condition
        :param condition: (str)
        :param status: (bool)
        :param updated: (str) datetime format('%Y-%m-%d %H:%M:%S')
        :param message: (str)
        :return: (bool) True - updated, False - not updated
        """
        index = self._find_condition_index(condition)
        if index > 0:
            if self.conditions[index].status != status or \
                self.conditions[index].message != message:
                self.conditions[index].status = status
                self.conditions[index].updated = updated
                self.conditions[index].message = message
                return True
            else:
                return False

        obj = Condition()
        obj.set_condition(condition)
        obj.set_status(status)
        obj.set_message(message)
        obj.set_updated(updated)
        self.conditions.append(obj)

        return True