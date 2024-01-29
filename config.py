TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': '121.40.25.50',
                'port': '27017',
                'database': '',
            }
        }
    },
    'apps': {
        'models': {
            'models': ['entity.Clas', 'entity.Course', 'entity.Student', 'entity.Teacher', 'aerich.models'],
            'default_connection': 'default'
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}

