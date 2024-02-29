import six

from cluster.common.type import Event
from repository.common.type import NetStat
from utils.validate import Validator

class MultiClusterService:

    fields = {
        'kind': 'str',
        'name': 'str', # local cluster_id
        'exports': 'list[ServiceExport]', # service export list
        'imports': 'list[ServiceImport]' # service import list
    }

    def __init__(self):
        self.kind = NetStat.MULTI_CLUSTER_SERVICE.value
        self.exports = []
        self.imports = []

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

        instance = cls()
        exports = []
        imports = []

        for key, value in _dict.items():
            if key == 'exports':
                for item in value:  # list(ServiceExport)
                    exports.append(ServiceExport.to_object(item))
                setattr(instance, key, exports)
            if key == 'imports':
                for item in value:  # list(ServiceImport)
                    imports.append(ServiceImport.to_object(item))
                setattr(instance, key, imports)
            else:
                setattr(instance, key, value)

        return instance

    """ service export """
    def _get_export_index(self, val):
        """
        get service export index
        :param val: (ServiceExport)
        :return: (int) index; -1: not exist index, 0 or positive number: index
        """
        if len(self.exports) <= 0:
            return -1

        service_id = ''.join([val.cluster_id, val.name, val.namespace])
        for index in range(0, len(self.exports)):
            if self.exports[index].get_service_id() == service_id:
                return index

        return -1

    @staticmethod
    def _validate_service_export(val):
        """
        validate service export
        raise ValueError or TypeError exception when val has invalid value or type
        :param val: (ServiceExport)
        :return:
        """
        if val is None:
            raise ValueError('val is None')
        if type(val) != list:
            raise TypeError('Invalid type for val({}). Must input val as List[ServiceExport]'.format(type(val)))
        for v in val:
            if type(v) != ServiceExport:
                raise TypeError('Invalid type for val({}). Must input val as List[ServiceExport]'.format(type(val)))

    def set_service_exports(self, val):
        """
        set service export
        :param val: (ServiceExport)
        :return:
        """
        self._validate_service_export(val)
        self.exports = val

    def delete_service_export(self, val):
        """
        delete service export
        :param val:
        :return:
        """
        self._validate_service_export(val)

        index = self._get_export_index(val)
        if index >= 0:
            del self.exports[index]

    def get_service_exports(self):
        """
        getter
        :return: (list(ServiceExport))
        """
        return self.exports

    def synchronize_service_exports(self, val):
        """
        set service exports
        :param val: (list(ServiceExport))
        :return:
        """
        if val is None:
            raise ValueError('val is None')
        for item in val:
            self._validate_service_export(item)

        event_objects = []

        # check ADDED or MODIFIED event and store to repository
        for item in val:
            index = self._get_export_index(item)
            if index < 0:
                event_object = {
                    'event_type': Event.ADDED.value,
                    'object_type': NetStat.SERVICE_EXPORT.value,
                    'object_value': item
                }
                self.exports.append(item)
                event_objects.append(event_object)
            else:
                new = str(item.to_dict())
                orig = str(self.exports[index].to_dict())

                if new != orig:
                    event_object ={
                        'event_type': Event.MODIFIED.value,
                        'object_type': NetStat.SERVICE_EXPORT.value,
                        'object_value': item
                    }
                    self.exports[index] = item
                    event_objects.append(event_object)

        # check DELETED event and store to repository
        service_ids = []
        deleted_items = []
        deleted = False
        first = True

        for item in val:
            service_ids.append(item.get_service_id())

        while True:
            if not deleted and not first:
                break
            first = False
            for index in range(0, len(self.exports)):
                deleted = False
                if self.exports[index].get_service_id() not in service_ids:
                    deleted_items.append(self.exports.pop(index))
                    deleted = True
                    break

        for item in deleted_items:
            event_object = {
                'event_type': Event.DELETED.value,
                'object_type': NetStat.SERVICE_EXPORT.value,
                'object_value': item
            }
            event_objects.append(event_object)

        return event_objects

    """ service import """
    def _get_import_index(self, val):
        """
        get service import index
        :param val: (ServiceImport)
        :return: (int) index; -1: not exist index, 0 or positive number: index
        """
        if len(self.imports) <= 0:
            return -1

        service_id = ''.join([val.cluster_id, val.name, val.namespace])
        for index in range(0, len(self.imports)):
            if self.imports[index].get_service_id() == service_id:
                return index

        return -1

    def set_service_imports(self, val):
        """
        set service import
        :param val: (ServiceImport)
        :return:
        """
        self._validate_service_import(val)
        self.imports = val
        #
        #
        # index = self._get_import_index(val)
        # if index < 0:
        #     self.imports.append(val)
        # else:
        #     self.imports[index] = val

    @staticmethod
    def _validate_service_import(val):
        """
        validate service import
        raise ValueError or TypeError exception when val has invalid value or type
        :param val: (ServiceImport)
        :return:
        :param val:
        :return:
        """
        if val is None:
            raise ValueError('val is None')
        if type(val) != list:
            raise TypeError('Invalid type for val({}). Must input val as List[ServiceImport]'.format(type(val)))
        for v in val:
            if type(v) != ServiceImport:
                raise TypeError('Invalid type for val({}). Must input val as List[ServiceImport]'.format(type(val)))

    def delete_service_import(self, val):
        """
        delete service import
        :param val:
        :return:
        """
        self._validate_service_import(val)
        index = self._get_import_index(val)

        if index >= 0:
            del self.imports[index]

    def get_service_imports(self):
        """
        getter
        :return: (list(ServiceImport))
        """
        return self.imports

    def synchronize_service_imports(self, val):
        """
        synchronize service imports
        :param val: (list(ServiceImport))
        :return: (list(EventObject))
        (list(EventObject)); event_objects
        [{
            'event_type': Event.MODIFIED.value, # Event.ADDED.value or Event.MODIFIED.value or Event.DELETED.value
            'object_type': NetStat.SERVICE_IMPORT.value,
            'object_value': item
        }]
        """
        if val is None:
            raise ValueError('val is None')
        for item in val:
            self._validate_service_import(item)

        event_objects = []

        # check ADDED or MODIFIED event and store to repository
        for item in val:
            index = self._get_import_index(item)
            if index < 0:
                event_object = {
                    'event_type': Event.ADDED.value,
                    'object_type': NetStat.SERVICE_IMPORT.value,
                    'object_value': item
                }
                self.imports.append(item)
                event_objects.append(event_object)
            else:
                new = str(item.to_dict())
                orig = str(self.imports[index].to_dict())

                if new != orig:
                    event_object ={
                        'event_type': Event.MODIFIED.value,
                        'object_type': NetStat.SERVICE_IMPORT.value,
                        'object_value': item
                    }
                    self.imports[index] = item
                    event_objects.append(event_object)

        # check DELETED event and store to repository
        service_ids = []
        deleted_items = []
        deleted = False
        first = True

        for item in val:
            service_ids.append(item.get_service_id())

        while True:
            if not deleted and not first:
                break
            first = False
            for index in range(0, len(self.imports)):
                deleted = False
                if self.imports[index].get_service_id() not in service_ids:
                    deleted_items.append(self.imports.pop(index))
                    deleted = True
                    break

        for item in deleted_items:
            event_object = {
                'event_type': Event.DELETED.value,
                'object_type': NetStat.SERVICE_IMPORT.value,
                'object_value': item
            }
            event_objects.append(event_object)

        return event_objects


