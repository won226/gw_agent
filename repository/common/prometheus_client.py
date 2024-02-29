import datetime

import json
import requests
from urllib import parse

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger
from utils.validate import Validator


class Connector(object):
    """
    metric connector
    """
    _endpoint = None
    _logger = None
    _step = '5s'
    _period = 59

    probe_format = 'http://{endpoint}'
    range_query_format = 'http://{endpoint}/api/v1/query_range?query={query}&start={start}&end={end}&step={step}'
    query_format = 'http://{endpoint}/api/v1/query?query={query}'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._logger = get_logger(__name__)

    def is_ready(self):
        if self._endpoint is None:
            return False

        return True

    def set_endpoint_none(self):
        """
        set endpoint invalid(none)
        :return:
        """
        self._endpoint = None

    def set_endpoint(self, ip, port):
        """
        set endpoint address
        :return:
        """
        if not Validator.is_ip_address(ip):
            raise ValueError('Invalid value in ip({})'.format(ip))

        if not Validator.is_int(port):
            raise ValueError('Invalid value in port({}). Must input int as port'.format(port))

        self._endpoint = '{}:{}'.format(ip, port)

    def get_endpoint(self):
        """
        getter
        :return: (str) prometheus endpoint address
        """
        return self._endpoint

    def is_connectable(self):
        """
        check whether prometheus server is connectable or not
        :return:
        (bool) True - connectable, False - not connectable
        (str) error message
        """
        url = self.probe_format.format(endpoint=self._endpoint)

        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                return True, ''
        except Exception as exc:
            return False, get_exception_traceback(exc)

        return True, ''

    def get_number_of_cpu(self):
        """
        get number of cpus
        :return: list(dict())
        [{
            "instance": "", # instance
            "total": 2 # number of cpus
        }]
        """
        query = 'node_cpu_seconds_total{mode="system"}'
        query = parse.quote(query)
        url = self.query_format.format(endpoint=self._endpoint, query=query)
        metrics = []

        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)

            if response.status_code == 200:
                content = json.loads(response.content)

                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        if not any(d['instance'] == item['metric']['instance'] for d in metrics):
                            var = {
                                'instance': item['metric']['instance'],
                                'usages': [],
                                'total': 0,
                            }
                            metrics.append(var)

                    for item in result:
                        for metric in metrics:
                            if item['metric']['instance'] == metric['instance']:
                                metric['total'] += 1

                else:
                    return metrics

            else:
                raise SystemError('Fail to get number of cpu from prometheus({}})'.format(url))

        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_cpu_usages(self):
        """
        get cpu usage for each node
        :return: (dict)
        list(dict())
        [{
            "instance": "", # instance
            "total": 2 # number of cpus
            "usages": # list[list[int, float], ...]; list[[timestamp, cpu_usage]]
        }]
        """

        metrics = self.get_number_of_cpu()
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self._period)
        query = 'sum(rate(node_cpu_seconds_total{mode!~"idle|iowait"}[10s])) by (instance) ' \
                '/ count(node_cpu_seconds_total{mode="system"}) by (instance) * 100'
        query = parse.quote(query)
        url = self.range_query_format.format(endpoint=self._endpoint,
                                             query=query,
                                             start=start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             end=end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             step=self._step)
        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        for metric in metrics:
                            if metric['instance'] == item['metric']['instance']:
                                metric['usages'] = item['values']
                                for usage in metric['usages']:
                                    usage[1] = round(float(usage[1]), 2)
                else:
                    return []
            else:
                raise SystemError('Fail to get cpu usage from prometheus({}})'.format(url))
        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_total_memory(self):
        """
        get total memory for each node
        :return: list(dict())
        [{
            "instance": "", # instance
            "total": 16G # size of memory
        }]
        """
        query = 'node_memory_MemTotal_bytes'
        query = parse.quote(query)
        url = self.query_format.format(endpoint=self._endpoint, query=query)
        metrics = []

        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        if not any(d['instance'] == item['metric']['instance'] for d in metrics):
                            var = {
                                'instance': item['metric']['instance'],
                                'usages': [],
                                'total': str(round(int(item['value'][1])/1024**2, 0))+'MiB',
                            }
                            metrics.append(var)
                else:
                    return metrics
            else:
                raise SystemError('Fail to get cpu usage from prometheus({}})'.format(url))
        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_memory_usages(self):
        """
        get memory usages for each node
        :return:
        """
        metrics = self.get_total_memory()
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self._period)
        query = 'sum(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) by (instance) / ' \
                'sum(node_memory_MemTotal_bytes) by (instance)'
        query = parse.quote(query)
        url = self.range_query_format.format(endpoint=self._endpoint,
                                             query=query,
                                             start=start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             end=end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             step=self._step)
        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        for metric in metrics:
                            if metric['instance'] == item['metric']['instance']:
                                metric['usages'] = item['values']
                                for usage in metric['usages']:
                                    usage[1] = round(float(usage[1]), 2)
                else:
                    return []
            else:
                raise SystemError('Fail to get cpu usage from prometheus({}})'.format(url))
        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_network_info(self):
        """
        get network information
        :return:
        [{
            "instance": "", # instance
            "device": "eth0", # network device
        }]
        """
        query = 'node_network_info'
        query = parse.quote(query)
        url = self.query_format.format(endpoint=self._endpoint, query=query)
        metrics = []

        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        if not any(d['instance'] == item['metric']['instance'] for d in metrics):
                            var = {
                                'instance': item['metric']['instance'],
                                'rx_bytes': [],
                                'tx_types': [],
                                'device': 'eth0',
                            }
                            metrics.append(var)
                else:
                    return metrics

            else:
                raise SystemError('Fail to get cpu usage from prometheus({}})'.format(url))

        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_rx_bytes(self, metrics):
        """
        get received bytes for eth0
        :param metrics:
        :return: (list(dict))
        [{
            "instance": "", # instance
            "device": "eth0", # network device
            "rx_bytes": [[timestamp, rx_byte], ...]
        }]
        """
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self._period)
        query = 'node_network_receive_bytes_total'
        query = parse.quote(query)
        url = self.range_query_format.format(endpoint=self._endpoint,
                                             query=query,
                                             start=start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             end=end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             step=self._step)
        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        for metric in metrics:
                            if metric['instance'] == item['metric']['instance'] and \
                                    item['metric']['device'] == 'eth0':
                                metric['rx_bytes'] = item['values']
                                for rx_byte in metric['rx_bytes']:
                                    rx_byte[1] = int(rx_byte[1])
                else:
                    return []
            else:
                raise SystemError('Fail to get cpu usage from prometheus({}})'.format(url))
        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_tx_bytes(self, metrics):
        """
        get transmit bytes for eth0
        :param metrics:
        :return: (list(dict))
        [{
            "instance": "", # instance
            "device": "eth0", # network device
            "rx_bytes": [[timestamp, rx_byte], ...]
            "tx_bytes": [[timestamp, tx_byte], ...]
        }]
        """
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self._period)
        query = 'node_network_transmit_bytes_total'
        query = parse.quote(query)
        url = self.range_query_format.format(endpoint=self._endpoint,
                                             query=query,
                                             start=start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             end=end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             step=self._step)
        try:
            response = requests.get(url, timeout=settings.REST_REQUEST_TIMEOUT)
            if response.status_code == 200:
                content = json.loads(response.content)
                if content['status'] == 'success':
                    result = content['data']['result']
                    for item in result:
                        for metric in metrics:
                            if metric['instance'] == item['metric']['instance'] and \
                                    item['metric']['device'] == 'eth0':
                                metric['tx_bytes'] = item['values']
                                for tx_byte in metric['tx_bytes']:
                                    tx_byte[1] = int(tx_byte[1])
                else:
                    return []
            else:
                raise SystemError('Fail to get cpu usage from prometheus({}})'.format(url))
        except Exception as exc:
            raise SystemError('Fail to connect to prometheus server({}) '
                              'caused by {}'.format(self._endpoint, get_exception_traceback(exc)))

        return metrics

    def get_network_usages(self):
        """
        get network usages for each node
        :return:
        :return: (list(dict))
        [{
            "instance": "", # instance
            "device": "eth0", # network device
            "rx_bytes": [[timestamp, rx_byte], ...]
            "tx_bytes": [[timestamp, tx_byte], ...]
        }]
        """
        metrics = self.get_network_info()
        metrics = self.get_rx_bytes(metrics)
        metrics = self.get_tx_bytes(metrics)

        return metrics