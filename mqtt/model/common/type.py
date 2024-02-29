from enum import Enum

class Method(Enum):
    """
    MQTT Method type
    """

    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    PUT = 'PUT'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def to_enum(cls, obj):
        """
        cast value(str) to own class's Enum attribute
        if value is Enum, validate it and returns itself.
        :param obj: (object)
        :return:
            a Enum type in own class
        """
        result = cls.UNKNOWN
        if type(obj) is str:
            for key, value in cls.__dict__.items():
                if obj.upper() == key:
                    result = value
        else:
            if not cls.validate(obj):
                result = cls.UNKNOWN
            else:
                result = obj
        return result


    @classmethod
    def validate(cls, obj):
        """
        validate whether value is included in own class
        :param obj: (str or own class's attribute)
        :return:
        """
        if type(obj) is str:
            if obj.upper() not in cls.__dict__.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False
        return True


class ContentType(Enum):
    """
    MQTT Body content type
    """
    JSON = 'JSON'
    TEXT = 'TEXT'
    FILE = 'FILE'

    @classmethod
    def to_enum(cls, obj):
        """
        cast value(str) to own class's Enum attribute
        if value is Enum, validate it and returns itself.
        :param obj: (object)
        :return:
            a Enum type in own class
        """
        result = cls.UNKNOWN
        if type(obj) is str:
            for key, value in cls.__dict__.items():
                if obj.upper() == key:
                    result = value
        else:
            if not cls.validate(obj):
                result = cls.UNKNOWN
            else:
                result = obj
        return result


    @classmethod
    def validate(cls, obj):
        """
        validate whether value is included in own class
        :param obj: (str or own class's attribute)
        :return:
        """
        if type(obj) is str:
            if obj.upper() not in cls.__dict__.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False

        return True