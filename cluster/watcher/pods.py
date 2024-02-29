import threading

from cluster.common.type import Event
from cluster.event.object import EventObject
from cluster.notifier.notify import Notifier
from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger
from repository.cache.resources import ResourceRepository
from repository.common import k8s_client
from repository.common.type import Kubernetes


class PodStatusWatcher:
    """
    Watch pod status update event
    and notify it to gedge-center with notifier
    """

    _thread = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._notifier = Notifier()
        self._logger = get_logger(__name__)
        self._logger.info(__name__ + ' is started.')

    def start(self):
        self._thread = threading.Thread(target=self._watch_callback)
        self._thread.start()

    def _watch_callback(self):
        """
        thread callback for watch pod status check
        :return:
        """
        repository = ResourceRepository()
        notifier = Notifier()
        logger = self._logger

        while True:
            # pods = List[Pod]
            pods = repository.get_pods()

            for pod in pods:
                # if pod.get_state() == PodStatus.PENDING.value:
                try:
                    result = k8s_client.Connector().core_v1_api().read_namespaced_pod(pod.get_name(),
                                                                                      pod.get_namespace())
                except Exception as exc:
                    if exc.status == 404: # Pod Not found
                        event_object = EventObject(event_type=Event.DELETED.value,
                                                   object_type=Kubernetes.POD.value,
                                                   object_value=pod)
                        notifier.put_event(event_object)
                    else:
                        logger.error('Fail to call read_namespaced_pod() for pod={}, ns={}, '
                                     'caused by {}'.format(pod.get_name(),
                                                           pod.get_namespace(),
                                                           get_exception_traceback(exc)))
                    continue

                if result.status.phase != pod.get_state(): # update
                    obj = ResourceRepository().to_pod_model(result)
                    ResourceRepository().create_or_update(obj)

                    event_object = EventObject(event_type=Event.MODIFIED.value,
                                               object_type=Kubernetes.POD.value,
                                               object_value=obj)
                    notifier.put_event(event_object)


