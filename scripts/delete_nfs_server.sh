if [ $# -lt 2 ];then
  echo "Usage $0 [cluster name] [namespace]"
  exit 1
fi

cluster_name=$1
namespace=$2

# delete deployment
echo "kubectl delete -n $namespace deployment nfs-server-$cluster_name"
kubectl delete -n $namespace deployment nfs-server-$cluster_name

# delete service
echo "kubectl delete -n $namespace service nfs-server-$cluster_name"
kubectl delete -n $namespace service nfs-server-$cluster_name


