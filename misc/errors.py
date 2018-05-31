"""
Defines all custom errors used in this library.
"""

class CommandTestError(RuntimeError):
    """
    Defines a Command Test Error called when an error has to be forced
    (with -fe in command prompt or force_error=True in CommandTester)
    """
    pass

class OperatorInputTypeError(RuntimeError):
    """
    Defines an error that is raised when the input type for an item in an Operator
    is not valid. For more info see grammar.operators package.
    """
    pass
