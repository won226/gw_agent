import six
from repository.model.k8s.condition import Condition
from repository.common.type import Kubernetes, NodeStatus, ActiveStatus


class Node:
    """
    Node model class
    - unit test:
      serialize test: success
      deserialize: success
    """
    fields = {
        'kind': 'str',
        'name': 'str',
        'state': 'str',
        'role': 'str',
        'labels': 'list[str]',
        'taints': 'list[str]',
        'k8s_version': 'str',
        'os': 'str',
        'kernel_version': 'str',
        'iface': 'str',
        'ip': 'str',
        'number_of_cpu': 'str',
        'ram_size': 'str',
        'max_pods': 'str',
        'conditions': 'list[Condition]',
        'stime': 'str',
    }

    def __init__(self, name):
        """
        Node()
        :param name: (str)
        """
        # attributes
        self.kind = Kubernetes.NODE.value
        self.stime = None
        self.name = name
        self.state = ActiveStatus.UNKNOWN.value
        self.role = 'Worker'
        self.labels = []
        self.taints = []
        self.k8s_version = None
        self.os = None
        self.kernel_version = None
        self.iface = None
        self.ip = None
        self.number_of_cpu = None
        self.ram_size = None
        self.max_pods = None
        self.conditions = []

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

    def set_state(self, val):
        """
        setter
        :param val: (str) in ActiveStatus(Enum)
        :return:
        """
        if not ActiveStatus.validate(val):
            raise TypeError('Invalid Enum type(value={}). Must input val as str type in NodeStatus(Enum)'.format(val))
        self.state = val

    def get_state(self):
        """
        getter
        :return: (str) in NodeStatus(Enum)
        """
        return self.state

    def set_role(self, val):
        """
        setter
        :param val: (str) 'Worker' or 'Master'
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        if val != 'Worker' and val != 'Master':
            raise ValueError('Invalid value for val. Must input \'Worker\' or \'Master\'')
        self.role = val

    def get_role(self):
        """
        getter
        :return: (str)
        """
        return self.role

    def set_labels(self, val):
        """
        setter
        :param val: (list[str])
        :return:
        """
        if val is None:
            raise TypeError('Invalid type for val(None). Must input val as list[str] type')
        if type(val) != list:
            raise TypeError('Invalid type for val({}). Must input val as list[str] type'.format(type(val)))
        for item in val:
            if type(item) != str:
                raise TypeError('Invalid type for val[i]({}). Must input val[i] as str type'.format(type(item)))
        self.labels = val

    def get_labels(self):
        """
        getter
        :return: (list[str])
        """
        return self.labels

    def set_taints(self, val):
        """
        setter
        :param val: (list[str])
        :return:
        """
        if val is None:
            raise TypeError('Invalid type for val(None). Must input val as list[str] type')
        if type(val) != list:
            raise TypeError('Invalid type for val({}). Must input val as list[str] type'.format(type(val)))
        for item in val:
            if type(item) != str:
                raise TypeError('Invalid type for val[i]({}). Must input val[i] as str type'.format(type(item)))
        self.taints = val

    def get_taints(self):
        """
        getter
        :return: (list[str])
        """
        return self.taints

    def set_k8s_version(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.k8s_version = val

    def get_k8s_version(self):
        """
        getter
        :return: (str)
        """
        return self.k8s_version

    def set_kernel_version(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.kernel_version = val

    def get_kernel_version(self):
        """
        getter
        :return: (str)
        """
        return self.kernel_version

    def set_os(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.os = val

    def get_os(self):
        """
        getter
        :return: (str)
        """
        return self.os

    def set_ip(self, val):
        """
        setter
        :param val: (str) node ip address
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.ip = val

    def get_ip(self):
        """
        getter
        :return: (str) node ip address; nullable
        """
        return self.ip

    def set_number_of_cpu(self, val):
        """
        setter
        :param val: (str) number_of_cpu
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.number_of_cpu = val

    def get_number_of_cpu(self):
        """
        getter
        :return: (str) number_of_cpu
        """
        return self.number_of_cpu

    def set_ram_size(self, val):
        """
        setter
        :param val: (str) KiB
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.ram_size = val

    def get_ram_size(self):
        """
        getter
        :return: (str) KiB
        """
        return self.ram_size

    def set_max_pods(self, val):
        """
        setter
        :param val: (str) max number of pods
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type')
        self.max_pods = val

    def get_max_pods(self):
        """
        getter
        :return: (str) max number of pods
        """
        return self.max_pods

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
            raise TypeError('Invalid type for val. Must input val as str type')
        self.stime = val

    def get_stime(self):
        """
        getter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        return self.stime

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

    def get_iface(self):
        """
        get network interface
        :return: (str) network interface
        """
        return self.iface

    def set_iface(self, iface):
        """
        set network interface
        :return:
        """
        self.iface = iface