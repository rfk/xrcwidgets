"""

    XRCWidgets.utils:  Misc utility classes for XRCWidgets framework

"""


##
##  Implementation of callable-object currying via 'lcurry' and 'rcurry'
##

class _curry:
    """Currying Base Class.
    A 'curry' can be thought of as a partially-applied function call.
    Some of the function's arguments are supplied when the curry is created,
    the rest when it is called.  In between these two stages, the curry can
    be treated just like a function.
    """

    def __init__(self,func,*args,**kwds):
        self.func = func
        self.args = args[:]
        self.kwds = kwds.copy()


class lcurry(_curry):
    """Left-curry class.
    This curry places positional arguments given at creation time to the left
    of positional arguments given at call time.
    """

    def __call__(self,*args,**kwds):
        callArgs = self.args + args
        callKwds = self.kwds.copy()
        callKwds.update(kwds)
        return self.func(*callArgs,**callKwds)

class rcurry(_curry):
    """Right-curry class.
    This curry places positional arguments given at creation time to the right
    of positional arguments given at call time.
    """

    def __call__(self,*args,**kwds):
        callArgs = args + self.args
        callKwds = self.kwds.copy()
        callKwds.update(kwds)
        return self.func(*callArgs,**callKwds)


