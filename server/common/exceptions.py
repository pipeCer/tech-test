class InvalidParameterException(Exception):
    def __init__(self, message):
        super(InvalidParameterException, self).__init__(message)


class ResourceNotFoundException(Exception):
    def __init__(self, message):
        super(ResourceNotFoundException, self).__init__(message)
