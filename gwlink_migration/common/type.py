from enum import Enum

class MigrationSubTask(Enum):
    """
    Pod migration sub tasks
    """
    CREATE_SNAPSHOT = 'CREATE_SNAPSHOT'
    VALIDATE_SNAPSHOT = 'VALIDATE_SNAPSHOT'
    RESTORE = 'RESTORE'
    DELETE_ORIGIN = 'DELETE_ORIGIN'
    VALIDATE_MIGRATION = 'VALIDATE_MIGRATION'
    UNKNOWN = 'Unknown'

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
            value_map = getattr(cls, "_value2member_map_")
            for key, value in value_map.items():
                if obj == key:
                    result = value
                    break
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
            value_map = getattr(cls, "_value2member_map_")
            if obj not in value_map.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False

        return True

class MigrationStatus(Enum):
    """
    Migration status
    """
    ISSUED = 'ISSUED'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    PENDING = 'PENDING'
    ERROR_EXITED = 'ERROR_EXITED'
    COMPLETED = 'COMPLETED'
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
            value_map = getattr(cls, "_value2member_map_")
            for key, value in value_map.items():
                if obj == key:
                    result = value
                    break
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
            value_map = getattr(cls, "_value2member_map_")
            if obj not in value_map.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False

        return True

class MigrationOperation(Enum):
    """
    Migration Operation
    """
    CHECKPOINT = 'checkpoint'
    RESTORE = 'restore'
    UNKNOWN = 'unknown'


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
            value_map = getattr(cls, "_value2member_map_")
            for key, value in value_map.items():
                if obj == key:
                    result = value
                    break
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
            value_map = getattr(cls, "_value2member_map_")
            if obj not in value_map.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False

        return True

class MigrationError(Enum):
    """
    Migration error
    """
    NONE = 'NONE'
    INVALID_SUBTASK = 'INVALID_SUBTASK'
    GW_AGENT_REQUEST_TIMEOUT = 'GW_AGENT_REQUEST_TIMEOUT'
    MAX_RETRY_EXCEEDED = 'MAX_RETRY_EXCEEDED'
    MIGRATION_TIMEOUT_EXPIRED = 'MIGRATION_TIMEOUT_EXPIRED'
    NETWORK_UNREACHABLE = 'NETWORK_UNREACHABLE'
    GW_AGENT_NOT_CONNECTED = 'GW_AGENT_NOT_CONNECTED'
    CONNECTION_RESET_BY_PEER = 'CONNECTION_RESET_BY_PEER'
    CONNECTION_REFUSED = 'CONNECTION_REFUSED'
    POD_TEMPLATE_FILE_WRITE_ERROR = 'POD_TEMPLATE_FILE_WRITE_ERROR'
    SERVICE_MANIFEST_APPLY_ERROR = 'SERVICE_MANIFEST_APPLY_ERROR'
    SERVICE_MANIFEST_READ_ERROR = 'SERVICE_MANIFEST_READ_ERROR'
    SERVICE_TEMPLATE_FILE_CREATE_ERROR = 'SERVICE_TEMPLATE_FILE_CREATE_ERROR'
    SERVICE_TEMPLATE_FILE_WRITE_ERROR = 'SERVICE_TEMPLATE_FILE_WRITE_ERROR'
    MIGRATION_TEMPLATE_FILE_IO_ERROR = 'MIGRATION_TEMPLATE_FILE_IO_ERROR'
    SHARED_DIRECTORY_NOT_FOUND = 'SHARED_DIRECTORY_NOT_FOUND'
    SHARED_DIRECTORY_NOT_READY = 'SHARED_DIRECTORY_NOT_READY'
    POD_SNAPSHOT_DIRECTORY_NOT_FOUND = 'POD_SNAPSHOT_DIRECTORY_NOT_FOUND'
    SNAPSHOT_MANIFEST_APPLY_ERROR = 'SNAPSHOT_MANIFEST_APPLY_ERROR'
    SNAPSHOT_MANIFEST_DELETE_ERROR = 'SNAPSHOT_MANIFEST_DELETE_ERROR'
    RESTORE_MANIFEST_APPLY_ERROR = 'RESTORE_MANIFEST_APPLY_ERROR'
    RESTORE_MANIFEST_DELETE_ERROR = 'RESTORE_MANIFEST_DELETE_ERROR'
    DESCRIPTION_FILE_NOT_FOUND = 'DESCRIPTION_FILE_NOT_FOUND'
    POD_NOT_FOUND = 'POD_NOT_FOUND'
    LIVMIGRATION_CRD_NOT_FOUND = 'LIVMIGRATION_CRD_NOT_FOUND'
    INVALID_LIVMIGRATION_OPERATION = 'INVALID_LIVMIGRATION_OPERATION'
    CONTAINER_NAME_NOT_FOUND = 'CONTAINER_NAME_NOT_FOUND'
    CLUSTER_NOT_FOUND = 'CLUSTER_NOT_FOUND'
    NODE_NOT_FOUND = 'NODE_NOT_FOUND'
    NAMESPACE_NOT_FOUND = 'NAMESPACE_NOT_FOUND'
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
            value_map = getattr(cls, "_value2member_map_")
            for key, value in value_map.items():
                if obj == key:
                    result = value
                    break
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
            value_map = getattr(cls, "_value2member_map_")
            if obj not in value_map.keys():
                return False
        else:
            if obj not in cls.__dict__.values():
                return False

        return True
