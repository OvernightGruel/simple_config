class BaseError(Exception):
    pass


class ConvertError(BaseError):
    pass


class FileDoesNotExist(BaseError):
    pass


class VariableNotExist(BaseError):
    pass


class NotConfigured(BaseError):
    pass


class InvalidConfig(BaseError):
    pass
