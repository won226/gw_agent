kubectl delete namespace monitoring
kubectl delete -f prometheus.yaml
kubectl delete -f k8s-state-metric.yaml
kubectl delete -f node-exporter.yaml
