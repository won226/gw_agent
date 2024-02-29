from repository.common.type import MultiClusterRole


class Migration:

    @staticmethod
    def deploy_msv_nfs(vol_path):
        """
        deploy network filesystem server for multi-cluster shared volume
        :param vol_path: (str) nfs's shared volume mounted at host
        :return:
        """
        pass

    @staticmethod
    def deploy_msv_local_nfc(vol_path):
        """
        deploy network filesystem client for multi-cluster shared volume
        :param vol_path: (str) nfc's shared volume mounted at host
        :return:
        """
        pass

    @staticmethod
    def check_msv(role):
        """
        check component deployed status for multi-cluster shared volume
        :param role: (str) 'Local' or 'Remote'
        :return:
        """
        if not MultiClusterRole.validate(role):
            raise ValueError('Invalid value for role({}). Must input "Local" or "Remote" as role'.format(role))

        if role == MultiClusterRole.LOCAL.value:
            pass
        if role == MultiClusterRole.REMOTE.value:
            pass

    @staticmethod
    def migrate_pod(namespace, name):
        """
        migrate pod to connected cluster
        :param namespace: (str) pod namespace
        :param name: (str) pod name
        :return:
        """
        # check whether multi-cluster shared volume is ready
        # take a snapshot for pod
        # search services
        # search deployment(not supported)
        # search daemonset(not supported)
        pass

