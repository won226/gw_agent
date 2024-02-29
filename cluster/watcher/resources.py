"""
    desc: watcher methods for cluster resource
    (nodes, namespaces, pods, deployments, daemonsets, services)
"""
import threading
import time

import urllib3
from kubernetes.watch import watch

from gw_agent.settings import get_logger
from gw_agent.settings import KUBE_API_REQUEST_TIMEOUT
from cluster.event.object import EventObject
from cluster.notifier.notify import Notifier
from repository.common.k8s_client import Connector
from repository.cache.resources import ResourceRepository
from repository.common.type import Kubernetes
from cluster.common.type import ThreadState, ThreadControl
from cluster.common.type import Event


class ResourceWatcher:
    """
    Watch kubernetes resources(Node, Namespace, Pod, Deployment, DaemonSet, Service) event
    and notify it to gedge-center with notifier
    """
    _connector = None
    _notifier = None
    _core_v1_api = None
    _app_v1_api = None
    _kube_api_watch = None
    _repository = None
    _watch_threads = {}
    _all_threads_started = False
    _watch_condition = threading.Condition()

    _finalizer_free_namespaces = ['submariner-operator',
                                  'submariner-k8s-broker']

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._notifier = Notifier()
        self._logger = get_logger(__name__)
        self._logger.info(__name__ + ' is started.')

        # k8s api
        self._connector = Connector()
        self._core_v1_api = self._connector.core_v1_api()
        self._app_v1_api = self._connector.app_v1_api()
        self._watch = watch.Watch()

        # k8s resource repository
        self._repository = ResourceRepository()

        # add watch to gather k8s event
        self._add_watch(Kubernetes.NODE)
        self._add_watch(Kubernetes.NAMESPACE)
        self._add_watch(Kubernetes.POD)
        self._add_watch(Kubernetes.DEPLOYMENT)
        self._add_watch(Kubernetes.DAEMONSET)
        self._add_watch(Kubernetes.SERVICE)

        self._all_threads_started = True

    def _add_watch(self, target):
        """
        thread callback for watch k8s resource
        :param target: (string); from < class repository.common.type.Kubernetes >
        :return:
        """
        api = None
        if target is Kubernetes.NODE:
            api = self._core_v1_api.list_node
        elif target is Kubernetes.NAMESPACE:
            api = self._core_v1_api.list_namespace
        elif target is Kubernetes.POD:
            api = self._core_v1_api.list_pod_for_all_namespaces
        elif target is Kubernetes.DEPLOYMENT:
            api = self._app_v1_api.list_deployment_for_all_namespaces
        elif target is Kubernetes.DAEMONSET:
            api = self._app_v1_api.list_daemon_set_for_all_namespaces
        elif target is Kubernetes.SERVICE:
            api = self._core_v1_api.list_service_for_all_namespaces
        else:
            ValueError('Invalid resource type')

        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'api': api,
            'lock': threading.Lock(),
            'condition': self._watch_condition,
            'state': ThreadState.NOT_READY,
            'control': ThreadControl.EMPTY,
            'data_ready': False
        }

    def data_ready(self):
        """
        check kubernetes resource data is ready
        :return:
        """
        if not self._all_threads_started:
            return False

        for key, value in self._watch_threads.items():
            if value['data_ready'] is False:
                return False

        return True

    def start(self):
        """
        start k8s resource watcher threads
        :return:
        """
        for _, value in self._watch_threads.items():
            if value['thread'] is None:
                value['thread'] = threading.Thread(target=self._watch_callback,
                                                   args=(value['target'], value['api'],),
                                                   daemon=True)
                value['thread'].start()

        self._all_threads_started = True

    def stop(self):
        """
        stop all watch threads
        :return:
        """
        self._all_threads_started = False

        for key, value in self._watch_threads.items():
            if self._watch_threads[key]['thread'] is not None:
                self._send_to_thread(key, ThreadControl.THREAD_EXIT)
                self._watch_threads[key]['thread'].join()
                self._watch_threads[key]['thread'] = None
                self._watch_threads[key]['state'] = ThreadState.NOT_READY
                self._logger.info('success to join thread, thread={}'.format(key))

    def _set_data_ready(self, target):
        """
        set data ready
        :param target: (string); from < class repository.common.type.Kubernetes >
        :return:
        """
        self._watch_threads[target]['data_ready'] = True

    def is_all_resource_data_ready(self) -> bool:
        """
        is all resource data ready?
        :return: (bool)
        """
        for key, value in self._watch_threads.items():
            if not self._watch_threads[key]['data_ready']:
                return False

        return True

    def _send_to_thread(self, target, command):
        """
        send command to thread
        :param target: (str); from < class repository.common.type.Kubernetes >
        :param command: (str); ThreadControl(Enum)
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
        :param target: (str); from < class repository.common.type.Kubernetes >
        :return: (str); in THREAD_CONTROL_TYPES
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

    def _set_thread_to_suspend(self, target):
        """ set thread to suspend state """
        self._watch_threads[target]['lock'].acquire()
        self._watch_threads[target]['state'] = ThreadState.SUSPENDED
        self._watch_threads[target]['lock'].release()

    def resume_all_watches(self):
        """
        resume thread from conditional wait
        :return:
        """
        with self._watch_condition:
            self._watch_condition.notifyAll()

    def suspend_all_watches(self):
        """
        control thread to conditional wait
        :return:
        """
        for target in self._watch_threads.keys():
            self._send_to_thread(target, ThreadControl.SUSPEND)

        # wait all watches are suspended
        while True:
            all_threads_suspended = True

            for target, value in self._watch_threads.items():
                if value['state'] != ThreadState.SUSPENDED:
                    all_threads_suspended = False
                    break

            if not all_threads_suspended:
                time.sleep(0.1)
            else:
                return

    def _watch_callback(self, target, api):
        """
        thread callback for watch k8s resources
        :return:
        """
        logger = self._logger

        if not Kubernetes.validate(target):
            raise ValueError('Invalid K8S target(resource type)')

        first = True
        previous_events = 0
        self._init_thread(target)
        loop_counter = 0

        while True:
            current_events = 0
            # logger.debug('[{}]ResourceWatcher()._watch_callback({})-------------'.format(loop_counter, target))

            try:
                for event in self._watch.stream(api, _request_timeout = KUBE_API_REQUEST_TIMEOUT):
                    current_events += 1

                    if first:
                        self._dispatch_event(event)
                    else:
                        if current_events > previous_events:
                            self._dispatch_event(event)

            except urllib3.exceptions.ReadTimeoutError:
                """ event watch timeout """
                first = False
                loop_counter += 1

                if loop_counter > 1:
                    self._set_data_ready(target)

                previous_events = current_events

                """ process thread control command """
                command = ThreadControl.to_enum(self._receive_control(target))

                if command == ThreadControl.UNKNOWN:
                    logger.error('[T:{}] Unknown thread command'.format(target))

                if command == ThreadControl.SUSPEND:
                    with self._watch_condition:
                        self._set_thread_to_suspend(target)
                        self._watch_condition.wait()
                        self._complete_thread_control(target)
                    continue

                if command == ThreadControl.IGNORE:
                    continue

                if command == ThreadControl.THREAD_EXIT:
                    logger.info('[T:{}] receive {} command'.format(target, command))
                    return

                if command == ThreadControl.ADD_HOOK_METHOD:
                    # not supported
                    self._complete_thread_control(target)
                    pass

                if command == ThreadControl.REMOVE_HOOK_METHOD:
                    # not supported
                    self._complete_thread_control(target)
                    pass

            # except urllib3.exceptions.MaxRetryError:
            #     print('Mac Retry Error')
            #     self._connector.reconnect()

    def _dispatch_event(self, event):
        """
        dispatch event
        :param event: (<class 'dict'>); watch event
        :return:
        """
        logger = self._logger
        notifier = self._notifier

        event_type = event['type']
        item = event['object']
        raw_object = event['raw_object']
        name = item.metadata.name
        kind = item.kind
        # logger.debug('[T:{}] type={}, name={}'.format(kind, event_type, name))
        event_type = Event.to_enum(event_type)

        # ''' removes finalizers for stuck namespaces
        #     i.e., submariner-operator, submariner-k8s-broker '''
        # if 'finalizers' in raw_object['spec'] and kind == 'Namespace':
        #     if name in self._finalizer_free_namespaces:
        #         raw_object['spec']['finalizers'] = []
        #         self._core_v1_api.replace_namespace_finalize(name, raw_object)

        if event_type == Event.ADDED or event_type == Event.MODIFIED:
            obj, kind = self._repository.to_model(item)
            self._repository.create_or_update(obj)

        elif event_type == Event.ERROR or event_type == Event.BOOKMARK:
            # BOOKMARK event treated the same as ERROR
            # described in (< class kubernetes.watch.Watch().unmarshal_event() >)
            logger.error('[{}] type={}, name={}, raw_object={}'.format(kind, event_type, name, raw_object))
            obj, kind = self._repository.to_model(item)
            self._repository.create_or_update(obj)

        elif event_type == Event.DELETED:
            obj, kind = self._repository.to_model(item)
            self._repository.delete(item)

        else:
            logger.error('[T:{}] Unknown event, type={}, name={}'.format(kind, event_type, name))
            return

        event_object = EventObject(event_type=event_type.value,
                                   object_type=kind,  # EventObject deliver 'kind' field
                                   object_value=obj)

        notifier.put_event(event_object)
