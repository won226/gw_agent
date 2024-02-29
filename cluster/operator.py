import sys

import os
from configparser import ConfigParser

from cluster.watcher.pods import PodStatusWatcher
from cluster.watcher.services import ServiceStatusWatcher
from gw_agent import settings
from cluster.command.submariner import SubmarinerCommand
from cluster.common.type import Event
from cluster.data_access_object import ClusterDAO
from cluster.event.object import EventObject
from cluster.notifier.notify import Notifier
from cluster.watcher.commands import CommandExecutor
from cluster.watcher.components import ComponentWatcher
from cluster.watcher.metrics import MetricWatcher
from cluster.watcher.networks import NetworkWatcher
from cluster.watcher.resources import ResourceWatcher
from mqtt.consumer import Consumer
from repository.cache.network import NetworkStatusRepository
from repository.cache.resources import ResourceRepository
from utils.memory_manage import MemoryManager
from utils.threads import ThreadUtil

logger = settings.get_logger(__name__)

def start():
    # if subctl is not installed, install to host
    if not os.path.isfile('/sbin/subctl'):
        ok, stdout, stderr = SubmarinerCommand.deploy_subctl()
        if not ok:
            logger.error('Fail to install subctl caused by {}'.format(stderr))
            ThreadUtil.exit_process()

    # read config.ini file (config.ini file is created at docker entry point)
    config = ConfigParser()
    config.read(settings.PROPERTY_FILE)
    cluster_id = config.get('ClusterSection', 'cluster_id')
    center_name = config.get('ClusterSection', 'center')
    center_http = config.get('ClusterSection', 'http')
    center_https = config.get('ClusterSection', 'https')
    center_amqp_ip = config.get('ClusterSection', 'amqp_ip')
    center_amqp_port = config.get('ClusterSection', 'amqp_port')
    center_amqp_id = config.get('ClusterSection', 'amqp_id')
    center_amqp_pwd = config.get('ClusterSection', 'amqp_pwd')
    center_amqp_vhost = config.get('ClusterSection', 'amqp_vhost')
    center_amqp_url = '{}:{}'.format(center_amqp_ip, center_amqp_port)
    center_token = config.get('ClusterSection', 'token')

    # check broker_info directory
    if not os.path.isdir(settings.LOCAL_BROKER_INFO):
        os.makedirs(settings.LOCAL_BROKER_INFO, exist_ok=True)

    if not os.path.isdir(settings.REMOTE_BROKER_INFO):
        os.makedirs(settings.REMOTE_BROKER_INFO, exist_ok=True)

    # setup cluster table
    if not cluster_id:
        logger.error('Not found cluster_id. See cluster_id in static/config.ini file')
        ThreadUtil.exit_process()

    ok, error_message = ClusterDAO.initialize_cluster(cluster_id)
    if not ok:
        logger.error('Failed in ClusterDAO.initialize_cluster({}), caused by {}'.format(cluster_id, error_message))
        ThreadUtil.exit_process()

    # setup multiClusterConfig table
    ok, mc_config, error_message = ClusterDAO.get_multi_cluster_config()

    if not ok:
        logger.error('Failed in ClusterDAO.get_multi_cluster_config(), caused by ' + error_message)
        sys.exit(1)

    if not mc_config.mc_config_state:
        ok, error_message = ClusterDAO.reset_multi_cluster_config_request()
        if not ok:
            logger.error('Failed in ClusterDAO.reset_multi_cluster_config_request(), '
                         'caused by ' + error_message)
            sys.exit(1)

    # start memory manager
    MemoryManager().start()

    # start notifier
    Notifier().set_cluster_id(cluster_id)
    Notifier().start()
    Notifier().put_event(EventObject(Event.AGENT_INIT.value, None, None))

    # start mqtt consumer
    Consumer().start(center_amqp_ip,
                     center_amqp_port,
                     center_amqp_id,
                     center_amqp_pwd,
                     center_amqp_vhost,
                     cluster_id)

    # set cluster id
    ResourceRepository().set_cluster_id(cluster_id)

    # network status repository
    NetworkStatusRepository().set_center_network(center_name)
    NetworkStatusRepository().set_center_network_http(center_name, center_http)
    NetworkStatusRepository().set_center_network_https(center_name, center_https)
    NetworkStatusRepository().set_center_network_ampq(center_name, center_amqp_url)
    NetworkStatusRepository().set_center_network_token(center_name, center_token)

    # start kubernetes resource watcher
    ResourceWatcher().start()

    # Pod Status watcher
    PodStatusWatcher().start()

    # Service Status watcher
    ServiceStatusWatcher().start()

    # start command execute thread pool
    CommandExecutor().start()

    # start network status watcher(center_network, mc_network)
    NetworkWatcher().start()

    # start metric watcher(node, mc_network)
    MetricWatcher().start()

    # start component watcher
    ComponentWatcher().start()

    logger.info('[START] gedge-agent.')