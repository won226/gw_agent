from typing import List

import six

from repository.common.type import Kubernetes, ActiveStatus
from repository.model.k8s.condition import Condition


class DaemonSet:
    """
    DaemonSet model class
    - unit test:
      serialize test: success
      deserialize: success
    """

    fields = {
        'kind': 'str',
        'name': 'str',
        'namespace': 'str',
        'state': 'str',
        'images': 'list[str]',
        'desired': 'int',
        'current': 'int',
        'ready': 'int',
        'conditions': 'list[Condition]',
        'selector': 'list[str]',
        'stime': 'str',
    }

    def __init__(self, name):
        """
        DaemonSet()
        :param name: (str)
        """
        self.kind = Kubernetes.DAEMONSET.value
        self.name = name
        self.namespace = None
        self.state = ActiveStatus.UNKNOWN.value
        self.images = []
        self.desired = 0
        self.current = 0
        self.ready = 0
        self.selector = []
        self.conditions = []
        self.stime = None

    def get_name(self) -> str:
        """
        getter
        :return: (str) daemonset name
        """
        return self.name

    def get_kind(self) -> str:
        """
        getter
        :return: (str) resource kind
        """
        return self.kind

    def set_namespace(self, val: str):
        """
        setter
        :param val: (str) namespace; not null
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val(value={}). Must input val as str type'.format(val))
        self.namespace = val

    def get_namespace(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.namespace

    def set_state(self, val: str):
        """
        setter
        :param val: (str) in ActiveStatus(Enum)
        :return:
        """
        if not ActiveStatus.validate(val):
            raise TypeError('Invalid val type({}). Must input val as str type in NodeStatus(Enum)'.format(type(val)))
        self.state = val

    def get_state(self) -> str:
        """
        getter
        :return: (str) in ActiveStatus(Enum)
        """
        return self.state

    def set_images(self, val: List[str]):
        """
        setter
        :param val: (list[str])
        :return:
        """
        if val is None:
            raise TypeError('Invalid type for val({}). Must input val as list[str] type'.format(type(val)))
        if type(val) != list:
            raise TypeError('Invalid type for val({}). Must input val as list[str] type'.format(type(val)))
        for item in val:
            if type(item) != str:
                raise TypeError('Invalid type for val[i]({}). Must input val[i] as str type'.format(type(item)))
        self.images = val

    def get_images(self) -> List[str]:
        """
        getter
        :return: (list[str])
        """
        return self.images

    def set_desired(self, val: int):
        """
        setter
        :param val: (int)
        :return:
        """
        if type(val) != int:
            raise TypeError('Invalid type for val({}). Must input val as int type'.format(type(val)))
        self.desired = val

    def get_desired(self) -> int:
        """
        getter
        :return: (int)
        """
        return self.desired

    def set_current(self, val: int):
        """
        setter
        :param val: (int)
        :return:
        """
        if type(val) != int:
            raise TypeError('Invalid type for val({}). Must input val as int type'.format(type(val)))
        self.current = val

    def get_current(self) -> int:
        """
        getter
        :return: (int)
        """
        return self.current

    def set_ready(self, val: int):
        """
        setter
        :param val: (int)
        :return:
        """
        if type(val) != int:
            raise TypeError('Invalid type for val({}). Must input val as int type'.format(type(val)))
        self.ready = val

    def get_ready(self) -> int:
        """
        getter
        :return: (int)
        """
        return self.ready

    def set_selector(self, val: List[str]):
        """
        setter
        :return: (list[str])
        """
        if val is None:
            raise TypeError('Invalid type for val({}). Must input val as list[str] type'.format(type(val)))
        if type(val) != list:
            raise TypeError('Invalid type for val({}). Must input val as list[str] type'.format(type(val)))
        for item in val:
            if type(item) != str:
                raise TypeError('Invalid type for val[i]({}). Must input val[i] as str type'.format(type(item)))
        self.selector = val

    def get_selector(self) -> List[str]:
        """
        getter
        :return: (list[str])
        """
        return self.selector

    def set_conditions(self, val: List[Condition]):
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

    def get_conditions(self) -> List[Condition]:
        """
        getter
        :return: (list[Condition])
        """
        return self.conditions

    def set_stime(self, val: str):
        """
        setter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.stime = val

    def get_stime(self) -> str:
        """
        getter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        return self.stime

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

    @staticmethod
    def validate_dict(_dict: dict):
        """
        validate _dict
        """
        for key in _dict.keys():
            if key not in DaemonSet.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict: dict) -> object:
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

    def _find_condition_index(self, condition: str) -> int:
        """
        find index for condition
        :param condition: (str)
        :return:
        """

        for index in range(0, len(self.conditions)):
            if self.conditions[index].condition == condition:
                return index

        return -1

    def update_condition(self,
                         condition: str,
                         status: bool,
                         updated: str,
                         message: str) -> bool:
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
