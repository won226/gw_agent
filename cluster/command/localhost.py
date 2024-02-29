import time
from multiprocessing import Process, Queue

import os, threading

from gw_agent import settings
from gw_agent.common.error import get_exception_traceback
from utils.fileutils import FileUtil
from utils.run import RunCommand
from utils.threads import ThreadUtil
from utils.validate import Validator

logger = settings.get_logger(__name__)
IFCONFIG = '/sbin/ifconfig'
NETPLAN = '/usr/sbin/netplan'


class LocalHostCommand:

    @staticmethod
    def get_iface(node_ip: str) -> str:
        """
        get node's network interface
        :param node_ip: (str)
        :return: (str)
        """
        cmdline = IFCONFIG + ' | grep -B1 {} | grep -o \"^\w*\"'.format(node_ip)

        ok, stdout, stderr = RunCommand.execute_bash_wait(cmdline)
        if not ok:
            logger.error(stderr)
            return None

        return stdout.decode('utf-8').strip()

    @staticmethod
    def get_network_rx_bytes(iface: str) -> (bool, int, str):
        """
        get network rx bytes
        :param iface: (str) interface name
        :return:
        (bool) True - success, False - fail
        (int) receive bytes
        (str) error reason
        """
        statistics_file = '/sys/class/net/{iface}/statistics/rx_bytes'.format(iface=iface)

        if not os.path.isfile(statistics_file):
            return False, -1, 'Not found interface ' + iface

        try:
            data = FileUtil.read_text_file(statistics_file)
        except Exception as exc:
            return False, -1, get_exception_traceback(exc)

        if not Validator.is_enable_cast_to_int(data):
            return False, -1, 'Invalid value({}) in {}'.format(data, statistics_file)

        return True, int(data), None

    @staticmethod
    def get_network_tx_bytes(iface: str) -> (bool, int, str):
        """
        get network tx bytes
        :param iface: (str) interface name
        :return:
        (bool) True - success, False - fail
        (int) receive bytes
        (str) error reason
        """
        statistics_file = '/sys/class/net/{iface}/statistics/tx_bytes'.format(iface=iface)

        if not os.path.isfile(statistics_file):
            return False, -1, 'Not found interface ' + iface

        try:
            data = FileUtil.read_text_file(statistics_file)
        except Exception as exc:
            return False, -1, get_exception_traceback(exc)

        if not Validator.is_enable_cast_to_int(data):
            return False, -1, 'Invalid value({}) in {}'.format(data, statistics_file)

        return True, int(data), None

    @staticmethod
    def network_restart():
        """
        restart network
        :return:
        """
        cmdline = NETPLAN + ' apply'

        return RunCommand.execute_bash_wait(cmdline)

    @staticmethod
    def remove_agent() -> (bool, str):
        """
        remove agent
        :return: (bool) True - success, False - fail
        """
        ThreadUtil.exit_process()

        return True, None

    @staticmethod
    def is_directory_accessible(path: str, timeout: int = 0) -> (bool, str):
        """
        check whether directory is accessible
        :param path: (str) directory absolute path
        :param timeout: (int) blocking seconds
        :return:
        """
        cmdline = "timeout {timeout} ls {path}".format(timeout=timeout, path=path)
        ok, stdout, stderr = RunCommand.execute_shell_wait(cmdline)

        if not ok:
            return False, stderr

        return True, None

