crds=(
brokers.submariner.io
clusterglobalegressips.submariner.io
clusters.submariner.io
endpoints.submariner.io
gateways.submariner.io
globalegressips.submariner.io
globalingressips.submariner.io
servicediscoveries.submariner.io
serviceexports.multicluster.x-k8s.io
serviceimports.multicluster.x-k8s.io
submariners.submariner.io
)

deployments=(
submariner-operator
submariner-lighthouse-agent
submariner-lighthouse-coredns
)

daemonsets=(
submariner-gateway
submariner-globalnet
submariner-routeagent
)

services=(
submariner-operator-metrics
submariner-gateway-metrics
submariner-globalnet-metrics
submariner-lighthouse-agent-metrics
submariner-lighthouse-coredns
submariner-lighthouse-coredns-metrics
)

namespaces=(
submariner-k8s-broker
submariner-operator    
)

echo "deleting submariner custom resource definitions"
for item in ${crds[@]};
do
  kubectl delete crd $item
done


echo "deleting submariner deployments"
for item in ${deployments[@]};
do
  kubectl delete deployment $item -n submariner-operator
done


echo "deleting submariner daemonsets"
for item in ${daemonsets[@]};
do
  kubectl delete daemonset $item -n submariner-operator
done


echo "deleting submariner services"
for item in ${services[@]};
do
  kubectl delete service $item -n submariner-operator
done


echo "deleting submariner namespaces"
for item in ${namespaces[@]};
do
  kubectl delete namespace $item
done
