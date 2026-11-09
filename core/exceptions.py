class NotFound(Exception):
    """Raised when the data in not present in the cache"""
    pass

class InsertionError(Exception):
    """Raised when a new item fails to get inserted in the db and no row id is returned"""
    pass

class InvalidOperation(Exception):
    """Raised when operation is other than any valid and defined operations"""
    pass

class UpdateError(Exception):
    """Raised when there is error in cache update or any other update"""
    pass