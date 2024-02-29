from enum import Enum


class Connection(Enum):
    """ center, cluster connection type """
    AMQP = 'amqp'
    HTTP = 'http'
    HTTPS = 'https'

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
                if obj == key:
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


class Event(Enum):

    """ event types in kubernetes client api """
    ADDED = 'ADDED'
    MODIFIED = 'MODIFIED'
    DELETED = 'DELETED'
    AGENT_INIT = 'AGENT_INIT'
    NO_CHANGE = 'NO_CHANGE'
    ERROR = 'ERROR'
    BOOKMARK = 'BOOKMARK'
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
                if obj == key:
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
            if obj not in cls.__dict__.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False
        return True

class ThreadControl(Enum):

    """ thread control  """
    EMPTY = 'EMPTY'
    THREAD_EXIT = 'THREAD_EXIT'
    SUSPEND = 'SUSPEND'
    ADD_HOOK_METHOD = 'ADD_HOOK_METHOD'
    REMOVE_HOOK_METHOD = 'REMOVE_HOOK_METHOD'
    IGNORE = 'IGNORE'
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
                if obj == key:
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
            if obj not in cls.__dict__.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False
        return True


class ThreadState(Enum):

    """ thread state """
    NOT_READY = 'NOT_READY'
    RUNNING = 'RUNNING'
    SUSPENDED = 'SUSPENDED'
    BUSY = 'BUSY'
    DEAD = 'DEAD'
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
                if obj == key:
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
            if obj not in cls.__dict__.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False
        return True

class ThreadType(Enum):

    """ thread type """
    THREAD_WATCHDOG = 'THREAD_WATCHDOG'
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
                if obj == key:
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
            if obj not in cls.__dict__.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False
        return True
