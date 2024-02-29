#!/bin/bash

if [ $# -lt 1 ]; then
    echo "USAGE: $0 [ delete migration name ]"
    exit 1
fi

kubectl delete Livmigration $1
