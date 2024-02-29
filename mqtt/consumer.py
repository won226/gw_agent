import threading
from gw_agent import settings
import pika

from gw_agent.common.error import get_exception_traceback
from mqtt.dispatch import Dispatcher
from utils.threads import ThreadUtil


class Consumer:
    """
    MQTT Request consumer(receiver) from CEdge-center
    """
    _channel = None
    _url = None
    _port = None
    _id = None
    _password = None
    _queue = None
    _vhost = None
    _logger = None
    _thread_pool = []
    _thread_pool_capacity = settings.NUMBER_OF_MQTT_CONSUMERS
    _route = {
        # 'path': __callback_method
    }

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._logger = settings.get_logger(__name__)
        Dispatcher().register_router()

    def start(self, url: str, port: int, user: str, password: str, vhost: str, cluster_id: str):
        """
        consumer thread pool start
        :param url: (str)
        :param port: (str)
        :param user: (str)
        :param password: (str)
        :param vhost: (str)
        :param cluster_id: (str); my cluster's id
        :return:
        """
        self._url = url
        self._port = port
        self._id = user
        self._password = password
        self._vhost = vhost
        self._queue = cluster_id

        # thread pool creation
        for i in range(0, self._thread_pool_capacity):
            item = {
                'thread': threading.Thread(target=self._callback_consumer,
                                           args=(i,),
                                           daemon=True),
                'lock': threading.Lock(),
                'connection': None
            }
            self._thread_pool.append(item)
            item['thread'].start()

    def stop(self):
        """
        exit all threads in thread pool
        :return:
        """
        for i in range(0, self._thread_pool_capacity):
            connection = self._thread_pool[i]['connection']
            if connection is not None:
                connection.close()

    @classmethod
    def __callback_on_message(cls, channel, method, properties, body):
        """
        consume message callback
        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        return Dispatcher().dispatch(body)

    def _callback_consumer(self, index):
        """
        callback
        :param index: (int) thread pool index
        :return:
        """
        thread_data = self._thread_pool[index]
        credentials = pika.PlainCredentials(self._id, self._password)
        connection = None

        while True:
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(self._url, self._port, self._vhost, credentials))
            except Exception as exc:
                # error_message = get_exception_traceback(exc)
                self._logger.error('Fail to pika.BlockingConnection')
                # ThreadUtil.exit_process()

            if not connection:
                self._logger.error('Fail to connect AMQP broker({}:{}). '
                                   'Terminate GEdge-agent.'.format(self._url, self._port))
                # ThreadUtil.exit_process()

            thread_data['connection'] = connection
            channel = connection.channel()
            channel.queue_declare(queue=self._queue)
            channel.basic_consume(queue=self._queue,
                                  on_message_callback=Consumer.__callback_on_message,
                                  auto_ack=True)

            self._logger.info('MQTT consumer thread[{}] is started: queue[{}]'.format(index, self._queue))

            try:
                channel.start_consuming()
            except Exception:
                self._logger.error('Fail to channel.start_consuming()')
            channel.close()

            self._logger.info('MQTT consumer thread[{}] is re-initialized: queue[{}]'.format(index, self._queue))

