import six

from repository.common.type import NetStat, MultiClusterRole
from repository.model.netstat.endpoint import EndpointNetwork


class MultiClusterNetwork:
    """
    Multi-cluster network model class
    """

    fields = {
        'kind': 'str',
        'name': 'str',  # cluster_id
        'broker_role': 'str',  # broker location ('Local', 'Remote')
        'globalnet': 'bool',  # global vpn y/n(i.e., 'enabled' or 'disabled')
        'global_cidr': 'str',  # global vpn(i.e., '244.0.0.0/8')
        'cable_driver': 'str',  # tunneling driver(i.e., 'wireguard' or 'libswan' or 'ipsec')
        'endpoints': 'list[EndpointNetwork]'
    }

    def __init__(self, name):
        """
        MultiClusterNetwork()
        :param name: (str) cluster name created from center (i.e., west-cls)
        """
        self.kind = NetStat.MULTI_CLUSTER_NETWORK.value
        self.name = name
        self.broker_role = MultiClusterRole.UNKNOWN
        self.globalnet = False
        self.global_cidr = None
        self.cable_driver = None
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
        instance = cls(name=_dict['name'])
        endpoints = []
        for key, value in _dict.items():
            if key == 'endpoints':
                for item in value:
                    endpoints.append(EndpointNetwork.to_object(item))
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

    def set_broker_role(self, val):
        """
        setter
        :param val: (MultiClusterRole(Enum)) LOCAL or REMOTE or UNKNOWN
        :return:
        """
        if not MultiClusterRole.validate(val):
            raise TypeError('Invalid Enum type(value={}). '
                            'Must input val as str type in MultiClusterRole(Enum)'.format(val))

        self.broker_role = val

    def get_broker_role(self):
        """
        getter
        :return: (MultiClusterRole(Enum)) LOCAL or REMOTE or UNKNOWN
        """
        return self.broker_role

    def set_globalnet(self, val):
        """
        setter
        :param val: (bool) True - enabled, False - disabled
        :return:
        """
        if type(val) != bool:
            raise TypeError('Invalid type for val({}). Must input val as bool type'.format(type(val)))

        self.globalnet = val

    def get_globalnet(self):
        """
        getter
        :return: (bool) True - enabled, False - disabled
        """
        return self.globalnet

    def set_global_cidr(self, val):
        """
        setter
        :param val: (str) global vpn(i.e., '244.0.0.0/8'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.global_cidr = val

    def get_global_cidr(self):
        """
        getter
        :return: (str) global vpn(i.e., '244.0.0.0/8')
        """
        return self.global_cidr

    def set_cable_driver(self, val):
        """
        setter
        :param val: (str) tunneling driver(i.e., 'wireguard' or 'libswan' or 'ipsec'); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid type for val({}). Must input val as str type'.format(type(val)))
        self.cable_driver = val

    def get_cable_driver(self):
        """
        getter
        :return: (str) tunneling driver(i.e., 'wireguard' or 'libswan' or 'ipsec')
        """
        return self.cable_driver

    def _get_endpoint_index(self, val):
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

    def get_remote_endpoints(self):
        """
        get remote endpoints
        :return:
        """
        endpoints = []

        for endpoint in self.endpoints:
            if endpoint.get_role() == MultiClusterRole.REMOTE.value:
                endpoints.append(endpoint)

        return endpoints

    def get_endpoints(self):
        """
        get endpoints
        :return: (list(EndpointNetwork))
        """
        return self.endpoints

    @classmethod
    def validate_endpoint_list(cls, val):
        if val is None:
            raise ValueError('val is None')
        if len(val) <= 0:
            return None
        if type(val) != list:
            raise ValueError('Invalid type for val({}). Must input val as list(EndpointNetwork)'.format(type(val)))
        for item in val:
            if type(item) != EndpointNetwork:
                raise ValueError('Invalid type for val({}). Must input val as list(EndpointNetwork)'.format(type(val)))

    def set_endpoints(self, val):
        """
        set endpoints
        :param val:
        :return:
        """
        self.validate_endpoint_list(val)

        for item in val:
            index = self._get_endpoint_index(item)

            if index < 0:
                self.endpoints.append(item)
            else:
                self.endpoints[index] = item

    def delete_endpoints(self, val):
        """
        delete endpoints
        :param val: (list(EndpointNetwork))
        :return:
        """
        self.validate_endpoint_list(val)

        for item in val:
            index = self._get_endpoint_index(item)
            if index >= 0:
                del self.endpoints[index]


    # def synchronize_endpoints(self, val):
    #     """
    #     synchronize endpoints
    #     :param val: (list(EndpointNetwork))
    #     :return: (list(EventObject)); event_objects
    #     [{
    #         'event_type': Event.MODIFIED.value,
    #         'object_type': NetStat.ENDPOINT_NETWORK.value,
    #         'object_value': item
    #     }]
    #     """
    #     self.validate_endpoint_list(val)
    #
    #     event_objects = []
    #
    #     # check ADDED or MODIFIED event and store to repository
    #     for item in val:
    #         index = self._get_endpoint_index(item.get_name())
    #         if index < 0:
    #             event_object = {
    #                 'event_type': Event.ADDED.value,
    #                 'object_type': NetStat.ENDPOINT_NETWORK.value,
    #                 'object_value': item
    #             }
    #             self.endpoints.append(item)
    #             event_objects.append(event_object)
    #         else:
    #             new = str(item.to_dict())
    #             orig = str(self.endpoints[index].to_dict())
    #
    #             if new != orig:
    #                 event_object = {
    #                     'event_type': Event.MODIFIED.value,
    #                     'object_type': NetStat.ENDPOINT_NETWORK.value,
    #                     'object_value': item
    #                 }
    #                 self.endpoints[index] = item
    #                 event_objects.append(event_object)
    #
    #     # check DELETED event and store to repository
    #     param_names = []
    #     delete_names = []
    #     deleted_items = []
    #     total_deletions = 0
    #     deletions = 0
    #
    #     # create parameter name list
    #     for item in val:
    #         param_names.append(item.get_name())
    #
    #     # create delete name list
    #     for endpoint in self.endpoints:
    #         if endpoint.get_name() not in param_names:
    #             delete_names.append(endpoint.get_name())
    #             total_deletions += 1
    #
    #     # pop delete items from self.endpoints, create delete endpoint list
    #     while True:
    #         if deletions >= total_deletions:
    #             break
    #         for index in range(0, len(self.endpoints)):
    #             if self.endpoints[index].get_name() in delete_names:
    #                 deleted_items.append(self.endpoints.pop(index))
    #                 deletions += 1
    #                 break
    #
    #     # create endpoint delete event
    #     for item in deleted_items:
    #         event_object = {
    #             'event_type': Event.DELETED.value,
    #             'object_type': NetStat.ENDPOINT_NETWORK.value,
    #             'object_value': item
    #         }
    #         event_objects.append(event_object)
    #
    #     return event_objects
