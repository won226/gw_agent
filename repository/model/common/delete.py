import six

from repository.common.type import Common


class DeleteModel:
    """
    Name model class
    """
    fields = {
        'kind': 'str',
        'namespace': 'str',
        'name': 'str',
    }

    def __init__(self, kind, name, namespace):
        """
        Name()
        :param name: (str) object name
        """
        self.kind = kind
        self.name = name
        self.namespace = namespace

    def get_kind(self):
        """
        get kind
        :return: (str)
        """
        return self.kind

    def get_name(self):
        """
        get resource name
        :return: (str)
        """
        return self.name

    def get_namespace(self):
        """
        get namespace
        :return:
        """
        return self.namespace

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

        return cls(name=_dict['name'])

