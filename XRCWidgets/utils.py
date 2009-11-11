# Copyright 2004-2009, Ryan Kelly
# Released under the terms of the MIT Licence.
# See the file 'LICENSE.txt' in the main distribution for details.
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
##  Basic XML parsing for our own reading of the XRC file
##

from xml.parsers import expat

class XMLNameError(Exception): pass

class XMLElementData:
    """Represents information about an element obtained from an XML file.

    This class represents an XML element and as much information as needed
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


class XMLDocTree:
    """Represents an XML document as a tree of XMLElementData objects.

    This class provides the attribute 'root' which is the root XML
    element, and the dictionary 'elements' which maps values of the XML
    attribute "name" to the XMLElementData object for the corresponding
    element.
    """

    def __init__(self,xmlfile):
        """XMLDocTree initialiser.
        A file-like object containing the XML data must be given.
        """

        self.root = None
        self._curElem = None
        self.elements = {}

        parser = expat.ParserCreate()
        parser.StartElementHandler = self.onStart
        parser.EndElementHandler = self.onEnd
        parser.CharacterDataHandler = self.onCdata
        parser.ParseFile(xmlfile)


    def onStart(self,name,attrs):
        data = XMLElementData()
        data.name = name
        data.attrs = attrs
        data.parent = self._curElem
        if self._curElem is not None:
            self._curElem.children.append(data)
        self._curElem = data
        try:
            nm = attrs["name"]
            if self.elements.has_key(nm):
                raise XMLNameError("Duplicate element name: '%s'" % (nm,))
            self.elements[nm] = data
        except KeyError:
            pass


    def onEnd(self,name):
        if self._curElem.parent is not None:
            self._curElem = self._curElem.parent
        else:
            self.root = self._curElem
            self._curElem = None

    def onCdata(self,cdata):
        cdata = cdata.strip()
        if cdata != "":
            # Append CData to previous child if it was also CData
            if len(self._curElem.children) == 0:
                self._curElem.children.append(cdata)
            else:
                prevChild = self._curElem.children[-1]
                if not isinstance(prevChild,XMLElementData):
                    self._curElem.children[-1] = "%s %s" % (prevChild,cdata)
                else:
                    self._curElem.children.append(cdata)



