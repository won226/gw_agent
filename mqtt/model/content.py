import six

from mqtt.model.common.type import ContentType
from mqtt.model.file_content import FileContent

class Content:
    """
    MQTT Body model for CEdge-agent
    """
    fields = {
        "content_type": "str",
        "content": "list"
    }

    def __init__(self):
        self.content_type = None
        self.content = []

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
        to body object
        :param _dict: (dict)
        :return:
        """
        cls._validate(_dict)
        instance = cls()

        if not ContentType.validate(_dict['content_type']):
            raise ValueError('Invalid content_type')

        instance.set_content_type(_dict['content_type'])

        if _dict['content_type'] == ContentType.FILE.value:
            contents = []
            for item in _dict['content']:
                contents.append(FileContent.to_object(item))
            setattr(instance, 'content', contents)
        else:
            contents = []
            for item in _dict['content']:
                contents.append(item)
            setattr(instance, 'content', contents)

        return instance

    def to_dict(self):
        """
        to dict from self instance
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

    def get_content_type(self):
        """
        get content type
        :return: (str) ContentType(Enum).value
        """
        return self.content_type

    def set_content_type(self, content_type):
        """
        get content type
        :param content_type: (str) ContentType(Enum).value
        :return:
        """
        if not ContentType.validate(content_type):
            raise ValueError('Invalid value for content_type')

        self.content_type = content_type

    def get_content(self):
        """
        get content
        :return: (str)
        """
        return self.content

    def append_content(self, item):
        """
        append content
        :param item:
        :return:
        """
        if self.content_type == ContentType.FILE.value:
            if type(item) != FileContent:
                raise TypeError('Invalid type for item')
        elif self.content_type == ContentType.JSON.value:
            if type(item) != dict:
                raise TypeError('Invalid type for item')
        elif self.content_type == ContentType.TEXT.value:
            if type(item) != str:
                raise TypeError('Invalid type for item')
        else:
            raise ValueError('Not found content_type for self')

        self.content.append(item)