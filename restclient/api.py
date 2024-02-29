import json
import requests

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger
from repository.cache.network import NetworkStatusRepository

logger = get_logger(__name__)

class RestClient:
    """
    CEdge-center client API(RESTful)
    """
    @classmethod
    def _get_hostname(cls):
        """
        get CEdge-center hostname
        :return:
        """
        if NetworkStatusRepository().get_center_network() is None:
            raise SystemError('Not found center http info')

        return NetworkStatusRepository().get_center_network().get_http()

    # @classmethod
    # def push_event(cls,
    #                cluster_id: str,
    #                event: dict) -> (bool, str):
    #     """
    #     push event
    #     :param cluster_id: (str)
    #     :param event: (str)
    #     :return:
    #     """
    #     if type(cluster_id) != str:
    #         raise ValueError('Invalid value for cluster_id')
    #
    #     if event is None and type(event) != dict:
    #         raise ValueError('Invalid value for event')
    #
    #     hostname = cls._get_hostname()
    #     url = hostname + '/api/agent' \
    #                      '/cluster/{cluster_id}/event'.format(cluster_id=cluster_id)
    #     try:
    #         response = requests.post(url=url, data=event)
    #         if response.status_code == 200:
    #             return True, ''
    #     except Exception as exc:
    #         logger.debug('Fail to request POST {}, body={}'.format(url, event))
    #         return False, get_exception_traceback(exc)
    #
    #
    #     return False, 'Error in response status({})'.format(response.status_code)

    @classmethod
    def push_response(cls, cluster_id: str,
                      request_id: str,
                      success: bool,
                      error: str,
                      result: str) -> (bool, str):
        """
        push response for MQTT request
        :param request_id:
        :param cluster_id:
        :param success: (bool)
        :param error: (str)
        :param result: (str)
        :return:
        """
        if type(cluster_id) != str:
            raise ValueError('Invalid value for cluster_id')

        if type(request_id) != str:
            raise ValueError('Invalid value for request_id')

        if result is not None:
            if type(result) != str:
                raise ValueError('Invalid value for response')

        hostname = cls._get_hostname()
        url = hostname + '/api/agent/v1' \
                         '/cluster/{cluster_id}' \
                         '/request/{request_id}'.format(cluster_id=cluster_id,
                                                        request_id=request_id)
        if error is None:
            error = ''
        if result is None:
            result = ''

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        body = {
            'success': success,
            'error': error,
            'content': {
                'request_id': request_id,
                'result': result
            }
        }
        try:
            response = requests.put(url=url, headers=headers, data=json.dumps(body), timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                return True, ''
        except Exception as exc:
            logger.debug('Fail to request POST {}, body={}'.format(url, body))
            return False, get_exception_traceback(exc)

        return False, 'Error in response status({})'.format(response.status_code)

    @classmethod
    def get_multi_cluster_network_diagnosis(cls, cluster_name: str) -> (bool, str, str):
        """
        get multi-cluster network diagnosis
        :param cluster_name: (str) cluster name
        :return:
        (bool): success
        (str): result
        (str): error
        """
        if type(cluster_name) != str or len(cluster_name) <= 0:
            raise ValueError('Invalid param \'cluster_name\'. cluster_name=' + cluster_name)

        hostname = cls._get_hostname()
        url = hostname + '/api/agent/v1' \
                         '/cluster/{cluster_name}/mcn/diagnosis'.format(cluster_name=cluster_name)

        try:
            response = requests.get(url=url, timeout=settings.REST_REQUEST_TIMEOUT)

            if response.status_code == 200:
                body = json.loads(response.content)

                if 'cluster_name' not in body:
                    return False, None, 'Invalid body, not found \'cluster_name\' key'

                if body['cluster_name'] != cluster_name:
                    return False, None, 'Invalid body value. cluster_name=' + body['cluster_name']

                if 'result' not in body:
                    return False, None, 'Invalid body, not found \'result\' key'

                if not body['result'] or len(body['result']) <= 0:
                    return False, None, 'Invalid body value. result=' + body['result']

                return True, body['result'], None

            else:
                content = json.loads(response.content)
                error = content['error']
                return False, None, error
        except Exception as exc:
            logger.debug('Fail to request GET {}'.format(url))
            return False, None, get_exception_traceback(exc)

    @classmethod
    def get_join_broker_info(cls, mc_connect_id: str) -> (bool, str, str):
        """
        get multi-cluster network diagnosis
        :param mc_connect_id: (str) multi-cluster connection id
        :return:
        (bool): success
        (str): result
        (str): error
        """
        if type(mc_connect_id) != str or len(mc_connect_id) <= 0:
            raise ValueError('Invalid param \'mc_connect_id\'. mc_connect_id=' + mc_connect_id)

        hostname = cls._get_hostname()
        url = hostname + '/api/agent/v1' \
                         '/mcn/{mc_connect_id}/broker'.format(mc_connect_id=mc_connect_id)

        try:
            response = requests.get(url=url, timeout=settings.REST_REQUEST_TIMEOUT)

            if response.status_code == 200:
                body = json.loads(response.content)

                if 'mc_connect_id' not in body:
                    return False, None, 'Invalid body, not found \'mc_connect_id\' key'

                if body['mc_connect_id'] != mc_connect_id:
                    return False, None, 'Invalid body value. mc_connect_id=' + body['mc_connect_id']

                if 'result' not in body:
                    return False, None, 'Invalid body, not found \'result\' key'

                if not body['result'] or len(body['result']) <= 0:
                    return False, None, 'Invalid body value. result=' + body['result']

                return True, body['result'], None

            else:
                content = json.loads(response.content)

                error = content['error']
                return False, None, error
        except Exception as exc:
            logger.debug('Fail to request GET ' + url)

            return False, None, get_exception_traceback(exc)
