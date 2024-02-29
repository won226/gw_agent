kubectl create namespace monitoring
kubectl apply -f prometheus-cluster-role.yaml
kubectl apply -f prometheus-config-map.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f prometheus-node-exporter.yaml
kubectl apply -f prometheus-svc.yaml

kubectl apply -f kube-state-cluster-role.yaml
kubectl apply -f kube-state-deployment.yaml
kubectl apply -f kube-state-svcaccount.yaml
kubectl apply -f kube-state-svc.yaml

