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
            "Port": 20401,
            "ClientAuth": 4,
            "EnableTLS": true,
            "TLS": [
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
            "Port": 20402,
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
    "redis": {
        "Addr": "172.16.0.178:21000"
    },
    "db": {
        "Write": {
            "DataBase": "user_backend",
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
        "EnableAuthPort": 20401,
        "SmtpServer": "{{邮箱 stmp 服务的访问域名}}",
        "Email": "{{发送人邮箱}}",
        "EmailAuthPassword": "{{发送人密码}}",
        "ExtSign": "csm.io",
        "SmtpPort": 587,
        "EmailHelo": "{{有些邮件运营商会检查该项。非强制的情况下可以不设置，强制的情况下需要设置一个发送服务的访问域名、要求域名需要能反向解析到 user_backend服务的公网 ip 上}}",
        "UserExtUrl": "uat.orderapi.appfast.cc"
    }
}'
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/local/user_backend $config
etcdctl --insecure-skip-tls-verify  --cert auth.crt --key auth.key  put /config/default/user_backend $config
