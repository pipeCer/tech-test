from functools import wraps
from http import HTTPStatus

from common.exceptions import InvalidParameterException
from common.exceptions import ResourceNotFoundException


def handle_exceptions(func):
    """A decorator that handle exceptions and returns a json response"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        status_code = HTTPStatus.OK
        error = ''
        try:
            return func(*args, **kwargs)
        except ResourceNotFoundException as e:
            status_code = HTTPStatus.NOT_FOUND
            error = str(e)
        except InvalidParameterException as e:
            status_code = HTTPStatus.BAD_REQUEST
            error = str(e)
        except Exception as e:
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            error = str(e)
        finally:
            if status_code >= HTTPStatus.BAD_REQUEST:
                response_object = {
                    'status': 'error',
                    'message': error,
                }
                return response_object, status_code
    return wrapper
