if [ $# -lt 2 ];then
  echo "Usage $0 [cluster name] [namespace]"
  exit 1
fi

cluster_name=$1
namespace=$2

# delete daemonset
echo "kubectl delete -n $namespace daemonset nfs-client-$cluster_name"
kubectl delete -n $namespace daemonset nfs-client-$cluster_name
