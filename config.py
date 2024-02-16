TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'user': 'root',
                'password': '114514',
                'host': 'localhost',
                'port': '3306',
                'database': 'internet_class_visible',
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

SERVER_IP = "localhost"
SERVER_PORT = 8080

LOGIN_JSON = "service/DataIn/prop.json"
LOGIN_AT_STARTUP = False

ENVIRONMENT = "default"
TIMEZONE = "Asia/Shanghai"

INTERNAL_REQUEST_TOKEN = "1145141919810"

# 邮件相关
SENDER_EMAIL = "1483823709@qq.com"
SENDER_PASSWORD = "hirzwvgpzsxfihec"
