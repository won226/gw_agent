import json
import threading
import requests
import time

import urllib3

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger
from repository.cache.network import NetworkStatusRepository
from cluster.common.type import ThreadState, ThreadControl
from repository.common.type import ClusterSessionStatus


class Notifier:
    """
    Notify gedge-agent events to gedge-center
    """
    _netstat_repository = None
    _watch_threads = {}
    _cluster_id = None
    _wait_queue = []
    _wait_queue_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._logger = get_logger(__name__)
        self._netstat_repository = NetworkStatusRepository()
        self._number_of_executor = settings.NUMBER_OF_EVENT_NOTIFIERS
        self._notifier_wait_seconds = settings.WATCH_NOTIFIER_INTERVAL
        self._notifier_max_retransmission_counts = settings.WATCH_NOTIFIER_INTERVAL

        # register thread pool
        for i in range(0, self._number_of_executor):
            self._add_watch(i)

    def _add_watch(self, target):
        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'lock': threading.Lock(),
            'control': ThreadControl.EMPTY,
            'state': ThreadState.NOT_READY
        }

    def set_cluster_id(self, cluster_id):
        """
        set cluster id
        :return:
        """
        self._cluster_id = cluster_id

    def start(self):
        """
        start network status watcher threads
        :return:
        """
        if self._cluster_id is None:
            raise SystemError('cluster id is None. Must call set_cluster_id() before start()')

        for _, value in self._watch_threads.items():
            if value['thread'] is None:
                value['thread'] = threading.Thread(target=self._watch_callback,
                                                   args=(value['target'],),
                                                   daemon=True)
                value['thread'].start()

    def _watch_callback(self, target):
        """
        thread callback for watch request command, and execute it
        :return:
        """
        logger = self._logger
        self._init_thread(target)

        while True:
            # sleep until center connection is available
            session_status = self._netstat_repository.get_cluster_session_status()
            name = self._netstat_repository.get_center_network_name()

            # if cluster session is not established, wait continuously
            if session_status != ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
                time.sleep(self._notifier_wait_seconds)
                continue

            # get event
            event = self._get_event()
            if not event:
                time.sleep(self._notifier_wait_seconds)
                continue
            # logger.debug('[T{}] _get_event(), event={}'.format(target, event.to_dict()))

            # Push event to center
            for retry_count in range(0, self._notifier_max_retransmission_counts):
                session_status = self._netstat_repository.get_cluster_session_status()
                # when cluster session status is changed from CLUSTER_SESSION_ESTABLISHED to others
                if session_status != ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
                    break

                try:
                    url = name + '/api/agent/v1/cluster/{}/event'.format(self._cluster_id)
                    headers = {'Content-Type': 'application/json; charset=utf-8'}
                    response = requests.put(url=url,
                                            headers=headers,
                                            data=json.dumps(event.to_dict()),
                                            timeout=settings.REST_REQUEST_TIMEOUT)
                    if response.status_code != 200:
                        logger.error('Fail to send event.'
                                     '\nevent=\n{}\nreason={}'.format(event.to_dict(), response.reason))

                except (urllib3.exceptions.NewConnectionError,
                        requests.exceptions.ConnectionError,
                        ConnectionRefusedError):
                    # retry to transfer event
                    time.sleep(self._notifier_wait_seconds)
                    continue

                except Exception as exc:
                    self._logger.fatal('{}'.format(get_exception_traceback(exc)))

    def put_event(self, event):
        """
        put event to wait queue
        :param event: (EventObject)
        :return:
        """
        center_network_session_status = NetworkStatusRepository().get_cluster_session_status()

        if center_network_session_status != ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value:
            return

        self._wait_queue_lock.acquire()
        self._wait_queue.append(event)
        self._wait_queue_lock.release()

    def flush_events(self):
        """
        flush all queued events
        :return:
        """
        self._wait_queue_lock.acquire()
        self._wait_queue.clear()
        self._wait_queue_lock.release()

    def _get_event(self):
        """
        get command from wait queue
        caution: you must call it in worker thread
        :return:
        """
        val = None

        self._wait_queue_lock.acquire()
        if len(self._wait_queue) > 0:
            val = self._wait_queue.pop(0)
        self._wait_queue_lock.release()

        return val

    def _send_to_thread(self, target, command):
        """
        send command to thread
        :param target: (string); from < class repository.common.type.Kubernetes >
        :param command: (string); in THREAD_CONTROL_TYPES
        :return: (bool); True - success to deliver command, False - Fail to deliver command
        """
        command = ThreadControl.to_enum(command)

        if command == ThreadControl.UNKNOWN:
            raise ValueError('Unknown thread control')
        if target not in self._watch_threads.keys():
            return False
        if self._watch_threads[target]['state'] is not ThreadState.RUNNING:
            return False

        self._watch_threads[target]['lock'].acquire()
        self._watch_threads[target]['control'] = command
        self._watch_threads[target]['lock'].release()

        return True

    def _receive_command(self, target):
        """
        receive command in thread
        :param target: (string); from < class repository.common.type.Kubernetes >
        :return: (string); in THREAD_CONTROL_TYPES
        """
        self._watch_threads[target]['lock'].acquire()
        command = self._watch_threads[target]['control']

        if command is not ThreadControl.EMPTY:
            self._watch_threads[target]['state'] = ThreadState.BUSY
        self._watch_threads[target]['lock'].release()

        return command

    def _init_thread(self, target):
        """ called it when enter a thread callback """
        self._watch_threads[target]['lock'].acquire()
        self._watch_threads[target]['state'] = ThreadState.RUNNING
        self._watch_threads[target]['control'] = ThreadControl.EMPTY
        self._watch_threads[target]['lock'].release()

    def _complete_thread_control(self, target):
        """ called it when a thread complete thread control """
        self._watch_threads[target]['lock'].acquire()
        self._watch_threads[target]['state'] = ThreadState.RUNNING
        self._watch_threads[target]['control'] = ThreadControl.EMPTY
        self._watch_threads[target]['lock'].release()
