from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

def get_first_error(data):
    if isinstance(data, dict):
        # Prefer 'detail' or 'non_field_errors' first if they exist
        for key in ['detail', 'non_field_errors']:
            if key in data:
                val = data[key]
                if isinstance(val, list) and val:
                    return get_first_error(val[0])
                elif isinstance(val, (str, dict)):
                    return get_first_error(val)
        
        # Otherwise, iterate through all keys
        for key, val in data.items():
            if isinstance(val, list) and val:
                return get_first_error(val[0])
            elif isinstance(val, (str, dict)):
                return get_first_error(val)
    elif isinstance(data, list):
        if data:
            return get_first_error(data[0])
    elif isinstance(data, str):
        return data
    return "An error occurred."

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first to get the standard response
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            if 'detail' not in response.data:
                response.data['detail'] = get_first_error(response.data)
            elif isinstance(response.data['detail'], list) and response.data['detail']:
                response.data['detail'] = get_first_error(response.data['detail'])
        elif isinstance(response.data, list):
            response.data = {
                'detail': get_first_error(response.data),
                'errors': response.data
            }

    return response
