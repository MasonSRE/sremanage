#!/bin/bash
export ETCDCTL_API=3 

export ETCDCTL_ENDPOINTS="https://47.83.5.168:2385"

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
    }
}'

etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key put /config/test $globalConfig
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key put /config/default $globalConfig

config='{
    "hertzClient": {
        "EnableTLS": true,
        "TLS": [
            {
                "CaCrt": "configs/unsafe_ca.crt",
                "Crt": "configs/unsafe_auth.crt",
                "Key": "configs/unsafe_auth.key"
            },
            {
                "CaCrt": "configs/ca.crt",
                "Crt": "configs/auth.crt",
                "Key": "configs/auth.key"
            }
        ]
    },
    "hertz": [
        {
            "Host": "0.0.0.0",
            "Port": 20001,
            "ClientAuth": 4,
            "EnableTLS": true,
            "TLS": [
                {
                    "CaCrt": "configs/unsafe_ca.crt",
                    "Crt": "configs/unsafe_auth.crt",
                    "Key": "configs/unsafe_auth.key"
                },
                {
                    "CaCrt": "configs/ca.crt",
                    "Crt": "configs/auth.crt",
                    "Key": "configs/auth.key"
                }
            ],
            "DisableServiceDiscovery": true,
            "DisablePrometheus": true
        },
        {
            "Host": "0.0.0.0",
            "Port": 20002,
            "EnableTLS": true,
            "TLS": [
                {
                    "CaCrt": "configs/unsafe_ca.crt",
                    "Crt": "configs/unsafe_auth.crt",
                    "Key": "configs/unsafe_auth.key"
                },
                {
                    "CaCrt": "configs/ca.crt",
                    "Crt": "configs/auth.crt",
                    "Key": "configs/auth.key"
                }
            ],
            "PublicAddressDiscovery": true,
            "ClientAuth": 4
        }
    ],
    "redis": {
        "Addr": "172.16.0.178:21000"
    },
    "ip": {
        "Db": "ip2region.xdb"
    },
    "db": {
        "Write": {
            "DataBase": "manager_admin",
            "Host": "172.16.0.178",
            "Port": 3306,
            "User": "root",
            "Pass": "y8uzS7C6riF3T2ADn9",
            "Charset": "utf8mb4",
            "SetMaxIdleConns": 10,
            "SetMaxOpenConns": 128,
            "SetConnMaxLifetime": 60
        }
    },
    "base": {
        "AllowCrossDomain": true,
        "SuperAdminRoleId": 1,
        "MaxHeartInterval": 120,
        "EnableAuthPort": 20001,
        "LogUrl": "uat.log.appfast.cc",
        "ExtUrl": "uat.orderapi.appfast.cc",
        "UserExtUrl": "uat.orderapi.appfast.cc",
        "ExtSign": "csm.io",
        "OrderSign": "csm.io",
        "PayDoneCallback": "https://uat.admin.appfast.cc/orders/pay/done/callback",
        "OrderExpireInterval": 168,
        "OnlinePayDoneBackUrl": "https://uat.console.appfast.cc/#/payStatus",
        "Key": "4725dd9c46beed8f7adfe9e9bc8f0fbf",
        "Iv": "56879bb3d8080253",
        "Aad": "a2e4ecd4ab71ecb2",
        "DomainUpdateLockTTl": "1800",
        "DomainUpdateMaxWaitBind": "60",
        "TtydSessionTTL": "3000",
        "SchedulerIv": "56879bb3d8080253",
        "SchedulerAad": "a2e4ecd4ab71ecb2",
        "AlertCheckLockTTL": "1800",
        "AppKeyCheckLockTTL": "1800",
        "AlertLbHeartTimeout": "60",
        "EmailHelo": "{{有些邮件运营商会检查该项。非强制的情况下可以不设置，强制的情况下需要设置一个发送服务的访问域名、要求域名需要能反向解析到 admin服务的公网 ip 上}}",
        "DomainUpdateMaxNum": 1,
        "RefreshAclInterval": 1,
        "UploadOssEndpoint": "{{Oss访问端点}}",
        "UploadAccessKey": "{{Oss访问 key}}",
        "UploadAccessSecret": "{{Oss访问Secret}}",
        "UploadBucket": "{{Oss上传使用的存储桶名字}}",
        "RuleStorageCreateTagValue": "admin"
    },
    "token": {
        "JwtTokenSignKey": "379d85cb87950a2eecddb2f71c4d6b2e",
        "JwtTokenOnlineUsers": 10,
        "JwtTokenCreatedExpireAt": 28800,
        "JwtTokenRefreshExpireAt": 36000,
        "IsCacheToRedis": 0
    }
}'
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key put /config/test/manager_admin $config
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key put /config/default/manager_admin $config
