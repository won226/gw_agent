import threading

from cluster.common.type import Event
from cluster.event.object import EventObject
from cluster.notifier.notify import Notifier
from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger
from repository.cache.resources import ResourceRepository
from repository.common import k8s_client
from repository.common.type import PodStatus, Kubernetes


class ServiceStatusWatcher:
    """
    Watch service status update event
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
            # services = List[Service]
            services = repository.get_services()

            for service in services:
                try:
                    result = k8s_client.Connector().core_v1_api().read_namespaced_service_status(service.get_name(),
                                                                                                 service.get_namespace())
                except Exception as exc:
                    if exc.status == 404: # Service Not found
                        event_object = EventObject(event_type=Event.DELETED.value,
                                                   object_type=Kubernetes.SERVICE.value,
                                                   object_value=service)
                        notifier.put_event(event_object)
                    else:
                        logger.error('Fail to call read_namespaced_service_status() for service={}, ns={}, '
                                     'caused by {}'.format(service.get_name(),
                                                           service.get_namespace(),
                                                           get_exception_traceback(exc)))
                    continue
