#!/bin/bash
set -e
MYCLUSTER=$(hostname)-cls

trap \
 "{ \
kubectl taint nodes $(hostname) node-role.kubernetes.io/master:NoSchedule ; exit 255; }" \
SIGINT SIGTERM ERR EXIT

# release taint
kubectl taint nodes $(hostname) node-role.kubernetes.io/master-

# set master node label for submariner
kubectl label node $(hostname) submariner.io/gateway=true --overwrite

subctl join broker-info.subm \
--kubeconfig /root/.kube/config \
--clusterid $MYCLUSTER \
--cable-driver wireguard \
--natt=false

# recover taint for master node
kubectl taint nodes $(hostname) node-role.kubernetes.io/master:NoSchedule
