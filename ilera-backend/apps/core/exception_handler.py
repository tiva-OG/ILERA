from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response and isinstance(response.data, dict):
        response.data = {
            "errors": response.data,
            "status": response.status_code,
        }

    return response
