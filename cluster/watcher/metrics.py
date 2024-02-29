import threading
import time

import os

from cluster.command.localhost import LocalHostCommand
from cluster.data_access_object import ClusterDAO
from gw_agent import settings
from gw_agent.settings import WATCH_NETWORK_INTERVAL
from cluster.common.type import Event
from cluster.event.object import EventObject
from cluster.notifier.notify import Notifier
from repository.cache.components import ComponentRepository
from repository.cache.metric import MetricRepository
from repository.cache.network import NetworkStatusRepository
from repository.cache.resources import ResourceRepository
from repository.common import prometheus_client
from repository.common.type import Metric, SubmarinerState
from repository.model.metric.cpu import CPUMetric
from repository.model.metric.memory import MemoryMetric
from repository.model.metric.network import NetworkMetric
from utils.dateformat import DateFormatter


class MetricWatcher:
    """
    Node, pod, multi-cluster metric watcher
    """
    _logger = None
    _prom_client = None
    _notifier = None
    _watch_threads = {}
    _last_node_metric_event_push = None
    _last_mcn_metric_event_push = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        """
        configure MetricWatcher
        :return:
        """
        self._logger = settings.get_logger(__name__)
        self._prom_client = prometheus_client.Connector()
        self._notifier = Notifier()
        self._add_watch(Metric.NODE_METRIC)
        self._add_watch(Metric.MULTI_CLUSTER_METRIC)

        # set self object to NetworkStatusRepository
        NetworkStatusRepository().set_mc_network_metric_watcher(self)

    def _add_watch(self, target):
        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'paused': False,
            'pause_cond': threading.Condition(threading.Lock()),
            'callback_access_time': None
        }

    def start(self):
        """
        start watcher threads
        :return:
        """
        for _, value in self._watch_threads.items():
            if value['target'] == Metric.MULTI_CLUSTER_METRIC:
                value['paused'] = True

            value['thread'] = threading.Thread(target=self._watch_callback, args=(value['target'],), daemon=True)
            value['thread'].start()

    def is_alive(self, target):
        """
        is target thread is alive
        :param target:
        :return:
        """
        return self._watch_threads[target]['thread'].is_alive()

    def set_callback_access_time(self, target):
        """
        set callback access time
        :param target:
        :return:
        """
        watch = self._watch_threads[target]
        watch['callback_access_time'] = time.time()

    def is_paused(self, target) -> bool:
        """
        is target thread is paused
        :param target:
        :return:
        """
        return self._watch_threads[target]['paused']

    def pause(self, target):
        """
        pause thread
        :param target:
        :return:
        """
        self._logger.debug('[PAUSE] MC NETWORK METRIC THREAD')
        watch = self._watch_threads[target]
        watch['paused'] = True
        # watch['pause_cond'].acquire()

    def resume(self, target):
        """
        resume thread
        :param target:
        :return:
        """
        self._logger.debug('[RESUME] MC NETWORK METRIC THREAD')
        watch = self._watch_threads[target]
        watch['pause_cond'].acquire()
        watch['paused'] = False
        watch['pause_cond'].notify()
        watch['pause_cond'].release()

    def get_pausing_time(self, target):
        """
        get paused duration
        :param target:
        :return:
        """
        watch = self._watch_threads[target]

        if not watch or not watch['callback_access_time']:
            return None

        return time.time() - watch['callback_access_time']

    def start_multi_cluster_network_metric_monitor(self):
        """
        start multi-cluster network metric monitor
        :return:
        """
        if self.is_paused(Metric.MULTI_CLUSTER_METRIC):
            self.resume(Metric.MULTI_CLUSTER_METRIC)

    def stop_multi_cluster_network_metric_monitor(self):
        """
        stop multi-cluster network metric monitor
        :return:
        """
        if not self.is_paused(Metric.MULTI_CLUSTER_METRIC):
            self.pause(Metric.MULTI_CLUSTER_METRIC)

    def _watch_callback(self, target):
        """
        thread callback for watch metric(node, multi-cluster network)
        :return:
        """
        logger = self._logger
        watch = self._watch_threads[target]

        while True:
            # thread pause
            with watch['pause_cond']:
                while watch['paused']:
                    watch['pause_cond'].wait()

            self.set_callback_access_time(target)

            if target == Metric.MULTI_CLUSTER_METRIC:
                self._collect_multi_cluster_network_metric(target)

            elif target == Metric.NODE_METRIC:
                self._collect_node_metric(target)

            else:
                logger.error('Invalid metric target')
                raise ValueError('[T:{}]Invalid metric target'.format(target.value))

            time.sleep(WATCH_NETWORK_INTERVAL)

    def _collect_multi_cluster_network_metric(self, target):
        """
        collect multi cluster network metric
        :return:
        """
        self._logger.debug('[CALL] MC METRIC THREAD')

        if not os.path.isdir(settings.SUBMARINER_DEV_PATH) or \
                not os.path.isfile(settings.SUBMARINER_RX) or \
                not os.path.isfile(settings.SUBMARINER_TX):
            return

        # get connected cluster name
        ok, remote_cluster_name, error_message = ClusterDAO.get_remote_cluster_name()
        if not ok:
            self._logger.error('Fail to get_remote_cluster_name(), caused by' + error_message)
            return

        if not remote_cluster_name:
            return

        # if gateway is connected bet/ multi-cluster
        if ComponentRepository().get_submariner_state() != SubmarinerState.GATEWAY_CONNECTED:
            return

        if ComponentRepository().get_submariner_state() == SubmarinerState.GATEWAY_CONNECTED:
            timestamp = time.time()

            # measure rx bytes
            ok, rx_byte, error = LocalHostCommand.get_network_rx_bytes(settings.SUBMARINER_DEV)
            if not ok:
                self._logger.error('Fail to read RX bytes in {}'.format(settings.SUBMARINER_DEV))
                return

            MetricRepository().set_mc_network_rx_byte(name=remote_cluster_name,
                                                      rx_byte=rx_byte,
                                                      timestamp=timestamp)

            # measure tx bytes
            ok, tx_bytes, error = LocalHostCommand.get_network_tx_bytes(settings.SUBMARINER_DEV)
            if not ok:
                self._logger.error('Fail to read TX bytes in {}'.format(settings.SUBMARINER_DEV))
                return

            MetricRepository().set_mc_network_tx_byte(name=remote_cluster_name,
                                                      tx_byte=tx_bytes,
                                                      timestamp=timestamp)
            # push event(period=5)
            current_ts = time.time()
            event_push = False

            if not self._last_mcn_metric_event_push:
                self._last_mcn_metric_event_push = current_ts
                event_push = True
            else:
                if current_ts - self._last_mcn_metric_event_push > 5:
                    event_push = True
                    self._last_mcn_metric_event_push = current_ts

            if event_push:
                # trigger event to notifier to send mc_network metric periodically
                event_object = EventObject(Event.ADDED.value,
                                           Metric.MULTI_CLUSTER_METRIC.value,
                                           MetricRepository().get_mc_network())

                self._notifier.put_event(event_object)
        return

    @staticmethod
    def get_node_exporter_pod_by_node(node_name):
        """
        get node-exporter pod hosted in a node
        :param node_name: (str)
        :return: (Pod)
        """
        pods = ResourceRepository().get_pods()

        for pod in pods:
            if pod.get_node_name() == node_name and 'node-exporter' in pod.get_name():
                return pod

        return None

    def _collect_node_metric(self, target):
        """
        collect node metric
        :return:
        """
        nodes = ResourceRepository().get_nodes()
        node_metrics = MetricRepository().get_nodes()
        n_nodes = len(nodes)
        n_node_metrics = len(node_metrics)
        node_names = []
        notifier = self._notifier
        logger = self._logger
        self._last_node_metric_event_push = None

        if n_nodes == 0:
            return
        else:
            if n_nodes == n_node_metrics:
                pass

            elif n_nodes > n_node_metrics:  # add node to node metric
                for node_metric in node_metrics:
                    node_names.append(node_metric.get_name())

                for node in nodes:
                    if node.get_name() not in node_names:
                        node_name = node.get_name()
                        MetricRepository().set_node(node_name)

            elif n_nodes < n_node_metrics:  # delete node from node metric
                deleted = False
                first = True

                for node in nodes:
                    node_names.append(node.get_name())

                while True:
                    if not deleted and not first:
                        break

                    first = False

                    for index in range(0, len(node_metrics)):
                        deleted = False

                        if node_metrics[index].get_name() not in node_names:
                            del node_metrics[index]
                            deleted = True
                            break

        """ set prometheus server endpoint setup """
        if not self._prom_client.is_ready():
            return

        """ set node instance(prometheus instance) to node metric """
        ok = False

        for node_metric in MetricRepository().get_nodes():
            node_name = node_metric.get_name()
            pod = self.get_node_exporter_pod_by_node(node_name)

            if pod is None:
                continue

            node_metric.set_instance('{}:{}'.format(pod.get_pod_ip(), settings.NODE_EXPORTER_PORT))
            ok = True

        if not ok:  # there are no node-exporter, skip collecting node metric
            return

        """ set_node_cpu_metric, CPUMetric """
        try:
            metrics = self._prom_client.get_cpu_usages()
        except SystemError as exc:
            error_message = ','.join(exc.args)
            if 'Fail to connect to prometheus server' in error_message:  # permit
                return

            else:
                logger.error('{} exception caused by {}'.format(exc.__class__.__name__, ','.join(exc.args)))
                return

        for metric in metrics:
            for node_metric in node_metrics:
                if metric['instance'] == node_metric.get_instance():
                    cpu_metric = CPUMetric(metric['total'], metric['usages'])
                    node_metric.set_cpu_metric(cpu_metric)

        """ set_node_mem_metric, MemoryMetric """
        try:
            metrics = self._prom_client.get_memory_usages()
        except Exception as exc:
            error_message = ','.join(exc.args)
            if 'Fail to connect to prometheus server' in error_message:  # permit
                return

            else:
                logger.error('{} exception caused by {}'.format(exc.__class__.__name__, ','.join(exc.args)))
                return

        for metric in metrics:
            for node_metric in node_metrics:
                if metric['instance'] == node_metric.get_instance():
                    memory_metric = MemoryMetric(metric['total'], metric['usages'])
                    node_metric.set_memory_metric(memory_metric)

        """ set_node_net_metric, NetworkMetric """
        try:
            metrics = self._prom_client.get_network_usages()
        except SystemError as exc:
            error_message = ','.join(exc.args)
            if 'Fail to connect to prometheus server' in error_message:  # permit
                return
            else:
                logger.error('{} exception caused by {}'.format(exc.__class__.__name__, ','.join(exc.args)))
                return

        for metric in metrics:
            for node_metric in node_metrics:
                if metric['instance'] == node_metric.get_instance():
                    if 'device' not in metric:
                        continue
                    if 'rx_bytes' not in metric:
                        continue
                    if 'tx_bytes' not in metric:
                        continue
                    network_metric = NetworkMetric(metric['device'], metric['rx_bytes'], metric['tx_bytes'])
                    node_metric.set_network_metric(network_metric)

        # push event(period=5)
        current_ts = time.time()
        event_push = False

        if not self._last_node_metric_event_push:
            self._last_node_metric_event_push = current_ts
            event_push = True
        else:
            if current_ts - self._last_node_metric_event_push > 5:
                event_push = True
                self._last_node_metric_event_push = current_ts

        if event_push:
            """ push node metric event """
            for node_metric in node_metrics:
                event = EventObject(Event.MODIFIED.value,
                                    Metric.NODE_METRIC.value,
                                    node_metric)
                notifier.put_event(event)
        return
