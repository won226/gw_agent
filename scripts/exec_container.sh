#!/bin/bash

if [ $# -lt 1 ]; then
  echo "USAGE: $0 { pod name } { container name }"
  exit 1
fi
  
pod=$1
container=$2

if [[ ! -z "$container" ]]; then
  kubectl exec -n gedge -it $pod -c $container -- /bin/bash
else
  kubectl exec -n gedge -it $pod -- /bin/bash
fi
