from typing import List

import six

from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.namespace import Namespace
from repository.model.k8s.node import Node
from repository.model.k8s.pod import Pod
from repository.model.k8s.service import Service


class ResourceBulk:
    """
    Resource model class
    - unit test:
      serialize test: success
      deserialize: success
    """
    fields = {
        'cluster_name': 'str',
        'nodes': 'list[Node]',
        'namespaces': 'list[Namespace]',
        'daemonsets': 'list[Daemonset]',
        'deployments': 'list[Deployment]',
        'pods': 'list[Pod]',
        'services': 'list[Service]',
    }

    def __init__(self, cluster_name):
        self.cluster_name = cluster_name
        self.nodes = []
        self.namespaces = []
        self.daemonsets = []
        self.deployments = []
        self.pods = []
        self.services = []

    @classmethod
    def validate_dict(cls, _dict: dict):
        """
        validate _dict
        """
        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict: dict) -> object:
        """
        Returns the model object
        """
        cls.validate_dict(_dict)

        instance = cls(_dict['cluster_name'])
        nodes = []
        namespaces = []
        daemonsets = []
        deployments = []
        pods = []
        services = []

        for key, value in _dict.items():
            if key == 'nodes':
                for item in value:  # list[Node]
                    nodes.append(Pod.to_object(item))
                setattr(instance, key, nodes)
            elif key == 'namespaces':
                for item in value:  # list[Namespace]
                    namespaces.append(Namespace.to_object(item))
                setattr(instance, key, namespaces)
            elif key == 'daemonsets':
                for item in value:  # list[Daemonset]
                    daemonsets.append(DaemonSet.to_object(item))
                setattr(instance, key, daemonsets)
            elif key == 'deployments':
                for item in value:  # list[Deployment]
                    deployments.append(Deployment.to_object(item))
                setattr(instance, key, deployments)
            elif key == 'pods':
                for item in value:  # list[Pod]
                    pods.append(Pod.to_object(item))
                setattr(instance, key, pods)
            elif key == 'services':
                for item in value:  # list[Service]
                    services.append(Service.to_object(item))
                setattr(instance, key, services)
            else:
                setattr(instance, key, value)

        return instance

    def to_dict(self) -> dict:
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in six.iteritems(self.fields):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def set_nodes(self, val: List[Node]):
        """
        set nodes
        :param val: (List[Node])
        :return:
        """
        self.nodes = val

    def get_nodes(self) -> List[Node]:
        """
        get nodes
        :return: (List[Node])
        """
        return self.nodes

    def set_namespaces(self, val: List[Namespace]):
        """
        set namespaces
        :param val: (List[Namespace])
        :return:
        """
        self.namespaces = val

    def get_namespaces(self) -> List[Namespace]:
        """
        get namespaces
        :return: (List[Namespace])
        """
        return self.namespaces

    def set_daemonsets(self, val: List[DaemonSet]):
        """
        set daemonsets
        :param val: (List[DaemonSet])
        :return:
        """
        self.daemonsets = val

    def get_daemonsets(self) -> List[DaemonSet]:
        """
        get daemonsets
        :return: (List[DaemonSet])
        """
        return self.daemonsets

    def set_deployments(self, val: List[Deployment]):
        """
        set deployments
        :param val: (List[Deployment])
        :return:
        """
        self.deployments = val

    def get_deployments(self) -> List[Deployment]:
        """
        get deployments
        :return: (List[Deployment])
        """
        return self.deployments

    def set_pods(self, val: List[Pod]):
        """
        set pods
        :param val: (List[Pod])
        :return: (List[Pod])
        """
        self.pods = val

    def get_pods(self) ->  (List[Pod]):
        """
        get pods
        :return: (List[Pod])
        """
        return self.pods

    def set_services(self, val: List[Service]):
        """
        set services
        :param val: (List[Service])
        :return:
        """
        self.services = val

    def get_services(self) -> List[Service]:
        """
        get services
        :return: (List[Service])
        """
        return self.services


