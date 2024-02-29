#!/bin/bash

SERVICE_FILE=/etc/systemd/system/gw_agent.service
INSTALL_DIR=/var/local/gw_agent

function error() {
    local message=$1
    echo -e "[ERROR] $message"
    exit 1
}

function info() {
    local message=$1
    echo -e "[INFO] $message"    
}

function service_exists() {
    local n=$1
    if [[ $(systemctl list-units --all -t service --full --no-legend "$n.service" | sed 's/^\s*//g' | cut -f1 -d' ') == $n.service ]]; then
        return 0
    else
        return 1
    fi
}

# uninstall gw_agent service
if service_exists gw_agent; then
    systemctl stop gw_agent
    systemctl disable gw_agent
    systemctl daemon-reload
fi

if [[ -f $SERVICE_FILE ]]; then
    rm -rf $SERVICE_FILE
fi

if [[ -d $INSTALL_DIR ]]; then
    rm -rf $INSTALL_DIR
fi