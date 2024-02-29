from repository.common.type import Metric


# todo: TBD, not used in current version
class PodMetric:
    """
    PodMetric model class
    """

    fields = {
        'kind': 'str',
        'name': 'str',
    }

    def __init__(self, name):
        self.kind = Metric.POD_METRIC.value
        self.name = name

    def get_kind(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.kind

    def get_name(self) -> str:
        """
        getter
        :return: (str)
        """
        return self.name

    @classmethod
    def validate_dict(cls, _dict):
        """
        validate _dict
        """
        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))
