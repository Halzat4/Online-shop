class ShopException(Exception):
    pass

class InsufficientQuantityException(ShopException):
    pass

class ItemNotFoundException(ShopException):
    pass

class InvalidDataException(ShopException):
    pass

class EmptyCartException(ShopException):
    pass
