import six

from repository.common.type import Kubernetes, Metric, NetStat, Common
# from repository.model.common.delete import DeleteModel
from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.namespace import Namespace
from repository.model.k8s.node import Node
from repository.model.k8s.pod import Pod
from repository.model.k8s.service import Service
from repository.model.metric.endpoint import EndpointNetworkMetric
from repository.model.metric.multi_cluster import MultiClusterMetric
from repository.model.metric.node import NodeMetric
from repository.model.netstat.multi_cluster import MultiClusterNetwork
from repository.model.netstat.service import MultiClusterService, ServiceExport, ServiceImport


class EventObject:
    """
    class for event transfer object
    """

    fields = {
        'event_type': 'str',
        'object_type': 'str',
        'object_value': 'object',
    }

    event_type = None
    object_type = None
    object_value = None

    def __init__(self, event_type, object_type, object_value):
        """
        EventObject()
        :param event_type:
            (str) a Enum in class cluster.common.type.Event(Enum)
        :param object_type:
            (str) class(Enum)'s value in class cluster.repository.common.type
        :param object_value:
        """
        self.event_type = event_type
        self.object_type = object_type
        self.object_value = object_value

    def to_dict(self):
        """Returns the model properties as a dict"""
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

    @classmethod
    def to_object(cls, _dict):
        # todo: test
        # check repository.common.type.Kubernetes(Enum)
        if _dict['object_type'] == Kubernetes.NODE.value:
            obj = Node.to_object(_dict['object_value'])
        elif _dict['object_type'] == Kubernetes.POD.value:
            obj = Pod.to_object(_dict['object_value'])
        elif _dict['object_type'] == Kubernetes.NAMESPACE.value:
            obj = Namespace.to_object(_dict['object_value'])
        elif _dict['object_type'] == Kubernetes.DEPLOYMENT.value:
            obj = Deployment.to_object(_dict['object_value'])
        elif _dict['object_type'] == Kubernetes.DAEMONSET.value:
            obj = DaemonSet.to_object(_dict['object_value'])
        elif _dict['object_type'] == Kubernetes.NAMESPACE.value:
            obj = Namespace.to_object(_dict['object_value'])
        elif _dict['object_type'] == Kubernetes.SERVICE.value:
            obj = Service.to_object(_dict['object_value'])

        # check repository.common.type.Metric(Enum)
        elif _dict['object_type'] == Metric.NODE_METRIC.value:
            obj = NodeMetric.to_object(_dict['object_value'])
        elif _dict['object_type'] == Metric.MULTI_CLUSTER_METRIC.value:
            obj = MultiClusterMetric.to_object(_dict['object_value'])
        elif _dict['object_type'] == NetStat.MULTI_CLUSTER_NETWORK.value:
            obj = MultiClusterNetwork.to_object(_dict['object_value'])
        elif _dict['object_type'] == NetStat.MULTI_CLUSTER_SERVICE.value:
            obj = MultiClusterService.to_object(_dict['object_value'])
        elif _dict['object_type'] == NetStat.SERVICE_EXPORT.value:
            obj = ServiceExport.to_object(_dict['object_value'])
        elif _dict['object_type'] == NetStat.SERVICE_IMPORT.value:
            obj = ServiceImport.to_object(_dict['object_value'])
        elif _dict['object_type'] == Metric.ENDPOINT_NETWORK_METRIC.value:
            obj = EndpointNetworkMetric.to_object(_dict['object_value'])

        else:
            raise TypeError('Invalid value. Not defined in cluster.repository.model.common.type')

        return EventObject(event_type=_dict['event_type'],
                           object_type=_dict['object_type'],
                           object_value=obj)
