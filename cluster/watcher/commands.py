import threading
from gw_agent import settings
from gw_agent.settings import get_logger
from cluster.common.type import ThreadState, ThreadControl
from utils.run import RunCommand
from multiprocessing import Queue


class CommandExecutor:
    """
    class CommandWatcher
    limitation: can not modify number of threads in runtime.
    only configure with editing gw_agent.settings.NUMBER_OF_EXECUTORS
    """

    _number_of_executor = 0
    _watch_threads = {}
    _wait_queue = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        """
        set executor thread pool
        """
        self._number_of_executor = settings.NUMBER_OF_COMMAND_EXECUTORS

        for i in range(0, self._number_of_executor):
            self._add_watch(i)

        self._wait_queue = Queue()
        self._logger = get_logger(__name__)

    def _add_watch(self, target):
        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'lock': threading.Lock(),
            'control': ThreadControl.EMPTY,
            'state': ThreadState.NOT_READY
        }

    def _watch_callback(self, target):
        """
        thread callback for watch request command, and execute it
        :return:
        """
        logger = self._logger
        self._init_thread(target)

        while True:
            command = self._get_command()
            logger.debug('[T{}] _get_command, command={}'.format(target, command))
            stdout, stderr = RunCommand.execute_shell_wait(command)
            print(stdout)

    def start(self):
        """
        start k8s resource watcher threads
        :return:
        """
        for _, value in self._watch_threads.items():
            if value['thread'] is None:
                value['thread'] = threading.Thread(target=self._watch_callback,
                                                   args=(value['target'],),
                                                   daemon=True)
                value['thread'].start()

    def put_command(self, command):
        """
        put command to wait queue
        :param command: (dict)
        :return:
        """
        self._wait_queue.put(command)

    def _get_command(self):
        """
        get command from wait queue
        caution: you must call it in worker thread
        :return:
        """
        return self._wait_queue.get()

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
