# Copyright 2004, Ryan Kelly
# Released under the terms of the MIT license
# See the file 'LICENSE.txt' in the main distribution for details.
"""

    XRCWidgets:   GUI Toolkit build around wxPython and the XRC file format

XRC is a wxWidgets standard for describing a GUI in an XML file.  This module
provides facilities to easily incorporate GUI components ('widgets') whose
layout is defined in such a file.

"""

__ver_major__ = 0
__ver_minor__ = 3
__ver_patch__  = 0
__ver_sub__ = ""
__version__ = "%d.%d.%d%s" % (__ver_major__,__ver_minor__,
                              __ver_patch__,__ver_sub__)


import sys
import os

import wx
from wx import xrc

from XRCWidgets.utils import lcurry, XMLDocTree, XMLElementData
from XRCWidgets.connectors import getConnectors


########
##
##  Module-Specific Exception Classes
##
########

class XRCWidgetsError(Exception):
    """Base class for XRCWidgets-specific Exceptions."""
    pass


########
##
##  Base XRCWidget Class
##
########


class NotGiven:
    """Sentinal to indicate that no value was given for an argument."""
    pass


class XRCWidget(object):
    """Mix-in class providing basic XRC behaviors.

    Classes inheriting from this class should also inherit from one of the
    wxPython GUI classes that can be loaded from an XRC file - for example,
    wxPanel or wxFrame.  This class provides the mechanisms for automatically
    locating the XRC file and loading the definitions from it.
    """

    # Name of the XRC file to load content from
    # Will be searched for along the default XRC file path
    # Set at class-level in the subclass to force a specific name
    _xrcfilename = None

    # Location of the XRC file to load content from
    # Can be set at class-level in the subclass to force a specific location
    _xrcfile = None

    # Name of the resource to load from the XRC file, containing definitions
    # for this object.  Defaults to the name of the class.
    # Set at class-level to specify a specific name.
    _xrcname = None

    # Whether not not to look for any connect methods with magic names of
    # the form on_<name>_<action>.  Set to false to make initialisation
    # quicker.
    _useMagicMethods = True

    # When this event is fired, we know the widget is fully initialized.
    _initEvent = wx.EVT_WINDOW_CREATE

    def __init__(self,parent=NotGiven):
        self._xmltree = None
        if self._xrcfile is None:
            self._xrcfile = self._findXRCFile()
        pre = self._getPre()
        if parent is NotGiven:
            #  Assume the caller is doing two-phase creation themselves.
            self.PostCreate(pre)
            self.Bind(self._initEvent,self._handle_on_create)
        else:
            #  Delegate the two-phase create to the XRC loader
            self._loadXRCFile(self._xrcfile,pre,parent)

    def _handle_on_create(self,event=None):
        self.Unbind(self._initEvent)
        wx.CallAfter(self.on_create)

    def on_create(self):
        if self._useMagicMethods:
            self._connectEventMethods()

    def compact(self):
        """Reduce memory/resource usage of the widget.

        This method is called automatically after initialisation to drop
        references to unneeded resources.  These may be accumulated as
        as time goes on, so this method may be called manually to release
        them if they are causing a problem.
        """
        self._xmltree = None

    ##  Methods for dealing with XRC resource files

    @classmethod
    def _findXRCFile(cls):
        """Locate the XRC file for this class, and return its location.

        The name of the XRC file is constructed from the name of the class
        and its defining module.  If this class is named <ClassName> and is
        defined in module <TopLevel>.<SubLevel>.<Package>, then the XRC file
        searched for will be <TopLevel>/<SubLevel>/<Package>.xrc
        The locations within the filesystem which are to be searched are
        obtained from the _getXRCFileLocations() method.
        """
        if cls._xrcfilename is None:
            filePath =  "/".join(cls.__module__.split(".")) + ".xrc"
        else:
            filePath = cls._xrcfilename
        for fileLoc in cls._getXRCFileLocations():
            pth = os.path.join(fileLoc,filePath)
            if os.path.exists(pth):
                return pth
        raise XRCWidgetsError("XRC File '%s' could not be found" % (filePath,))

    @staticmethod
    def _getXRCFileLocations():
        """Iterator over the possible locations where XRC files are kept.

        XRC files can be found in the following places:

            * the directories in sys.path
            * <sys.prefix>/share/XRCWidgets/data

        """
        for p in sys.path:
            yield p
        yield os.path.normpath(os.path.join(sys.prefix,"share/XRCWidgets/data"))

    def _loadXRCFile(self,fileNm,pre,parent):
        """Load this object's definitions from an XRC file.

        The file at <fileNm> should be an XRC file containing a resource
        with the same name as this class.  This resource's definition
        will be loaded into the current object using two-stage initialisation.
        <pre> must be the pre-initialised widget object to load into, and 
        <parent> must be the desired parent of the to-be-created widget.

        The class-level attribute _xrcname may be used to specify an alternate
        name for the resource, rather than the class name.
        """
        xrcres = xrc.XmlResource(fileNm)
        if self._xrcname is None:
            self._xrcname = self.__class__.__name__
        self._loadOn(xrcres,pre,parent,self._xrcname)
        self.PostCreate(pre)
        self.on_create()

    def _makeXmlTree(self):
        """Populate self._xmltree with a representation of the XRC file."""
        if self._xrcname is None:
            self._xrcname = self.__class__.__name__
        if self._xmltree is None:
            xmlfile = file(self._xrcfile)
            self._xmltree = XMLDocTree(xmlfile)

    ##  Methods for obtaining references to child widgets

    def getChild(self,cName):
        """Lookup and return a child widget by name."""
        # This can be done in two ways.  Hopefully, the child has been
        # picked up by xrc and can be obtained using XRCCTRL().
        # If not, parse the XRC file ourselves and try to find it
        chld = xrc.XRCCTRL(self,cName)
        if chld is None:
            # Find XML data on the named child, if possible
            self._makeXmlTree()
            try:
                data = self._xmltree.elements[cName]
            except KeyError:
                raise XRCWidgetsError("Child '%s' not found" % (cName,))
            # Determine object class, pass data off to appropriate method
            mthdNm = "_getChild_%s" % (data.attrs["class"],)
            try:
                mthd = getattr(self,mthdNm)
            except AttributeError:
                raise XRCWidgetsError("Child '%s' of unsupported type '%s'"%(cName,data.attrs["class"],))
            chld = mthd(data)
            if chld is None:
                raise XRCWidgetsError("Child '%s' not found" % (cName,))
        return chld


    def getChildId(self,cName):
        """Obtain the numeric ID of the named child."""
        id = xrc.XRCID(cName)
        if id is not None:
            return id
        chld = self.getChild(cName)
        try:
            return chld.GetId()
        except AttributeError:
            pass
        raise XRCWidgetsError("Child '%s' could not be found" % cName)


    def getChildType(self,cName):
        """Determine the type of the named child.

        The type is returned as a string, typically the 'class' attribute of
        the defining element in the XRC file.  For example, "wxTextCtrl" or
        "wxListBox".
        """
        self._makeXmlTree()
        data = self._xmltree.elements[cName]
        try:
            return data.attrs["class"]
        except KeyError:
            pass
        eStr = "Type of child '%s' could not be determined"
        raise XRCWidgetsError(eStr % (cName,))


    # The following methods are specially-named so they can be found easily
    # Each is named of the form _getChild_<class> where <class> is the
    # requested object's class attribute from the XRC file.  Each will
    # accept an XMLElementData object describing the requested widget and
    # will attempt to return a reference to it.


    def _getChild_wxMenuItem(self,data):
        """Get a reference to a wxMenuItem widget.

        This requires finding the containing wxMenu widget (assumed to be
        the immediate parent) then looking it up by its label, which is
        found in the immediate children.
        """
        # Get the containing menu
        mData = data.parent
        if mData.attrs.get("class") != "wxMenu":
            eStr = "Child '%s' has incorrect parent" % (data.attrs["name"],)
            raise XRCWidgetsError(eStr)
        menu = self._getChild_wxMenu(mData)
            
        # Determine the item label.  If it has a single underscore, remove
        # it as it will be an accelerator key.  If it has more than one,
        # leave it alone. TODO: how does XRC respond in this case?
        # Also remove anything following a tab, as it's an accelerator
        # indicator.
        lbl = None
        for c in data.children:
            if isinstance(c,XMLElementData) and c.name == "label":
                lbl = c.children[0]
        if lbl is None:
            eStr = "Child '%s' has no label" % (data.attrs["name"],)
            raise XRCWidgetsError(eStr)
        lblParts = lbl.split("_")
        if len(lblParts) == 2:
            lbl = "".join(lblParts)
        lbl = lbl.split("\t")[0]
        # Get and return the widget
        for item in menu.GetMenuItems():
            if item.GetLabel() == lbl:
                return item
 

    def _getChild_wxMenu(self,data):
        """Get a reference to a wxMenu widget.

        This requires finding the containing widget, which is either a
        wxMenu or a wxMenuBar, and applying the appropriate method to
        find the menu by label.
        """
        # Determine the item label
        lbl = None
        for c in data.children:
            if isinstance(c,XMLElementData) and c.name == "label":
                lbl = c.children[0]
        if lbl is None:
            eStr = "Child '%s' has no label" % (data.attrs["name"],)
            raise XRCWidgetsError(eStr)
        lblParts = lbl.split("_")
        if len(lblParts) == 2:
            lbl = "".join(lblParts)
        # Find parent widget, get and return reference
        mData = data.parent
        cls = mData.attrs.get("class")
        if cls == "wxMenu":
            menu = self._getChild_wxMenu(mData)
            for item in menu.GetMenuItems():
                if item.GetLabel() == lbl:
                    return item.GetSubMenu()
            eStr = "Child '%s' has incorrect parent" % (data.attrs["name"],)
            raise XRCWidgetsError(eStr)
        elif cls == "wxMenuBar":
            menu = self._getChild_wxMenuBar(mData)
            return menu.GetMenu(menu.FindMenu(lbl))
        else:
            eStr = "Child '%s' has incorrect parent" % (data.attrs["name"],)
            raise XRCWidgetsError(eStr)
 

    def _getChild_wxMenuBar(self,data):
        """Get a reference to a wxMenuBar widget.

        This is done in two stages - first by checking whether XRCCTRL
        has a reference to it, and if not then attempting to obtain it
        from the parent widget's GetMenuBar() method.
        This could probably be done more reliablly - suggestions welcome!
        """
        cName = data.attrs["name"]
        mbar = xrc.XRCCTRL(self,cName)
        if mbar is not None:
            return mbar
        parent = self.getChild(data.parent.attrs["name"])
        try:
            mbar = parent.GetMenuBar()
            return mbar
        except AttributeError:
            eStr = "Child '%s' unreachable from parent." % (cName,)
            raise XRCWidgetsError(eStr)


    ##
    ##  Methods for manipulating child widgets
    ##

    def createInChild(self,cName,toCreate,*args):
        """Create a Widget inside the named child.

        <toCreate> should be a callable (usually a class) returning the widget
        instance. It must take the new widget's parent as first argument. It
        will be called as:

            toCreate(self.getChild(cName),*args)

        The newly created widget will be displayed as the only content of the
        named child, expanded inside a sizer.  A reference to it will also be
        returned.
        """
        chld = self.getChild(cName)
        newWidget = toCreate(chld,*args)
        self.showInWindow(chld,newWidget)
        return newWidget


    def showInChild(self,cName,widget):
        """Show the given widget inside the named child.

        The widget is expected to have the child as its parent.  It will be
        shown in an expandable sizer as the child's only content.
        """
        self.showInWindow(self.getChild(cName),widget)


    def replaceInChild(self,cName,widget):
        """As with showInChild, but destroys the child's previous contents."""
        self.replaceInWindow(self.getChild(cName),widget)


    def showInWindow(self,window,widget):
        """Show the given widget inside the given window.

        The widget is expected to have the window as its parent.  It will be
        shown in an expandable sizer as the windows's only content.
        Any widgets that are currently children of the window will be hidden,
        and a list of references to them will be returned.
        """
        oldChildren = []
        sizer = window.GetSizer()
        if sizer is None:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            # I dont understand th behavior of GetChildren().  The list appears
            # to include duplicate entries for children we have created, and
            # sometimes has links to Dead C++ objects.  Filter out the dead
            # or repeated entries from the list.
            for c in window.GetChildren():
                if c:
                    sizer.Remove(c)
                    if c is not widget:
                        c.Hide()
                        if c not in oldChildren:
                            oldChildren.append(c)
        sizer.Add(widget,1,wx.EXPAND|wx.ADJUST_MINSIZE)
        widget.Show()
        sizer.Layout()
        window.SetSizer(sizer,False)
        window.Layout()
        return oldChildren
 
    def replaceInWindow(self,window,widget):
        """As with showInWindow, but destroys the window's previous contents.
        Does not return a list of references.
        """
        oldChildren = self.showInWindow(window,widget)
        for c in oldChildren:
            c.Destroy()


    ##
    ##  Methods for helping to connect event handlers
    ##

    def _connectEventMethods(self):
        """Automatically connect specially named methods as event handlers.

        An XRCWidget subclass may provide any number of methods named in the
        form 'on_<cname>_<action>' where <cname> is the name of a child
        widget from the XRC file and <action> is an event identifier appropiate
        for that widget type.  This method sets up the necessary event
        connections to ensure that such methods are called when appropriate.
        """
        prfx = "on_"
        connectors = getConnectors()
        for mName in dir(self):
            if mName.startswith(prfx):
                for action in connectors:
                    sffx = "_"+action
                    if mName.endswith(sffx):
                        # Method matches magic pattern, hook it up
                        cName = mName[len(prfx):-1*len(sffx)]
                        hndlr = getattr(self,mName)
                        if not callable(hndlr):
                            break
                        if connectors[action].connect(cName,self,hndlr):
                            break
                        else:
                            eStr = "Widget type <%s> not supported by"
                            eStr = eStr + " '%s' action."
                            cType = self.getChildType(cName)
                            raise XRCWidgetsError(eStr % (cType,action))



