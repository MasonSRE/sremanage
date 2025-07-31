export ETCDCTL_ENDPOINTS="https://47.83.5.168:2385"


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
            "Port": 20501,
            "EnableTLS": true,
            "TLS": [
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
    "tcp_server": {
        "Port": 20502,
        "ReadTimeout": 3600,
        "IdleTimeout": 3600
    },
    "tcp_client": {
        "Timeout": 60
    },
    "base": {
        "CheckInterval": "0 30 0/1 * * ? ",
        "DeleteExpireConnInterval": "0 15 2 * * ?",
        "TTL": 86400,
        "CheckLockTTl": 3600,
        "CheckMaxOnlineTime": 1,
        "DayTTl": 7776000,
        "CheckMaxGoroutine": 50
    },
    "ip": {
        "Db": "ip2region.xdb"
    },
    "db": {
        "Write": {
            "Host": "172.16.0.175",
            "Port": 3306,
            "User": "root",
            "Pass": "y8uzS7C6riF3T2ADn9",
            "DataBase": "push",
            "Charset": "utf8mb4",
            "SetMaxIdleConns": 10,
            "SetMaxOpenConns": 128,
            "SetConnMaxLifetime": 60
        }
    },
    "redis": {
        "Addr": "172.16.0.175:21000"
    }
}'
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/default/push $config
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/local/push $config
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  get /config/local/push
