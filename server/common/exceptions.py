class InvalidParameterException(Exception):
    def __init__(self, message):
        super(InvalidParameterException, self).__init__(message)


class ResourceNotFoundException(Exception):
    def __init__(self, message):
        super(ResourceNotFoundException, self).__init__(message)


class CustomException(Exception):
    def __init__(self, message='Error', status_code=500):
        super(CustomException, self).__init__(message)
        self.status_code = status_code
