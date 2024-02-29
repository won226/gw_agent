from django.db import models


# Create your model here.


class Cluster(models.Model):
    """
    Cluster model
    """

    class Role(models.TextChoices):
        """
        Cluster role in multi-cluster
        """
        LOCAL = 'Local'
        REMOTE = 'Remote'
        NONE = 'None'
        UNKNOWN = 'Unknown'

    # auto increment
    id = models.BigAutoField(primary_key=True)

    # cluster name
    cluster_name = models.CharField(max_length=128,
                                    verbose_name='cluster name',
                                    unique=True,
                                    null=False)

    # multi-cluster connect id(uuid4 format)
    mc_connect_id = models.CharField(max_length=128,
                                     default=None,
                                     null=True,
                                     verbose_name='multicluster connection id')

    # cluster role in multi-cluster
    role = models.CharField(max_length=10,
                            choices=Role.choices,
                            default=Role.NONE,
                            verbose_name='cluster role in multi-cluster')

    # remote_cluster name
    remote_cluster_name = models.CharField(max_length=128,
                                           verbose_name='remote cluster name',
                                           null=True)

    # is multi-cluster network applications provisioned?
    is_mc_provisioned = models.BooleanField(default=False,
                                            verbose_name='is multi-cluster network application provisioned?')

    # create date
    create_date = models.TimeField(verbose_name='create date',
                                   null=False, auto_now=True)
    # update date
    update_date = models.TimeField(verbose_name='update date',
                                   null=False, auto_now=True)

    def __str__(self):
        return self.cluster_name


class MultiClusterConfig(models.Model):
    """
    Multi-cluster configuration request model
    request issued from CEdge-center
    """

    class MultiClusterConfigState(models.TextChoices):
        """
        Multi-cluster configuration state
        """
        CONNECT_REQUEST = 'ConnectRequest'
        CONNECTING = 'Connecting'
        DISCONNECT_REQUEST = 'DisconnectRequest'
        DISCONNECTING = 'Disconnecting'
        NONE = 'None'

    # auto increment
    id = models.BigAutoField(primary_key=True)

    # multi-cluster connect id(uuid4 format)
    mc_connect_id = models.CharField(max_length=128,
                                     default=None,
                                     null=True,
                                     verbose_name='multicluster connection id')

    # cluster role in multi-cluster
    role = models.CharField(max_length=10,
                            choices=Cluster.Role.choices,
                            default=Cluster.Role.NONE,
                            verbose_name='cluster role in multi-cluster')

    # multi-cluster config state
    mc_config_state = models.CharField(max_length=25,
                                       choices=MultiClusterConfigState.choices,
                                       default=MultiClusterConfigState.NONE,
                                       verbose_name='multi-cluster configuration state')

    # remote_cluster name
    remote_cluster_name = models.CharField(max_length=128,
                                           verbose_name='remote cluster name',
                                           null=True)

    # create date
    create_date = models.TimeField(verbose_name='create date',
                                   null=False, auto_now=True)
    # update date
    update_date = models.TimeField(verbose_name='update date',
                                   null=False, auto_now=True)

    def __str__(self):
        return self.mc_connect_id
