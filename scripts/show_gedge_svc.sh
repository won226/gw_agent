echo ""
echo ">> local-cluster services"
kubectl get svc -n gedge -o wide

echo ""
echo ">> multi-cluster services"
kubectl get serviceimport -n submariner-operator
