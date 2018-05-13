"""
Defines all custom errors used in this library.
"""

class CommandTestError(RuntimeError):
    """
    Defines a Command Test Error called when an error has to be forced
    (with -fe in command prompt or force_error=True in CommandTester)
    """
    pass
