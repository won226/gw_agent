import threading
import time

from gw_agent import settings
from cluster.command.kubernetes import KubeCommand
from cluster.common.type import ThreadControl, ThreadState, Event
from cluster.event.object import EventObject
from cluster.notifier.notify import Notifier
from cluster.watcher.resources import ResourceWatcher
from repository.cache.components import ComponentRepository
from repository.cache.resources import ResourceRepository
from repository.common.type import Common, Kubernetes


class ComponentWatcher:
    """
    Watch cluster components (kube, prometheus, node-exporter, submariner, nfs-server)
    """

    _notifier = None
    _watch_threads = {}
    _netstat_repository = None
    _nfs_server_connector = None
    _ready = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()
        return cls._instance

    def _config(self):
        """
        configure NetworkWatcher
        :return:
        """
        self._logger = settings.get_logger(__name__)
        self._notifier = Notifier()
        self._add_watch(Common.COMPONENT_WATCHER)
        self._add_watch(Common.PROVISONER)

    def _add_watch(self, target):
        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'lock': threading.Lock(),
            'control': ThreadControl.EMPTY,
            'state': ThreadState.NOT_READY
        }

    def start(self):
        """
        start network status watcher threads
        :return:
        """
        for _, value in self._watch_threads.items():
            if value['thread'] is None:
                value['thread'] = threading.Thread(target=self._watch_callback,
                                                   args=(value['target'],),
                                                   daemon=True)
                value['thread'].start()

    def stop(self):
        """
        stop all watch threads
        :return:
        """
        for key, value in self._watch_threads.items():
            if self._watch_threads[key]['thread'] is not None:
                self._send_to_thread(key, ThreadControl.THREAD_EXIT)
                self._watch_threads[key]['thread'].join()
                self._watch_threads[key]['thread'] = None
                self._watch_threads[key]['state'] = ThreadState.NOT_READY
                self._logger.debug('success to join thread, thread={}'.format(key))

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

    def _receive_control(self, target):
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
        """
        called it when enter a thread callback
        """
        self._watch_threads[target]['lock'].acquire()
        self._watch_threads[target]['state'] = ThreadState.RUNNING
        self._watch_threads[target]['control'] = ThreadControl.EMPTY
        self._watch_threads[target]['lock'].release()

    def _complete_thread_control(self, target):
        """
        called it when a thread complete thread control
        """
        self._watch_threads[target]['lock'].acquire()
        self._watch_threads[target]['state'] = ThreadState.RUNNING
        self._watch_threads[target]['control'] = ThreadControl.EMPTY
        self._watch_threads[target]['lock'].release()

    def _watch_callback(self, target):
        """
        thread callback for watch network(cluster, multi-cluster network, center connection)
        :return:
        """
        logger = self._logger
        self._init_thread(target)

        while True:
            if target == Common.COMPONENT_WATCHER:
                self._collect_cluster_components()

            elif target == Common.PROVISONER:
                self._provision_cluster_components()

            else:
                logger.error('Invalid component watcher target')
                raise ValueError('[T:{}]Invalid component target'.format(target.value))

            command = ThreadControl.to_enum(self._receive_control(target))

            if command == ThreadControl.UNKNOWN:
                logger.error('[T:{}] Unknown thread command'.format(target))

            if command == ThreadControl.IGNORE:
                continue

            if command == ThreadControl.THREAD_EXIT:
                logger.debug('[T:{}] receive {} command'.format(target, command))
                return

            if command == ThreadControl.ADD_HOOK_METHOD:
                self._complete_thread_control(target)
                pass

            if command == ThreadControl.REMOVE_HOOK_METHOD:
                self._complete_thread_control(target)
                pass

            time.sleep(settings.WATCH_COMPONENT_INTERVAL)

    def _collect_cluster_components(self):
        """
        collector for gedge-agent managed component
        - nfs-server-{local_cluster_id}, nfs-client-{local_cluster_id},
        - prometheus, node-exporter, k8s-state-metric
        - after join-broker
        - nfs-client-{remote_cluster_id} for remote broker connected env.
        :return:
        """
        cluster_id = ResourceRepository().get_cluster_id()
        master_name = KubeCommand.get_master_name()

        ''' initialize gedge components '''
        if not cluster_id or not master_name or not self._ready:
            # check whether resourceWatcher resource data is ready
            if not ResourceWatcher().data_ready():
                return

            # initialize ComponentRepository()
            ComponentRepository().initialize(cluster_id, master_name)
            self._ready = True

        ''' audit gedge components(validate and provision) '''
        ComponentRepository().audit_gedge_components()
        # ComponentRepository().print_cluster_component_conditions()

        ''' push event to center '''
        conditions = ComponentRepository().get_conditions()
        event_object = EventObject(Event.MODIFIED.value,
                                   Kubernetes.COMPONENTS.value,
                                   conditions)

        Notifier().put_event(event_object)

    @classmethod
    def _provision_cluster_components(cls):
        """
        provisioner for cluster components
        :return:
        """
        ComponentRepository().provision_gedge_components()