echo "[INFO] BEFORE REMOVE"
kubectl get livmigration
echo ""
echo ""

kubectl get livmigration -o yaml > temp
kubectl delete -f temp
rm -rf /mnt/migrate/gedge-cls1/pod-test1/
rm -rf /mnt/migrate/gedge-cls1/template/pod-test1_template.yaml

echo "[INFO] AFTER REMOVE"
kubectl get livmigration
echo ""
echo ""

