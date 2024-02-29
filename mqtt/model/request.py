import six

from mqtt.model.common.type import Method
from urllib.parse import urlparse, parse_qs
from mqtt.model.content import Content
from utils.validate import Validator


class Request:
    """
    MQTT Request model for CEdge-agent
    """
    fields = {
        'request_id': 'str',
        'path': 'str',
        'method': 'str',
        'body': 'dict',
        'created_date': 'str',  # datetime format(yyyy-mm-ddTHH:MM:SS)
    }

    def __init__(self):
        """
        Request
        """
        self.request_id = None
        self.path = None
        self.method = Method.UNKNOWN.value
        self._query_params = {}
        self._arguments = {}
        self.body = {}
        self.created_date = None

    @classmethod
    def _validate(cls, _dict: dict):
        """
        validate Request dictionary
        :param _dict:
        :return:
        """
        if type(_dict) != dict:
            raise TypeError('Invalid type. Must input dict type')

        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict: dict):
        """
        create object for mqtt body
        :param _dict: (dict)
        :return:
        """
        cls._validate(_dict)
        instance = cls()
        body = {}

        for key, value in _dict.items():
            if key == 'body':  # dict
                if len(value) > 0:
                    for k, v in value.items():
                        body[k] = Content.to_object(v)
                        print(body[k])
                setattr(instance, key, body)
            else:
                setattr(instance, key, value)

        return instance

    def to_dict(self):
        """
        get dictionary from instance
        :return:
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

    def get_request_id(self):
        """
        get request ID
        :return:
        """
        return self.request_id

    def set_request_id(self, request_id):
        """
        set request ID
        :param request_id: (str)
        :return:
        """
        if type(request_id) != str:
            raise TypeError('Invalid type. Input str type')

        self.request_id = request_id

    def get_path(self):
        """
        get path
        :return: (str)
        """
        return self.path

    def set_path(self, path):
        """
        set path
        :param path: (str) url path
        :return:
        """
        if type(path) != str:
            raise TypeError('Invalid type. Input str type')

        self.path = path

        self._parse_path()

    def get_method(self):
        """
        get method
        :return:
        """
        return self.method

    def set_method(self, method):
        """
        set method
        :param method: (str)
        :return:
        """
        if type(method) != str:
            raise TypeError('Invalid type for method param. Input str type')
        if not Method.validate(method):
            raise ValueError('Invalid value')

        self.method = method

    def get_body(self):
        """
        get body
        :return:
        """
        return self.body

    def set_body(self, body):
        """
        set body
        :param body: (dict)
        :return:
        """
        if body is not None:
            self.body = body

    def get_create_date(self):
        """
        get create date
        :return: (str) datetime format(yyyy-mm-ddTHH:MM:SS)
        """
        return self.created_date

    def set_create_date(self, create_date):
        """
        set create date
        :param create_date: (str) datetime format(yyyy-mm-ddTHH:MM:SS)
        :return:
        """
        Validator.is_dateformat(create_date)
        self.created_date = create_date

    def _parse_path(self):
        """
        parse path: parse query parameters
        :return:
        """
        result = urlparse(self.path)
        query = result.query
        self._query_params = parse_qs(query)

    def get_query_params(self):
        """
        get query parameter list from path fields
        :return: (dict); query parameter dictionary
        """
        return self._query_params

    def set_arguments(self, arguments):
        """
        set path variables
        :param arguments: (dict)
        :return:
        """
        self._arguments = arguments

    def get_arguments(self):
        """
        get path variables
        :return: (dict)
        """
        return self._arguments