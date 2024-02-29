import six

from gw_agent import settings
from repository.common.type import NetStat, ClusterSessionStatus, ClusterNetworkConnectionStatus
from utils.dateformat import DateFormatter


class CenterNetwork:
    """
    Center network model class
    """

    fields = {
        'kind': 'str',
        'name': 'str',  # center network name(http access url)
        'cluster_session_status': 'str',  # center cluster session status
        'network_connection_status': 'str',  # network connection status(i.e., 'connected' or 'unavailable')
        'last_connection_error_date': 'str', # last network connection error occurs datetime
        'http': 'str',  # http access '/' url
        'https': 'str',  # https access '/' url
        'amqp': 'str',  # amqp access url
        'token': 'str',  # center http/https access token
    }

    def __init__(self, name):
        """
        MultiClusterNetwork()
        :param name: (str) gedge-center access '/' url(http or https)
        """
        self.kind = NetStat.CENTER_NETWORK.value
        self.name = name
        self.network_connection_status = ClusterNetworkConnectionStatus.UNAVAILABLE.value
        self.cluster_session_status = ClusterSessionStatus.UNAVAILABLE.value
        self.last_connection_error_date = None
        self.http = None
        self.https = None
        self.amqp = None
        self.token = None
        self.firstNetworkFailureTime = None

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

        instance = cls(name=_dict['name'])
        instance.set_cluster_session_status(_dict['cluster_session_status'])
        instance.set_network_connection_status(_dict['network_connection_status'])
        instance.set_http(_dict['http'])
        instance.set_https(_dict['https'])
        instance.set_amqp(_dict['amqp'])
        instance.set_token(_dict['token'])

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

    def set_cluster_session_status(self, val):
        """
        set cluster session status
        :param val:
        :return:
        """
        if not ClusterSessionStatus.validate(val):
            raise ValueError('Invalid value. val={}, See ClusterSessionStatus(Enum)'.format(val))

        self.cluster_session_status = val

    def get_cluster_session_status(self):
        """
        get cluster session status
        :return:
        """
        return self.cluster_session_status

    def set_network_connection_status(self, val):
        """
        set network connection status
        :param val: (str) NetworkConnectionStatus(Enum)
        :return:
        """
        # Validate value error
        if not ClusterNetworkConnectionStatus.validate(val):
            raise TypeError('Invalid value. val={}. See ClusterSessionStatus(Enum)'.format(val))

        if val == ClusterNetworkConnectionStatus.TEMPORARY_NETWORK_FAILURE.value:
            previous_status = self.get_cluster_session_status()
            if previous_status == ClusterNetworkConnectionStatus.NETWORK_FAILURE.value:
                # If previous network connection status is NETWORK_FAILURE, returns
                return

            if not self.last_connection_error_date:
                self.last_connection_error_date = DateFormatter.current_datetime()
                self.network_connection_status = val
                return

            else:
                # decide as network failure
                elapsed = DateFormatter.get_elapsed_seconds(self.last_connection_error_date)
                if elapsed >= settings.CENTER_RECONNECT_WAIT_TIME:
                    # After wait settings.CENTER_RECONNECT_WAIT_TIME,
                    # change network connection status to NETWORK_FAILURE
                    self.last_connection_error_date = None
                    self.network_connection_status = \
                        ClusterNetworkConnectionStatus.NETWORK_FAILURE.value
                return

        self.network_connection_status = val  # It can be UNAVAILABLE or CONNECTED or NETWORK_FAILURE
        self.last_connection_error_date = None

        return

    def get_network_connection_status(self) -> str:
        """
        get network connection status
        :return: (str) NetworkConnectionStatus(Enum)
        """
        return self.network_connection_status

    def set_http(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as val'.format(type(val)))
        self.http = val

    def get_http(self):
        """
        getter
        :return: (str)
        """
        return self.http

    def set_https(self, val):
        """
        setter
        :param val: (str); nullable
        :return:
        """

        if val is not None and type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as url'.format(val))
        self.https = val

    def get_https(self):
        """
        getter
        :return: (str)
        """
        return self.https

    def set_amqp(self, val):
        """
        setter
        :param val: (str); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as val'.format(val))
        self.amqp = val

    def get_amqp(self):
        """
        getter
        :return: (str)
        """
        return self.amqp

    def set_token(self, val):
        """
        setter
        :param val: (str); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as val'.format(val))
        self.token = val

    def get_token(self):
        """
        getter
        :return: (str)
        """
        return self.token


