import os
import gc
import threading
import time
import psutil

from gw_agent import settings
from utils.threads import ThreadUtil

logger = settings.get_logger(__name__)

class MemoryManager(threading.Thread):
    """
    param: interval: (int) garbage collector calling interval(default=600s)
    """
    def __init__(self, interval:int=30):
        self.interval = interval
        threading.Thread.__init__(self)

    def run(self):
        logger.info("memory manager is started. interval={}s".format(self.interval))
        if not gc.isenabled():
            gc.enable()
        logger.info("GC enabled")

        while True:
            time.sleep(self.interval)

            # Memory circuit break
            # if memory usage is over threshold(settings.MEMORY_CIRCUIT_BREAK_THRESHOLD),
            # quit gwlink-manager automatically
            system_memory_usage = psutil.virtual_memory().percent

            if settings.DISPLAY_PROCESS_MEMORY:
                memory_used_mib = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
                logger.info("Process memory = {:.2f}MiB".format(memory_used_mib))

            if settings.MEMORY_CIRCUIT_BREAK_ENABLED:
                if settings.MEMORY_CIRCUIT_BREAK_THRESHOLD < system_memory_usage:
                    memory_used_mib = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
                    logger.error("Terminate gwlink-manager caused by occurring memory circuit break.\n"
                                 "    Memory circuit break threshold = {}%\n"
                                 "    System memory usage = {:.2f}% \n"
                                 "    System total memory = {:.2f}MiB \n"
                                 "    Process memory = {:.2f}MiB \n".format(
                        settings.MEMORY_CIRCUIT_BREAK_THRESHOLD,
                        system_memory_usage,
                        psutil.virtual_memory().total / 1024 ** 2,
                        memory_used_mib
                    ))
                    ThreadUtil.exit_process()
