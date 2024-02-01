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

LOGIN_JSON = "service/DataIn/prop.json"
LOGIN_AT_STARTUP = False
