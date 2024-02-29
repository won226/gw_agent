echo ""
echo ">> service imports"
kubectl get serviceimport -n submariner-operator

echo ""
echo ">> service exports"
kubectl get serviceexport -n gedge
