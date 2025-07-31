export ETCDCTL_ENDPOINTS="https://47.83.5.168:2381"


config='{
    "hertzClient": {
        "EnableTLS": true,
        "ClientCrt": "configs/auth.crt",
        "ClientKey": "configs/auth.key",
        "TLS": [
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
            "Port": 8282,
            "EnableTLS": true,
            "TLS": [
                {
                    "CaCrt": "configs/ca.crt",
                    "Crt": "configs/auth.crt",
                    "Key": "configs/auth.key"
                }
            ],
            "ServerCrt": "configs/auth.crt",
            "ServerKey": "configs/auth.key",
            "CaCrt": "configs/ca.crt",
            "DisablePrometheus": true,
            "DisableServiceDiscovery": true,
            "Tags": {
                "type": "public"
            },
            "ClientAuth": 0
        },
        {
            "Host": "0.0.0.0",
            "Port": 8380,
            "EnableTLS": true,
            "TLS": [
                {
                    "CaCrt": "configs/ca.crt",
                    "Crt": "configs/auth.crt",
                    "Key": "configs/auth.key"
                }
            ],
            "ServerCrt": "configs/auth.crt",
            "ServerKey": "configs/auth.key",
            "CaCrt": "configs/ca.crt",
            "PublicAddressDiscovery": true,
            "ClientAuth": 0
        }
    ],
    "ip": {
        "Db": "configs/ip2region.xdb"
    },
    "base": {
        "CheckUpdateInterval": 5,
        "OkReCheckInterval": 5,
        "ErrorReCheckInterval": 10,
        "DialTimeout": 5,
        "CacheTTL": 60,
        "Key": "4725dd9c46beed8f7adfe9e9bc8f0fbf",
        "Iv": "56879bb3d8080253",
        "Aad": "a2e4ecd4ab71ecb2",
        "LbPort": 10000
    }
}'

etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/local/scheduler $config
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/default/scheduler $config
