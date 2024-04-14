TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'port': '3306',
                'database': 'work',
            }
        }
    },
    'apps': {
        'models': {
            'models': ['entity.db_entity', 'aerich.models'],
            'default_connection': 'default'
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}

SERVER_IP = "172.16.22.248"
SERVER_PORT = 8080

LOGIN_JSON = "service/DataIn/prop.json"
LOGIN_AT_STARTUP = False

ENVIRONMENT = "default"
TIMEZONE = "Asia/Shanghai"

INTERNAL_REQUEST_TOKEN = "1145141919810"

# 邮件相关
SENDER_EMAIL = "1483823709@qq.com"
SENDER_PASSWORD = "hirzwvgpzsxfihec"

BASE_PASSWORD = "114514"