class ServiceImport:

    fields = {
        'kind': 'str',
        'cluster_id': 'str', # source cluster id
        'name': 'str',  # source service name
        'namespace': 'str',  # source service namespace
        'ip': 'str',  # source service ip
        'port': 'int',  # source service port
        'protocol': 'str',  # source service protocol
        'dns': 'str' # source service dns(service discovery)
    }

    def __init__(self):
        """
        ServiceImport()
        """
        self.kind = NetStat.SERVICE_IMPORT.value
        self.cluster_id = None
        self.name = None
        self.namespace = None
        self.ip = None
        self.port = None
        self.protocol = None
        self.dns = None

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

    def get_service_id(self):
        """
        get unique id
        :return:
        """
        return ''.join([self.cluster_id, self.name, self.namespace])

    def set_cluster_id(self, val):
        """
        setter
        :param val: (str) cluster_id
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type for val(({}){}). Must input val as str'.format(type(val), val))

        self.cluster_id = val

    def get_cluster_id(self):
        """
        getter
        :return:  (str) cluster_id
        """
        return self.cluster_id

    def set_name(self, val):
        """
        setter
        :param val: (str) service name
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type for val(({}){}). Must input val as str'.format(type(val), val))

        self.name = val

    def get_name(self):
        """
        getter
        :return: (str)  service name
        """
        return self.name

    def set_namespace(self, val):
        """
        setter
        :param val: (str) namespace
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type for val(({}){}). Must input val as str'.format(type(val), val))

        self.namespace = val

    def get_namespace(self):
        """
        getter
        :return:  (str) namespace
        """
        return self.namespace

    def set_ip(self, val):
        """
        setter
        :param val: (str) service ip address
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as str'.format(type(val), val))

        if not Validator.is_ip_address(val):
            raise ValueError('Invalid value({}). Must input val as ip address'.format(val))

        self.ip = val

    def get_ip(self):
        """
        getter
        :return:  (str) service ip address
        """
        return self.ip

    def set_port(self, val):
        """
        setter
        :param val: (int) val
        :return:
        """
        if not Validator.is_int(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as int'.format(type(val), val))

        self.port = val

    def set_protocol(self, val):
        """
        setter
        :param val: (str) protocol (TCP or UDP)
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as str'.format(type(val), val))
        if val.lower() not in ['tcp', 'udp']:
            raise ValueError('Invalid value({}). Must input val as TCP or UDP'.format(val))

        self.protocol = val

    def set_dns(self, val):
        """
        setter
        :param val: (str) dns
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as str'.format(type(val), val))

        self.dns = val


class ServiceExport:

    fields = {
        'kind': 'str',
        'cluster_id': 'str', # source cluster id
        'name': 'str',  # source service name
        'namespace': 'str',  # source service namespace
        'ip': 'str',  # source service ip
        'port': 'int',  # source service port
        'protocol': 'str',  # source service protocol
        'dns': 'str' # source service dns(service discovery)
    }

    def __init__(self):
        """
        ServiceImport()
        """
        self.kind = NetStat.SERVICE_EXPORT.value
        self.cluster_id = None
        self.name = None
        self.namespace = None
        self.ip = None
        self.port = None
        self.protocol = None
        self.dns = None

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

    def get_service_id(self):
        """
        get unique id
        :return:
        """
        return ''.join([self.cluster_id, self.name, self.namespace])

    def set_cluster_id(self, val):
        """
        setter
        :param val: (str) cluster_id
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type for val(({}){}). Must input val as str'.format(type(val), val))

        self.cluster_id = val

    def get_cluster_id(self):
        """
        getter
        :return:  (str) cluster_id
        """
        return self.cluster_id

    def set_name(self, val):
        """
        setter
        :param val: (str) service name
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type for val(({}){}). Must input val as str'.format(type(val), val))

        self.name = val

    def get_name(self):
        """
        getter
        :return: (str)  service name
        """
        return self.name

    def set_namespace(self, val):
        """
        setter
        :param val: (str) namespace
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type for val(({}){}). Must input val as str'.format(type(val), val))

        self.namespace = val

    def get_namespace(self):
        """
        getter
        :return:  (str) namespace
        """
        return self.namespace

    def set_ip(self, val):
        """
        setter
        :param val: (str) service ip address
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as str'.format(type(val), val))

        if not Validator.is_ip_address(val):
            raise ValueError('Invalid value({}). Must input val as ip address'.format(val))

        self.ip = val

    def get_ip(self):
        """
        getter
        :return:  (str) service ip address
        """
        return self.ip

    def set_port(self, val):
        """
        setter
        :param val: (int) val
        :return:
        """
        if not Validator.is_int(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as int'.format(type(val), val))

        self.port = val

    def set_protocol(self, val):
        """
        setter
        :param val: (str) protocol (TCP or UDP)
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as str'.format(type(val), val))
        if val.lower() not in ['tcp', 'udp']:
            raise ValueError('Invalid value({}). Must input val as TCP or UDP'.format(val))

        self.protocol = val

    def set_dns(self, val):
        """
        setter
        :param val: (str) dns
        :return:
        """
        if not Validator.is_str(val):
            raise TypeError('Invalid type or value for val(({}){}). Must input val as str'.format(type(val), val))

        self.dns = val