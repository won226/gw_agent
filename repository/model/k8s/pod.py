import six

from repository.model.k8s.condition import Condition
from repository.common.type import Kubernetes, NodeStatus, PodStatus


class Pod:
    """
    Pod model class
    - unit test:
      serialize test: success
      deserialize: success
    """
    fields = {
        'kind': 'str',          # kind
        'name': 'str',          # pod name
        'state': 'str',         # pod status
        'namespace': 'str',     # namespace name
        'labels': 'list[str]',  # pod labels
        'host_ip': 'str',       # host node ip
        'pod_ip': 'str',        # pod ip
        'node': 'str',          # node hostname
        'conditions': 'list[Condition]',    # pod conditions
        'images': 'list[str]',  # docker images
        'stime': 'str',         # start time
    }

    def __init__(self, name):
        """
        Pod()
        :param name: (str)
        """
        self.kind = Kubernetes.POD.value
        self.name = name
        self.namespace = None
        self.state = PodStatus.UNKNOWN.value
        self.labels = []
        self.host_ip = None
        self.pod_ip = None
        self.node = None
        self.images = []
        self.conditions = []
        self.stime = None

    def set_namespace(self, val):
        """
        setter
        :param val: (str) namespace; not null
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.namespace = val

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind

    def get_name(self):
        """
        getter
        :return: (str) pod name
        """
        return self.name

    def get_namespace(self):
        """
        getter
        :return: (str)
        """
        return self.namespace

    def set_state(self, val):
        """
        setter
        :param val: (str) in PodStatus(Enum)
        :return:
        """
        if not PodStatus.validate(val):
            raise TypeError('Invalid Enum type(value={}). Must input val as str type in NodeStatus(Enum)'.format(val))
        self.state = val

    def get_state(self):
        """
        getter
        :return: (str) in PodStatus(Enum)
        """
        return self.state
    
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

    def set_host_ip(self, val):
        """
        setter
        :param val: (str) host ip address
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.host_ip = val

    def get_host_ip(self):
        """
        getter
        :return: (str) host ip address
        """
        return self.host_ip

    def set_pod_ip(self, val):
        """
        setter
        :param val: (str) pod ip address; nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.pod_ip = val

    def get_pod_ip(self):
        """
        getter
        :return: (str) pod ip address; nullable
        """
        return self.pod_ip

    def set_node_name(self, val):
        """
        setter
        :param val: (str) node hostname; not null
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.node = val

    def get_node_name(self):
        """
        getter
        :return: (str) node hostname
        """
        return self.node

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
                raise TypeError('Invalid val type(val[i]{}). Must input val as list[Condition] type'.format(type(item)))
        self.conditions = val

    def get_conditions(self):
        """
        getter
        :return: (list[Condition])
        """
        return self.conditions

    def set_images(self, val):
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
        self.images = val

    def get_images(self):
        """
        getter
        :return: (list[str])
        """
        return self.images

    def set_stime(self, val):
        """
        setter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.stime = val

    def get_stime(self):
        """
        getter
        :return: (str) datetime format ('%Y-%m-%d %H:%M:%S.%f')
        """
        return self.stime

    def to_dict(self):
        """Returns the model properties as a dict"""
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
        """ validate _dict """
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
