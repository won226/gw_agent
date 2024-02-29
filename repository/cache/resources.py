from typing import List

from gw_agent.settings import get_logger
from cluster.command.localhost import LocalHostCommand
from repository.common.k8s_client import Connector
from repository.common.type import Kubernetes, ActiveStatus, PodStatus
from repository.model.k8s.condition import Condition
from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.namespace import Namespace
from repository.model.k8s.node import Node
from repository.model.k8s.pod import Pod
from repository.model.k8s.resource import ResourceBulk
from repository.model.k8s.service import Service
from repository.model.k8s.service_port import ServicePort
from utils.dateformat import DateFormatter

class ResourceRepository(object):
    """
    Kubernetes resource management class
    """
    _logger = None
    _connector = None
    _cluster_id = None
    _nodes = []
    _daemonsets = []
    _deployments = []
    _namespaces = []
    _pods = []
    _services = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._logger = get_logger(__name__)
            cls._instance._connector = Connector()

        return cls._instance

    def clear(self):
        """
        clear entire cache
        :return:
        """
        self._nodes.clear()
        self._daemonsets.clear()
        self._deployments.clear()
        self._namespaces.clear()
        self._pods.clear()
        self._services.clear()

    def set_cluster_id(self, cluster_id):
        """
        set cluster id
        :param cluster_id: (str)
        :return:
        """
        self._cluster_id = cluster_id

    def get_cluster_id(self) -> str:
        """
        get cluster name
        :return: (str) cluster name
        """
        return self._cluster_id

    def create_or_update(self, resource):
        """
        create or update resource
        :param resource: (object) Node or Namespace or Pod or Service or Deployment or Daemonset
        :return:
        """
        if type(resource) == Node:
            iterate_item = self._nodes
        elif type(resource) == Namespace:
            iterate_item = self._namespaces
        elif type(resource) == Pod:
            iterate_item = self._pods
        elif type(resource) == Deployment:
            iterate_item = self._deployments
        elif type(resource) == DaemonSet:
            iterate_item = self._daemonsets
        elif type(resource) == Service:
            iterate_item = self._services
        else:
            raise ValueError('Invalid resource')

        index = -1
        if hasattr(resource, 'namespace'):
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == resource.name and \
                        iterate_item[i].namespace == resource.namespace:
                    index = i
        else:
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == resource.name:
                    index = i
        # print(resource.to_dict())

        # create or update resource
        if index >= 0:
            iterate_item[index] = resource
        else:
            iterate_item.append(resource)

    def delete(self, resource):
        """
        delete resource
        :param resource: (object) Node or Namespace or Pod or Service or Deployment or Daemonset
        :return:
        """
        iterate_item = None

        if not hasattr(resource, 'to_dict') or 'kind' not in resource.to_dict():
            raise KeyError('Invalid resource')

        resource_dict = resource.to_dict()

        if resource_dict['kind'] == Kubernetes.NODE.value:
            iterate_item = self._nodes

        elif resource_dict['kind'] == Kubernetes.NAMESPACE.value:
            iterate_item = self._namespaces

        elif resource_dict['kind'] == Kubernetes.POD.value:
            iterate_item = self._pods

        elif resource_dict['kind'] == Kubernetes.DEPLOYMENT.value:
            iterate_item = self._deployments

        elif resource_dict['kind'] == Kubernetes.DAEMONSET.value:
            iterate_item = self._daemonsets

        elif resource_dict['kind'] == Kubernetes.SERVICE.value:
            iterate_item = self._services

        else:
            self._logger.info('Not support Kubernetes resource kind=({})'.format(resource['kind']))

        index = -1
        name = resource_dict['metadata']['name']

        if hasattr(resource, 'namespace'):
            namespace = resource.get_namespace()
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == name and iterate_item[i].namespace == namespace:
                    index = i
        else:
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == name:
                    index = i

        # delete
        if index > 0:
            del iterate_item[index]

    def get_bulk_resource(self) -> ResourceBulk:
        """
        get all k8s resource collected
        :return: (ResourceBulk)
        """
        if not self._cluster_id:
            return False, 'Not found cluster name', None

        resource_bulk = ResourceBulk(self._cluster_id)
        resource_bulk.set_nodes(self.get_nodes())

        resource_bulk.set_namespaces(self.get_namespaces())
        resource_bulk.set_daemonsets(self.get_daemonsets())
        resource_bulk.set_deployments(self.get_deployments())
        resource_bulk.set_pods(self.get_pods())
        resource_bulk.set_services(self.get_services())

        return resource_bulk

    # name, kind, namespace
    def get_nodes(self) -> List[Node]:
        """
        get nodes from repository
        :return:
        """
        return self._nodes

    def get_namespaces(self) -> List[Namespace]:
        """
        get namespaces from repository
        :return:
        """
        return self._namespaces

    def get_k8s_version(self):
        """
        get k8s version
        :return:
        """
        for node in self._nodes:
            k8s_version = node.get_k8s_version()
            if k8s_version is not None:
                return k8s_version

        return None

    def get_pods(self) -> List[Pod]:
        """
        get pods from repository
        :return:
        """
        return self._pods

    def get_services(self) -> List[Service]:
        """
        get services from repository
        :return:
        """
        return self._services

    def get_daemonsets(self) -> List[DaemonSet]:
        """
        get daemonsets from repository
        :return:
        """
        return self._daemonsets

    def get_deployments(self) -> List[Deployment]:
        """
        get deployments from repository
        :return:
        """
        return self._deployments

    def to_model(self, event_object):
        """
        convert k8s event object to model
        :param event_object: (dict)
        :return:
        """
        if not hasattr(event_object, 'kind'):
            raise ValueError('Invalid kubernetes event object. Not exist kind attributes')
        if not hasattr(event_object, 'metadata'):
            raise ValueError('Invalid kubernetes event object. Not exist status attributes')
        if not hasattr(event_object, 'spec'):
            raise ValueError('Invalid kubernetes event object. Not exist spec attributes')
        if not hasattr(event_object, 'status'):
            raise ValueError('Invalid kubernetes event object. Not exist status attributes')

        if event_object.kind == Kubernetes.NODE.value:
            return self.to_node_model(event_object), event_object.kind
        if event_object.kind == Kubernetes.POD.value:
            return self.to_pod_model(event_object), event_object.kind
        if event_object.kind == Kubernetes.NAMESPACE.value:
            return self.to_namespace_model(event_object), event_object.kind
        if event_object.kind == Kubernetes.DEPLOYMENT.value:
            return self.to_deployment_model(event_object), event_object.kind
        if event_object.kind == Kubernetes.DAEMONSET.value:
            return self.to_daemonset_model(event_object), event_object.kind
        if event_object.kind == Kubernetes.SERVICE.value:
            return self.to_service_model(event_object), event_object.kind

        raise TypeError('Invalid kubernetes object. Input should be '
                        'kubernetes.client.model.v1_namespace.V1Namespace | '
                        'kubernetes.client.model.v1_pod.V1Pod | '
                        'kubernetes.client.model.v1_node.V1Node | '
                        'kubernetes.client.model.v1_service.V1Service | '
                        'kubernetes.client.model.v1_deployment.V1Deployment | '
                        'kubernetes.client.model.v1_daemon_set.V1DaemonSet.')

    @classmethod
    def to_node_model(cls, item):
        """
        convert to node model
        :param item: (<class 'kubernetes.client.model.v1_node.V1Node'>)
        :return:
        """
        metadata = item.metadata
        spec = item.spec
        status = item.status
        node_info = status.node_info

        name = metadata.name
        stime = metadata.creation_timestamp
        role = 'Worker'
        number_of_cpu = status.allocatable['cpu']  # max cpu
        mem_size = status.allocatable['memory']  # max memory
        max_pods = status.allocatable['pods']  # max pods
        os = node_info.os_image
        kernel_version = node_info.kernel_version
        k8s_version = node_info.kubelet_version

        # set labels
        labels = []
        for key, value in metadata.labels.items():
            labels.append('{}={}'.format(key, value))

        for label in labels:
            if 'node-role.kubernetes.io/master' in label:
                role = 'Master'

        # set taints
        taints = []
        if spec.taints is not None:
            for taint in spec.taints:
                # type(taint): kubernetes.client.model.v1_taint.V1Taint
                taint_dict = taint.to_dict()
                if taint_dict['value'] is None:
                    taints.append('{}:{}'.format(taint_dict['key'],
                                                 taint_dict['effect']))
                else:
                    taints.append('{}={}:{}'.format(taint_dict['key'],
                                                    taint_dict['value'],
                                                    taint_dict['effect']))

        # set node ip
        ip = None
        for elm in status.addresses:
            # type(elm): kubernetes.client.model.v1_node_address.V1NodeAddress
            elm_dict = elm.to_dict()
            if elm_dict['type'] == 'InternalIP':
                ip = elm_dict['address']

        # set conditions
        conditions = []
        if status.conditions is not None:
            for elm in status.conditions:
                # type(elm): kubernetes.client.model.v1_node_condition.V1NodeCondition
                elm_dict = elm.to_dict()
                condition = elm_dict['type']
                status = elm_dict['status']
                message = elm_dict['reason']
                updated = elm_dict['last_transition_time']
                obj = Condition()
                obj.set_condition(condition)
                obj.set_status(status)
                obj.set_message(message)
                obj.set_updated(DateFormatter.datetime_to_str(updated))
                conditions.append(obj)

        node = Node(name=name)
        node.set_state(ActiveStatus.ACTIVE.value)
        node.set_role(role)
        node.set_labels(labels)
        node.set_taints(taints)
        node.set_k8s_version(k8s_version)
        node.set_os(os)
        node.set_kernel_version(kernel_version)
        node.set_ip(ip)
        node.set_iface(LocalHostCommand.get_iface(ip))
        node.set_number_of_cpu(number_of_cpu)
        node.set_ram_size(mem_size)
        node.set_max_pods(max_pods)
        node.set_conditions(conditions)
        node.set_stime(DateFormatter.datetime_to_str(stime))

        return node

    @classmethod
    def to_namespace_model(cls, item):
        """
        convert to namespace model
        :param item: (<class 'kubernetes.client.model.v1_namespace.V1Namespace'>)
        :return: (Namespace)
        """
        metadata = item.metadata
        status = item.status
        name = metadata.name
        stime = metadata.creation_timestamp
        state = status.phase

        # set conditions
        conditions = []
        if status.conditions is not None:
            for elm in status.conditions:
                # type(elm): kubernetes.client.model.v1_node_condition.V1NodeCondition
                elm_dict = elm.to_dict()
                condition = elm_dict['type']
                status = elm_dict['status']
                message = elm_dict['reason']
                updated = elm_dict['last_transition_time']
                obj = Condition()
                obj.set_condition(condition)
                obj.set_status(status)
                obj.set_message(message)
                obj.set_updated(DateFormatter.datetime_to_str(updated))
                conditions.append(obj)

        namespace = Namespace(name=name)
        namespace.set_state(state)
        namespace.set_conditions(conditions)
        namespace.set_stime(DateFormatter.datetime_to_str(stime))

        return namespace

    @classmethod
    def to_pod_model(cls, item):
        """
        convert to namespace model
        :param item: (<class 'kubernetes.client.model.v1_pod.V1Pod'>)
        :return: (Pod)
        """
        metadata = item.metadata
        spec = item.spec
        status = item.status

        name = metadata.name
        namespace = metadata.namespace
        node = spec.node_name
        host_ip = status.host_ip  # host ip
        pod_ip = status.pod_ip  # allocated ip from cni network
        state = status.phase
        stime = status.start_time

        # set labels
        labels = []
        if metadata.labels:
            for key, value in metadata.labels.items():
                if key == 'pod-template-hash':
                    continue
                labels.append('{}={}'.format(key, value))

        # set conditions
        conditions = []
        if status.conditions is not None:
            for elm in status.conditions:
                # type(elm): kubernetes.client.model.v1_node_condition.V1NodeCondition
                elm_dict = elm.to_dict()
                condition = elm_dict['type']
                status = elm_dict['status']
                message = elm_dict['reason']
                updated = elm_dict['last_transition_time']

                obj = Condition()
                obj.set_condition(condition)
                obj.set_status(status)
                obj.set_message(message)
                obj.set_updated(DateFormatter.datetime_to_str(updated))
                conditions.append(obj)

        # set images
        images = []
        for container in spec.containers:
            images.append(container.image)  # 'rancher/fleet-agent:v0.3.9'

        pod = Pod(name=name)
        pod.set_namespace(namespace)
        pod.set_state(state)
        pod.set_labels(labels)
        pod.set_host_ip(host_ip)
        pod.set_pod_ip(pod_ip)
        pod.set_node_name(node)
        pod.set_conditions(conditions)
        pod.set_images(images)
        pod.set_stime(DateFormatter.datetime_to_str(stime))

        return pod

    def to_deployment_model(self, item):
        """
        convert to namespace model
        :param item: (<class 'kubernetes.client.model.v1_deployment.V1Deployment'>)
        :return: (Deployment)
        """
        metadata = item.metadata
        spec = item.spec
        status = item.status

        name = metadata.name
        namespace = metadata.namespace
        stime = metadata.creation_timestamp

        # set images
        images = []
        for container in spec.template.spec.containers:
            images.append(container.image)

        # set ready
        ready_replicas = status.ready_replicas
        replicas = status.replicas

        # set selector
        # limitation: only support 'match_labels'
        selector = []
        for key, value in spec.selector.match_labels.items():
            selector.append('{}={}'.format(key, value))
        restart = self.get_restarts_for_labeled_pods(selector[0])

        # set conditions
        conditions = []
        if status.conditions is not None:
            for elm in status.conditions:
                # type(elm): kubernetes.client.model.v1_node_condition.V1NodeCondition
                elm_dict = elm.to_dict()
                condition = elm_dict['type']
                status = elm_dict['status']
                message = elm_dict['reason']
                updated = elm_dict['last_transition_time']
                obj = Condition()
                obj.set_condition(condition)
                obj.set_status(status)
                obj.set_message(message)
                obj.set_updated(DateFormatter.datetime_to_str(updated))
                conditions.append(obj)

        deployment = Deployment(name=name)
        deployment.set_namespace(namespace)
        deployment.set_state(ActiveStatus.ACTIVE.value)
        deployment.set_images(images)
        deployment.set_ready_replicas(ready_replicas)
        deployment.set_replicas(replicas)
        deployment.set_restart(restart)
        deployment.set_selector(selector)
        deployment.set_conditions(conditions)
        deployment.set_stime(DateFormatter.datetime_to_str(stime))

        return deployment

    @classmethod
    def to_daemonset_model(cls, item):
        """
        convert to namespace model
        :param item: (<class 'kubernetes.client.model.v1_daemon_set.V1DaemonSet'>)
        :return: (DaemonSet)
        """
        metadata = item.metadata
        spec = item.spec
        status = item.status

        name = metadata.name
        namespace = metadata.namespace
        stime = metadata.creation_timestamp

        # set images
        images = []
        for container in spec.template.spec.containers:
            images.append(container.image)

        desired = status.desired_number_scheduled
        current = status.current_number_scheduled

        # set selector
        # limitation: only support 'match_labels'
        selector = []
        for key, value in spec.selector.match_labels.items():
            selector.append('{}={}'.format(key, value))

        # set ready
        ready = status.number_ready

        # set conditions
        conditions = []
        if status.conditions is not None:
            for elm in status.conditions:
                # type(elm): kubernetes.client.model.v1_node_condition.V1NodeCondition
                elm_dict = elm.to_dict()
                condition = elm_dict['type']
                status = elm_dict['status']
                message = elm_dict['reason']
                updated = elm_dict['last_transition_time']
                obj = Condition()
                obj.set_condition(condition)
                obj.set_status(status)
                obj.set_message(message)
                obj.set_updated(DateFormatter.datetime_to_str(updated))
                conditions.append(obj)

        daemonset = DaemonSet(name=name)
        daemonset.set_namespace(namespace)
        daemonset.set_state(ActiveStatus.ACTIVE.value)
        daemonset.set_images(images)
        daemonset.set_images(images)
        daemonset.set_desired(desired)
        daemonset.set_current(current)
        daemonset.set_ready(ready)
        daemonset.set_selector(selector)
        daemonset.set_conditions(conditions)
        daemonset.set_stime(DateFormatter.datetime_to_str(stime))

        return daemonset

    @classmethod
    def to_service_model(cls, item):
        """
        convert to namespace model
        :param item: (<class 'kubernetes.client.model.v1_service.V1Service'>)
        :return: (Service)
        """
        metadata = item.metadata
        spec = item.spec
        status = item.status
        name = metadata.name
        namespace = metadata.namespace
        stime = metadata.creation_timestamp

        service_type = spec.type
        cluster_ip = spec.cluster_ip
        external_ips = []
        if spec.external_i_ps is not None:
            for external_ip in spec.external_i_ps:
                external_ips.append(external_ip)

        ports = []
        for port in spec.ports:
            # type(port): kubernetes.client.model.v1_service_port.V1ServicePort
            port_dict = port.to_dict()
            obj = ServicePort(name=port_dict['name'])
            obj.set_port(port_dict['port'])
            obj.set_protocol(port_dict['protocol'])
            obj.set_node_port(port_dict['node_port'])
            obj.set_target_port(port_dict['target_port'])
            ports.append(obj)

        # set selector
        # limitation: only support 'match_labels'
        selector = []
        if spec.selector is not None:
            for key, value in spec.selector.items():
                selector.append('{}={}'.format(key, value))

        # set conditions
        conditions = []
        if status.conditions is not None:
            for elm in status.conditions:
                # type(elm): kubernetes.client.model.v1_node_condition.V1NodeCondition
                elm_dict = elm.to_dict()
                condition = elm_dict['type']
                status = elm_dict['status']
                message = elm_dict['reason']
                updated = elm_dict['last_transition_time']
                obj = Condition()
                obj.set_condition(condition)
                obj.set_status(status)
                obj.set_message(message)
                obj.set_updated(DateFormatter.datetime_to_str(updated))
                conditions.append(obj)

        service = Service(name=name)
        service.set_namespace(namespace)
        service.set_state(ActiveStatus.ACTIVE.value)
        service.set_service_type(service_type)
        service.set_cluster_ip(cluster_ip)
        service.set_external_ips(external_ips)
        service.set_selector(selector)
        service.set_conditions(conditions)
        service.set_ports(ports)
        service.set_stime(DateFormatter.datetime_to_str(stime))

        return service

    def get_restarts_for_labeled_pods(self, label_selector):
        """
        get pod restarts count for a label
        :param label_selector:
        :return:
        """
        result = self._connector.core_v1_api().list_pod_for_all_namespaces(label_selector=label_selector)
        if result.items is None or len(result.items) == 0:
            return 0

        if result.items[0].status is None:
            return 0

        if result.items[0].status.container_statuses is None or \
                len(result.items[0].status.container_statuses) == 0:
            return 0

        if result.items[0].status.container_statuses[0].restart_count is None:
            return 0

        try:
            restarts = result.items[0].status.container_statuses[0].restart_count

        except IndexError:
            return 0

        return restarts

    def is_deployment_deployed(self, namespace, name):
        """
        check whether deployment is deployed or not
        :param namespace: (str) namespace
        :param name: (str) deployment name
        :return: True - deployed, False - not deployed
        """
        found = False

        for deployment in self._deployments:
            if deployment.get_name() == name and deployment.get_namespace() == namespace:
                found = True

        return found

    def is_all_deployment_replicas_ready(self, namespace, name):
        """
        check whether all deployment replicas are ready
        :param namespace: (str) namespace
        :param name: (str) deployment name
        :return:
        """
        deployment = None

        for item in self._deployments:
            if item.get_namespace() == namespace and item.get_name() == name:
                deployment = item
                break

        if deployment is None:
            return False

        if deployment.get_ready_replicas() == deployment.get_replicas():
            return True

        return False

    def is_daemonset_deployed(self, namespace, name):
        """
        check whether daemonset is deployed or not
        :param namespace: (str) namespace
        :param name: (str) daemonset name
        :return: True - deployed, False - not deployed
        """
        found = False

        for daemonset in self._daemonsets:
            if daemonset.get_name() == name and daemonset.get_namespace() == namespace:
                found = True

        return found

    def is_all_daemonset_replicas_ready(self, namespace, name):
        """
        check whether all daemonset replicas are ready
        :param namespace: (str) namespace
        :param name: (str) daemonset name
        :return:
        """
        daemonset = None

        for item in self._daemonsets:
            if item.get_namespace() == namespace and item.get_name() == name:
                daemonset = item
                break

        if daemonset is None:
            return False

        if daemonset.get_desired() == daemonset.get_ready():
            return True

    def is_service_deployed(self, namespace, name):
        """
        check whether service is deployed or not
        :param namespace: (str) namespace
        :param name: (str) service name
        :return: True - deployed, False - not deployed
        """
        found = False

        for service in self._services:
            if service.get_name() == name and service.get_namespace() == namespace:
                found = True

        return found

    def get_service(self, namespace, name):
        """
        get service
        :param namespace: (str) service namespace
        :param name: (str) service name
        :return: (bool) success, (Service) service
        """
        if not namespace and type(namespace) != str:
            return False, None
        if not name and type(name) != str:
            return False, None

        for service in self._services:
            if service.get_name() == name and service.get_namespace() == namespace:
                return True, service

        return False, None

    def get_namespace_services(self, namespace: str) -> List[Service]:
        """
        get namespace services from repository
        :return: list[Service]
        """
        services = []

        if type(namespace) != str or len(namespace) <= 0:
            raise ValueError('Invalid parameter(namespace) value')

        for service in self._services:
            if service.get_namespace() == namespace:
                services.append(service)

        return services

    def get_namespace_services_by_pod(self,
                                      namespace: str,
                                      pod: str) -> List[Service]:
        """
        get namespace services by service name
        :param namespace: (str) namespace name
        :param pod: (str) pod name
        :return: List[Service]
        """
        filtrated_services = []
        filtrated_pods = []
        namespace_services = self.get_namespace_services(namespace)

        if len(namespace_services) == 0:
            return []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select service for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for service in namespace_services:
                if item.get_namespace() == service.get_namespace():
                    selectors = service.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_services.append(service)
                            break

        return filtrated_services

    def is_pod_deployed(self, namespace, name):
        """
        check whether pod is deployed not not
        :param namespace: (str) namespace
        :param name: (str) pod name
        :return:
        """
        found = False

        for pod in self._pods:
            if pod.get_name() == name and pod.get_namespace() == namespace:
                found = True

        return found

    def is_pod_running_for_prefix(self, namespace, prefix):
        """
        check whether pod is running or not
        :param namespace: (str) namespace
        :param prefix: (str) pod name prefix, i.e., name = prefix-lkajsdla
        :return: (bool)
        """
        name_pattern = '{}-'.format(prefix)
        for pod in self._pods:
            if name_pattern in pod.get_name() and pod.get_namespace() == namespace:
                if pod.get_state() == PodStatus.RUNNING.value:
                    return True

        return False

    def is_pod_running(self, namespace, name):
        """
        check whether pod is running or not
        :param namespace: (str) namespace
        :param name: (str) pod name
        :return: (bool)
        """
        for pod in self._pods:
            if name == pod.get_name() and pod.get_namespace() == namespace:
                if pod.get_state() == PodStatus.RUNNING.value:
                    return True

        return False

    def is_namespace_deployed(self, namespace):
        """
        check whether namespace is deployed or not
        :param namespace: (str)
        :return: (bool)
        """
        for item in self._namespaces:
            if item.get_name() == namespace:
                return True

        return False

    def get_namespace_service_account(self, namespace):
        """
        get all service account for namespace
        :param namespace: (str)
        :return:
        """

    def get_pods_for_deployment(self, namespace, deployment):
        """
        get pod list for deployment
        :param namespace: (str)
        :param deployment: (str)
        :return: (list(str))
        """
        pods = []
        for item in self._pods:
            if namespace == item.get_namespace() and deployment+'-' in item.get_name():
                pods.append(item.get_name())

        return pods

    def get_pods_for_daemonset(self, namespace, deployment):
        """
        get pod list for daemonset
        :param namespace:
        :param deployment:
        :return:
        """
        pods = []
        for item in self._pods:
            if namespace == item.get_namespace() and deployment + '-' in item.get_name():
                pods.append(item.get_name())

        return pods

    # def get_nodes_to_dict(self):
    #     """
    #     get nodes as dict from repository
    #     :return: (dict)
    #     """
    #     nodes = []
    #     for node in self._nodes:
    #         nodes.append(node.to_dict())
    #     return nodes
    #
    # def set_nodes(self):
    #     """
    #     test
    #     set nodes by calling kubernetes CoreV1Api
    #     :return:
    #     """
    #     result = self._connector.core_v1_api().list_node()
    #
    #     for item in result.items:
    #         obj = self.to_node_model(item)
    #         self.create_or_update(obj)
    #
    # def get_all_namespaces(self):
    #     """
    #     get namespaces gathered from k8s api
    #     :return:
    #     """
    #     namespaces = []
    #     for namespace in self._namespaces:
    #         namespaces.append(namespace.to_dict())
    #     return namespaces
    #
    # def set_all_namespaces(self):
    #     """
    #     test
    #     set namespaces by calling kubernetes CoreV1Api
    #     :return:
    #     """
    #     result = self._connector.core_v1_api().list_namespace()
    #
    #     for item in result.items:
    #         obj = self.to_namespace_model(item)
    #         self.create_or_update(obj)
    #
    # def get_pods_all_namespaces(self):
    #     """
    #     get pods gathered from k8s api
    #     :return:
    #     """
    #     pods = []
    #     for pod in self._pods:
    #         pods.append(pod.to_dict())
    #
    #     return pods
    #
    # def set_pods_all_namespaces(self):
    #     """
    #     API test
    #     set pods by calling kubernetes CoreV1Api
    #     :return:
    #     """
    #
    #     result = self._connector.core_v1_api().list_pod_for_all_namespaces()
    #     for item in result.items:
    #         obj = self.to_pod_model(item)
    #         self.create_or_update(obj)
    #
    # def get_services_all_namespaces(self):
    #     """
    #     get services gathered from k8s api
    #     :return:
    #     """
    #
    #     services = []
    #     for service in self._services:
    #         services.append(service.to_dict())
    #
    #     return services
    #
    # def set_services_all_namespaces(self):
    #     """
    #     API test
    #     set services by calling kubernetes CoreV1Api
    #     :return:
    #     """
    #
    #     result = self._connector.core_v1_api().list_service_for_all_namespaces()
    #     for item in result.items:
    #         obj = self.to_service_model(item)
    #         self.create_or_update(obj)
    #
    # def get_deployment_all_namespaces(self):
    #     """
    #     get deployments gathered from k8s api
    #     :return:
    #     """
    #
    #     deployments = []
    #     for deployment in self._deployments:
    #         deployments.append(deployment.to_dict())
    #
    #     return deployments
    #
    # def set_deployment_all_namespaces(self):
    #     """
    #     API test
    #     set deployments by calling kubernetes AppV1Api
    #     :return:
    #     """
    #     result = self._connector.app_v1_api().list_deployment_for_all_namespaces()
    #
    #     for item in result.items:
    #         obj = self.to_deployment_model(item)
    #         self.create_or_update(obj)
    #
    # def get_daemonset_all_namespace(self):
    #     """
    #     get daemonset gathered from k8s api
    #     :return:
    #     """
    #     daemonsets = []
    #     for daemonset in self._daemonsets:
    #         daemonsets.append(daemonset.to_dict())
    #
    #     return daemonsets
    #
    # def set_daemonset_all_namespace(self):
    #     """
    #     API test
    #     set deployments by calling kubernetes AppV1Api
    #     :return:
    #     """
    #     result = self._connector.app_v1_api().list_daemon_set_for_all_namespaces()
    #
    #     for item in result.items:
    #         obj = self.to_daemonset_model(item)
    #         self.create_or_update(obj)
