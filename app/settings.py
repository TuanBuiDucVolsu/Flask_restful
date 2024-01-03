import os
SECRET_KEY_DEVICE = os.getenv('SECRET_KEY_DEVICE')
DB = {
    'default': {
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT')
    },
}

GENDER = {
    'male': 'Trai',
    'female': 'Girl'
}

# MESSAGE
CODE_API = {
    'success': 1,
    'error': 0,
    'invalid_datetime': -2,
    'invalid_token': -3,
    'validate_error': -4,
    'account_inactive': -5,
    'token_expired': -6,
    'server_error': -99,
}

# HTTP_STATUS
HTTP_STATUS_MESSAGE = {
    500: {
        'api_code': CODE_API.get('server_error'),
        'message': 'Lỗi hệ thống'
    },
    400: {
        'api_code': CODE_API.get('validate_error'),
        'message': 'Missing required parameter in the post body.'
    },
    403: {
        'api_code': CODE_API.get('invalid_token'),
        'message': 'Token không hợp lệ'
    },
    404: {
        'api_code': CODE_API.get('error'),
        'message': 'Không tìm thấy đường dẫn (404)'
    }
}
