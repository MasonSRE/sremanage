#!/bin/bash

export ETCDCTL_ENDPOINTS="https://47.83.5.168:2381"

globalConfig='{
    "log": {
        "RootLogDir": "./logs",
        "TextFormat": "json",
        "TimePrecision": "millisecond",
        "MaxSize": 10,
        "MaxBackups": 30,
        "MaxAge": 15,
        "Compress": false,
        "LogLevel": -1
    },
    "etcd": {
        "EtcdTLSUrls": [
            "47.83.5.168:2381"
        ],
        "ClientCrt": "configs/auth.crt",
        "ClientKey": "configs/auth.key"
    },
    "hertzClient": {
        "EnableTLS": true,
        "ClientCrt": "configs/auth.crt",
        "ClientKey": "configs/auth.key"
    }
}'

etcdctl --insecure-skip-tls-verify --cert auth.crt --key auth.key put /config/test "$globalConfig"
etcdctl --insecure-skip-tls-verify --cert auth.crt --key auth.key put /config/default "$globalConfig"
