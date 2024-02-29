from enum import Enum

class Common(Enum):
    """
    model's kind for repository.model.common
    """
    COMPONENT_WATCHER = 'ComponentWatcher'
    PROVISONER = 'Provisioner'
    DELETE_MODEL = 'DeleteModel'
    CMD_RESULT = 'CmdResult'
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


class Kubernetes(Enum):
    """
    model's kind for repository.model.k8s
    """
    NODE = 'Node'
    POD = 'Pod'
    NAMESPACE = 'Namespace'
    DEPLOYMENT = 'Deployment'
    DAEMONSET = 'DaemonSet'
    SERVICE = 'Service'
    CONDITION = 'Condition'
    SERVICE_PORT = 'ServicePort'
    COMPONENTS = 'Components'
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


class Metric(Enum):
    """
    model's kind for repository.model.metric
    """
    NODE_METRIC = 'NodeMetric'
    POD_METRIC = 'PodMetric'
    MULTI_CLUSTER_METRIC = 'MultiClusterMetric'
    ENDPOINT_NETWORK_METRIC = 'EndpointNetworkMetric'
    CPU_METRIC = 'CPUMetric'
    MEM_METRIC = 'MemoryMetric'
    NETWORK_METRIC = 'NetworkMetric'
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


class NetStat(Enum):
    """
    model's kind for repository.model.netstat
    """
    MULTI_CLUSTER_NETWORK = 'MultiClusterNetwork'
    ENDPOINT_NETWORK = 'EndpointNetwork'
    CENTER_NETWORK = 'CenterNetwork'
    MULTI_CLUSTER_SERVICE = 'MultiClusterService'
    SERVICE_EXPORT = 'ServiceExport'
    SERVICE_EXPORTS = 'ServiceExports'
    SERVICE_IMPORT = 'ServiceImport'
    SERVICE_IMPORTS = 'ServiceImports'
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

class MultiClusterRole(Enum):
    """
     role enum for repository.model.netstat.MultiClusterNetwork
    """
    LOCAL = 'Local'
    REMOTE = 'Remote'
    NONE = 'None'
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

class MultiClusterConfigState(Enum):
    """
    Multi-cluster configuration state
    """
    CONNECT_REQUEST = 'ConnectRequest'
    CONNECTING = 'Connecting'
    DISCONNECT_REQUEST = 'DisconnectRequest'
    DISCONNECTING = 'Disconnecting'
    NONE = 'None'
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

class SubmarinerState(Enum):
    """
    Submariner state
    """
    BROKER_NA = "BrokerNotAvailable"
    BROKER_READY = "BrokerReady"
    BROKER_DEPLOYING = "BrokerDeploying"
    BROKER_JOINING = "BrokerJoining"
    BROKER_JOINED = "BrokerJoined"
    GATEWAY_CONNECTING = "GatewayConnecting"
    GATEWAY_CONNECTED = "GatewayConnected"
    GATEWAY_CONNECT_ERROR = "GatewayConnectError"
    BROKER_CLEANING = "BrokerCleaning"


class PodStatus(Enum):
    """
    Pod status(pod's phase) enum
    """
    # reference: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
    RUNNING = 'Running'
    PENDING = 'Pending'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
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

class ActiveStatus(Enum):
    """
    Service status enum
    """
    ACTIVE = 'Active'
    NOT_READY = 'NotReady'
    TERMINATING = 'Terminating'
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

class ClusterNetworkConnectionStatus(Enum):
    UNAVAILABLE = 'Unavailable'
    CONNECTED = 'Connected'
    TEMPORARY_NETWORK_FAILURE = 'TemporaryNetworkFailure'
    NETWORK_FAILURE = 'NetworkFailure'
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


class ClusterSessionStatus(Enum):
    UNAVAILABLE = 'Unavailable'
    CLUSTER_SESSION_INITIALIZING = 'ClusterSessionInitializing'
    CLUSTER_SESSION_ESTABLISHED = 'ClusterSessionEstablished'
    CLUSTER_SESSION_NOT_ESTABLISHED = 'ClusterSessionNotEstablished'
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

class NodeStatus(Enum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    SUCCEED = 'Terminated'
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


class ConnectionStatus(Enum):
    CONNECTED = 'Connected'
    CONNECTING = 'Connecting'
    UNAVAILABLE = 'Unavailable'
    ERROR = 'Error'
    UNKNOWN = 'Unknown'

    @classmethod
    def to_enum_str(cls, val):
        if val == "connecting":
            return cls.CONNECTING.value
        if val == "connected":
            return cls.CONNECTED.value
        if val == "unavailable":
            return cls.UNAVAILABLE.value
        if val == "error":
            return cls.ERROR.value

        return cls.UNKNOWN.value

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

class Constraints(Enum):
    DEPLOY_ALL_NODE = 'deployAllNode'
    DEPLOY_ONLY_MASTER_NODE = 'deployOnlyMasterNode'
    DEPLOY_ALL_WORKER_NODE = 'deployAllWorkerNode'
    DEPLOY_ANY_SINGLE_NODE = 'deployAnySingleNode'
    DEPLOY_ETCD = 'deployEtcd'
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

class CommandType(Enum):
    CREATE = 'create'
    DELETE = 'delete'
    NONE = 'none'
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

class ExecutionStatus(Enum):
    PENDING = 'Pending'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    RUNNING = 'Running'
    CREATING = 'Creating'
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


class CommandResult(Enum):
    BUSY = 'busy'
    SUCCESS = 'success'
    FAILED = 'failed'
    ACCEPT = 'accept'
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



class MultiClusterNetworkDiagnosis(Enum):
    """
    Multi-cluster network failure diagnosis result
    """
    BROKER_UPDATED = "BrokerUpdated"
    AGENT_NETWORK_ERROR = "AgentNetworkError"
    MULTI_CLUSTER_NETWORK_ERROR = "MultiClusterNetworkError"

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

    class MultiClusterConfigState(Enum):
        """
        Multi-cluster configuration state
        """
        CONNECT_REQUEST = 'ConnectRequest'
        CONNECTING = 'Connecting'
        DISCONNECT_REQUEST = 'DisconnectRequest'
        DISCONNECTING = 'Disconnecting'
        NONE = 'None'

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