########
##
##  XRCWidget subclasses for specific Widgets
##
########


class XRCPanel(XRCWidget,wx.Panel):
    """wx.Panel with XRCWidget behaviors."""

    def __init__(self,parent=NotGiven,id=-1,*args,**kwds):
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PrePanel()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnPanel(pre,parent,nm)



class XRCDialog(XRCWidget,wx.Dialog):
    """wx.Dialog with XRCWidget behaviors."""

    def __init__(self,parent=NotGiven,id=-1,title="Untitled Dialog",*args,**kwds):
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PreDialog()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnDialog(pre,parent,nm)



class XRCFrame(XRCWidget,wx.Frame):
    """wx.Frame with XRCWidget behaviors."""

    def __init__(self,parent=NotGiven,id=-1,title="Untitled Frame",*args,**kwds):
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PreFrame()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnFrame(pre,parent,nm)


class XRCApp(XRCFrame):
    """XRCFrame that can act as a standalone application.

    This class provides a convient way to specify the main frame of
    an application.  It is equivalent to an XRCFrame, but provides
    the following additional methods:

        * MainLoop/ExitMainLoop

    It thus behaves as a simple combination of a wx.Frame and a wx.App, with
    the frame coming from the XRC file and being the TopLevelWindow of
    the application.
    """

    def __init__(self,*args,**kwds):
        parent = None
        self.__app = wx.PySimpleApp(0)
        XRCFrame.__init__(self,parent,*args,**kwds)
        self.__app.SetTopWindow(self)

    def MainLoop(self):
        self.Show()
        self.__app.MainLoop()

    def ExitMainLoop(self):
        self.__app.ExitMainLoop()


