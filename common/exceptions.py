class ModelServingAssignmentException(Exception):
    """
    Base exception for all exceptions raised by the
    applications' code.
    """
    pass

class DuplicateItemException(ModelServingAssignmentException):
    """
    Raised when attempting to item whose contents have already
    been saved.
    """
    pass