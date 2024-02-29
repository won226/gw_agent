import ctypes
from threading import Thread

import os
import psutil


class ThreadUtil:

    @staticmethod
    def exit_process():
        current_system_pid = os.getpid()
        me = psutil.Process(current_system_pid)
        me.terminate()

    @staticmethod
    def raise_SystemExit_exception(thread: Thread) -> (bool, str):
        """
        raise SystemExist exception to thread
        :param thread: (threading.Thread)
        :return:
        (bool) True - success, False - fail
        (str) error message
        """
        if not thread.is_alive():
            return

        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)

        if res == 0:
            error_message = 'Invalid thread. Not found thread id'
            return False, error_message

        if res > 1:
            error_message = 'Fail to raise exception(SystemExit) to thread({})'.format(thread.ident)
            return False, error_message

        return True, None