import six

from repository.common.type import Metric


class MemoryMetric:
    """
    MemoryMetric model class
    """

    fields = {
        'kind': 'kind',
        'usages': 'list(list())', # [[int,float], [int,float], [int,float]]
        'total': 'int',
    }


    def __init__(self, total, usages):
        """
        MemoryMetric()
        :param total: (int) total amount
        :param usages: list(list()) memory usages
        """
        self.kind = Metric.MEM_METRIC.value
        self.total = total
        self.usages = usages

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

        return cls(total=_dict['total'],
                   usages=_dict['usages'])


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

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind
