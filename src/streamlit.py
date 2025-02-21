class ValidationException(Exception):
    def __init__(self, message, input_name):
        super().__init__(message)
        self.input_name = input_name
