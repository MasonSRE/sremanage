export ETCDCTL_ENDPOINTS="https://47.83.5.168:2381"

config='{
    "hertzClient": {
        "EnableTLS": true,
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
            "Port": 20101,
            "EnableTLS": true,
            "TLS": [
                {
                    "CaCrt": "configs/ca.crt",
                    "Crt": "configs/auth.crt",
                    "Key": "configs/auth.key"
                }
            ],
            "ClientAuth": 4,
            "PublicAddressDiscovery": true
        },
        {
            "Host": "127.0.0.1",
            "Port": 20103,
            "EnableTLS": false,
            "DisableServiceDiscovery": true,
            "DisablePrometheus": true
        }
    ],
    "base": {
        "LbPort": 10000,
        "AgentPort": 20101,
        "CheckUpdateInterval": 30,
        "HeartInterval": 10,
        "StatInterval": 30
    }
}'

etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/default/manager_agent "$config"
