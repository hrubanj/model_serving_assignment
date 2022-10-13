"""
Module for exceptions raised by the applications' code.
"""


class ModelServingAssignmentException(Exception):
    """
    Base exception for all exceptions raised by the
    applications' code.
    """


class DuplicateItemException(ModelServingAssignmentException):
    """
    Raised when attempting to item whose contents have already
    been saved.
    """
