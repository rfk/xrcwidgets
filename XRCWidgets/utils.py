# Copyright 2004, Ryan Kelly
# Released under the terms of the wxWindows Licence, version 3.
# See the file 'lincence/preamble.txt' in the main distribution for details.
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


##
##  Basic XML parsing for our own reading of the file
##

from xml.parsers import expat

class XMLElementData:
    """Represents information about an element gleaned from an XML file.

    This class represents an XML element as as much information as needed
    about from the containing XML file.  The important attribues are:

        * name:      name of XML element
        * attrs:     dictionary of key/value pairs of element attributes
        * parent:    XMLElementData representing parent element
        * children:  list containing XMLElementData objects and/or strings
                     of the element's children

    Instances of this class are not intended to be created directly.  Rather,
    they should be created using the <findElementData> function from this
    module.
    """

    def __init__(self):
        self.name = None
        self.attrs = {}
        self.parent = None
        self.children = []


def findElementData(xmlfile,checker):
    """Create and return XMLElemenetData for the requested element.

    This function parses the file-like object <xmlfile> in search of a
    particule XML element.  The callable object <checker> will be called
    with the arguments (<name>,<attrs>) for each element processed, and
    must return True only if that element matches the one being searched for.
    The result is returned as an XMLElementData object.
    """
    parser = expat.ParserCreate()
    handler = _ElementHandler(checker)
    parser.StartElementHandler = handler.onStart
    parser.EndElementHandler = handler.onEnd
    parser.CharacterDataHandler = handler.onCdata
    parser.ParseFile(xmlfile)
    return handler.getElement()


class _ElementHandler:
    """Private handlers for XML parsing with <findElementData>.

    This class provides methods <onStart>, <onEnd> and <onCdata> which can be
    used for the parsing event handlers.
    """

    ## TODO: only keep the parts of the tree that are needed

    def __init__(self,checker):
        "Constructor. <checker> must be search element identifying function."
        self._checker = checker
        self._curElem = None
        self._theElem = None

    def onStart(self,name,attrs):
        data = XMLElementData()
        data.name = name
        data.attrs = attrs
        data.parent = self._curElem
        if self._curElem is not None:
            self._curElem.children.append(data)
        self._curElem = data
        if self._theElem is None:
            if self._checker(name,attrs):
                self._theElem = data

    def onEnd(self,name):
        self._curElem = self._curElem.parent

    def onCdata(self,cdata):
        cdata = cdata.strip()
        if cdata != "":
            self._curElem.children.append(cdata)

    def getElement(self):
        """Called to retreive element data after parsing."""
        return self._theElem


