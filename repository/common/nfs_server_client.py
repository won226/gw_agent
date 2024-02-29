import json

import requests

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from repository.common.type import MultiClusterRole
from utils.validate import Validator


class Connector:
    _local_endpoint = None
    _remote_endpoint = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._log = settings.get_logger(__name__)
        self._api_port = settings.NFS_SERVER_API_PORT

    def is_ready(self, role):
        """
        is ready for "Local" or "Remote"
        :param role: (str) "Local" or "Remote"
        :return: (bool) True - ready, False - not ready
        """
        self.validate_role(role)

        if role == MultiClusterRole.LOCAL.value:
            if self._local_endpoint is None:
                return False

            else:
                return True
        else:
            if self._remote_endpoint is None:
                return False

            else:
                return True

    def set_endpoint_none(self, role):
        """
        set endpoint none
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :return:
        """
        self.validate_role(role)

        if role == MultiClusterRole.LOCAL.value:
            self._local_endpoint = None
        else:
            self._remote_endpoint = None

    def set_endpoint(self, role, ip, port):
        """
        set endpoint address
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :param ip: (str) ip address
        :param port: (int) port
        :return:
        """

        if not MultiClusterRole.validate(role):
            raise ValueError('Invalid role value({}). Must input "Local" or "Remote"', format(role))

        if not Validator.is_ip_address(ip):
            raise ValueError('Invalid value in ip({})'.format(ip))

        if not Validator.is_int(port):
            raise ValueError('Invalid value in port({}). Must input int as port'.format(port))

        if role == MultiClusterRole.LOCAL.value:
            self._local_endpoint = 'http://{}:{}'.format(ip, port)
        else:
            self._remote_endpoint = 'http://{}:{}'.format(ip, port)

    def validate_endpoint(self, role):
        """
        validate nfs-server api endpoint
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :return: (bool) True - validated, False - not validated
        """
        self.validate_role(role)

        if role == MultiClusterRole.LOCAL.value and self._local_endpoint is None:
            raise SystemError('nfs-server is not deployed in local cluster')

        if role == MultiClusterRole.REMOTE.value and self._remote_endpoint is None:
            raise SystemError('nfs-server is not deployed in local cluster')

    @staticmethod
    def validate_role(role):
        if not MultiClusterRole.validate(role):
            raise ValueError('Invalid role value({}). Must input "Remote" or "Local"'.format(role))

    def is_connectable(self, role):
        """
        check whether NFS server('Local' or 'Remote') is connectable
        :param role: (str) multi-cluster broker role
        :return:
        (bool) True - connectable, False - not connectable
        (str) error message
        """
        try:
            self.validate_role(role)
        except ValueError as exc:
            return False, ' '.format(get_exception_traceback(exc))

        if role == MultiClusterRole.LOCAL.value:
            url = self._local_endpoint + '/api/v1/vol'
        else:
            url = self._remote_endpoint + '/api/v1/vol'

        if url is None:
            return False, 'No connection'
        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                return True, ''
        except Exception as exc:
            return False, get_exception_traceback(exc)

        return True, ''

    def get_publish_volumes(self, role):
        """
        get publish volumes in nfs-server
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :return: list(str)
        """
        self.validate_endpoint(role)

        if role == MultiClusterRole.LOCAL.value:
            url = self._local_endpoint + '/api/v1/vol'
        else:
            url = self._remote_endpoint + '/api/v1/vol'

        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            body = json.loads(response.content)

            if response.status_code == 200:
                if body['success']:
                    return True, body['content'], None
                else:
                    return False, '', body['error']
            else:
                raise SystemError('Fail to get nfs-server published volumes. caused by {}.'.format(body['error']))
        except Exception as exc:
            raise SystemError('Fail to connect to nfs-server api({}) '
                              'caused by {}'.format(url, get_exception_traceback(exc)))

    def is_volume_exist(self, role, volume):
        """
        check whether volume is exist or not
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :param volume: (str) volume name
        :return: (bool) True - exist, False - not exist
        """
        self.validate_endpoint(role)

        if not Validator.is_str(volume):
            raise ValueError('Invalid volume value({}). Must input str, not None.'.format(volume))

        if role == MultiClusterRole.LOCAL.value:
            url = self._local_endpoint + '/api/v1/vol/{}'.format(volume)
        else:
            url = self._remote_endpoint + '/api/v1/vol/{}'.format(volume)

        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            body = json.loads(response.content)

            if response.status_code == 200:
                if body['success']:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as exc:
            raise SystemError('Fail to connect to nfs-server api({}) '
                              'caused by {}'.format(url, get_exception_traceback(exc)))

    def publish_volume(self, role, volume):
        """
        create volume
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :param volume: (str) volume name
        :return:
        """
        self.validate_endpoint(role)

        if not Validator.is_str(volume):
            raise ValueError('Invalid volume value({}). Must input str, not None.'.format(volume))

        if self.is_volume_exist(role, volume):
            return True, '', ''

        if role == MultiClusterRole.LOCAL.value:
            url = self._local_endpoint + '/api/v1/vol/{}'.format(volume)
        else:
            url = self._remote_endpoint + '/api/v1/vol/{}'.format(volume)

        try:
            response = requests.post(url, timeout=settings.REST_REQUEST_TIMEOUT)
            body = json.loads(response.content)

            if response.status_code == 200:
                if body['success']:
                    return True, '', ''
                else:
                    return False, '', body['error']
            else:
                raise SystemError('Fail to publish nfs-server volume({}). caused by {}.'.format(volume, body['error']))
        except Exception as exc:
            return False, '', 'Fail to connect to nfs-server api({}) ' \
                              'caused by {}'.format(url, get_exception_traceback(exc))

    def remove_volume(self, role, volume):
        """
        create volume
        :param role: (str) "Local" or "Remote" see repository.common.type.MultiClusterRole
        :param volume: (str) volume name
        :return:
        """
        self.validate_endpoint(role)

        if not Validator.is_str(volume):
            raise ValueError('Invalid volume value({}). Must input str, not None.'.format(volume))

        if not self.is_volume_exist(role, volume):
            return True, '', ''

        if role == MultiClusterRole.LOCAL.value:
            url = self._local_endpoint + '/api/v1/vol/{}'.format(volume)
        else:
            url = self._remote_endpoint + '/api/v1/vol/{}'.format(volume)

        try:
            response = requests.delete(url, timeout=settings.REST_REQUEST_TIMEOUT)
            body = json.loads(response.content)

            if response.status_code == 200:
                if body['success']:
                    return True, '', ''
                else:
                    return False, None, body['error']

            else:
                raise SystemError('Fail to remove nfs-server volume({}). caused by {}.'.format(volume, body['error']))
        except Exception as exc:
            return False, '', 'Fail to connect to nfs-server api({}) ' \
                              'caused by {}'.format(url, get_exception_traceback(exc))
