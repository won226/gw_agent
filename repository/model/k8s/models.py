from repository.model.k8s.node import Node
from repository.model.k8s.namespace import Namespace
from repository.model.k8s.pod import Pod
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.service import Service

classes = [
    Node,
    Namespace,
    Pod,
    Deployment,
    DaemonSet,
    Service
]

