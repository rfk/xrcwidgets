# Copyright 2004, Ryan Kelly
# Released under the terms of the wxWindows Licence, version 3.
# See the file 'lincence/preamble.txt' in the main distribution for details.
"""

    XRCWidgets:   GUI Toolkit build around wxPython and the XRC file format

XRC is a wxWidgets standard for describing a GUI in an XML file.  This module
provides facilities to easily incorporate GUI components ('widgets') whose
layout is defined in such a file.

"""

import sys
import os

import wx
from wx import xrc

from XRCWidgets.utils import lcurry, XMLDocTree, XMLElementData


#  The following seems to work around a wxWidgets bug which is making
#  XRCApp segfault, simply by creating a PySimpleApp.
from wxPython import wx as wx2
_WorkAround_app = wx2.wxPySimpleApp(0)
del _WorkAround_app



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

class XRCWidget:
    """Mix-in Class providing basic XRC behaviors.

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


    def __init__(self,parent):
        # Attribute initialisation
        self._xmltree = None

        # XRC resource loading
        if self._xrcfile is None:
            self._xrcfile = self._findXRCFile()
        self._loadXRCFile(self._xrcfile,parent)
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
    _findXRCFile = classmethod(_findXRCFile)


    def _getXRCFileLocations():
        """Iterator over the possible locations where XRC files are kept.
        XRC files can be found in the following places:

            * the directories in sys.path
            * <sys.prefix>/share/XRCWidgets/data

        """
        for p in sys.path:
            yield p
        yield os.path.normpath(os.path.join(sys.prefix,"share/XRCWidgets/data"))
    _getXRCFileLocations = staticmethod(_getXRCFileLocations)


    def _loadXRCFile(self,fileNm,parent):
        """Load this object's definitions from an XRC file.

        The file at <fileNm> should be an XRC file containing a resource
        with the same name as this class.  This resource's definition
        will be loaded into the current object using two-stage initialisation,
        abstracted by the object's '_getPre' and '_loadOn' methods.
        <parent> must be the desired parent of the to-be-created widget.

        The class-level attribute _xrcname may be used to specify an alternate
        name for the resource, rather than the class name.
        """
        self._xrcres = xrc.XmlResource(fileNm)
        pre = self._getPre()
        if self._xrcname is not None:
            resName = self._xrcname
        else:
            resName = self.__class__.__name__
        self._loadOn(self._xrcres,pre,parent,resName)
        self.PostCreate(pre)


    def _makeXmlTree(self):
        """Populate self._xmltree with a representation of the XRC file."""
        if self._xmltree is None:
            xmlfile = file(self._xrcfile)
            self._xmltree = XMLDocTree(xmlfile)


    ##  wxPython 2.5 introduces the PostCreate method to wrap a lot
    ##  of ugliness.  Check the wx version and implement this method
    ##  for versions less than 2.5
    if wx.VERSION[0] <= 2 and not wx.VERSION[1] >= 5:
        def PostCreate(self,pre):
            self.this = pre.this
            self._setOORInfo(self)


    ##
    ##  Methods for obtaining references to child widgets
    ##

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
            except:
                raise XRCWidgetsError("Child '%s' not found" % (cName,))
            # Determine object class, pass data off to appropriate method
            mthdNm = "_getChild_%s" % (data.attrs["class"],)
            try:
                mthd = getattr(self,mthdNm)
            except AttributeError:
                raise XRCWidgetsError("Child '%s' of unsupported type"%(cName,))
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
            return parent.GetMenuBar()
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
        for mName in dir(self):
            if mName.startswith(prfx):
                for action in self._EVT_ACTIONS:
                    sffx = "_"+action
                    if mName.endswith(sffx):
                        # Method matches magic pattern, hook it up
                        cName = mName[len(prfx):-1*len(sffx)]
                        handler = getattr(self,mName)
                        if not callable(handler):
                            break

                        cnctFuncName = self._EVT_ACTIONS[action]
                        cnctFunc = getattr(self,cnctFuncName)
                        cnctFunc(cName,handler)
                        break

    ##  _EVT_ACTIONS is a dictionary mapping the names of actions to the names
    ##  of methods of this class that should be used to connect events for
    ##  that action.  Such methods must take the name of the child in question
    ##  and the callable object to connect to, and need not return any value.

    _EVT_ACTIONS = {
                   "change": "_connectAction_Change",
                   "content": "_connectAction_Content",
                   "activate": "_connectAction_Activate",
                   }


    def _connectAction_Change(self,cName,handler):
        """Arrange to call <handler> when widget <cName>'s value is changed.

        The events connected by this method will be different depending on the
        precise type of <child>.  The handler to be called should expect the
        control itself as an optional argument, which may or may not be received
        depending on the type of control.  It may be wrapped so that the
        event is skipped in order to avoid a lot of cross-platform issues.
        """
        cType = self.getChildType(cName)

        # enourmous switch on child widget type
        # TODO: this would be better implemented using a dictionary
        if cType == "wxTextCtrl":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandleAndSkip,handler)
            wx.EVT_TEXT_ENTER(self,child.GetId(),handler)
            wx.EVT_KILL_FOCUS(child,handler)
        elif cType == "wxCheckBox":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_CHECKBOX(self,self.getChildId(cName),handler)
        elif cType == "wxListBox":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_LISTBOX(self,self.getChildId(cName),handler)
        elif cType == "wxComboBox":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_COMBOBOX(self,self.getChildId(cName),handler)
            wx.EVT_TEXT_ENTER(self,self.getChildId(cName),handler)
        elif cType == "wxRadioBox":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_RADIOBOX(self,self.getChildId(cName),handler)
        elif cType == "wxChoice":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_CHOICE(self,self.getChildId(cName),handler)
        else:
            eStr = "Widget type <%s> not supported by 'Change' action."
            raise XRCWidgetsError(eStr % cType)
        


    def _connectAction_Content(self,cName,handler):
        """Replace the content of <child> with that returned by method <mName>.

        Strictly, this is not an 'event' handler as it only performs actions
        on initialisation.  It is however a useful piece of functionality and
        fits nicely in the framework.  <handler> will be called with the child
        widget as its only argument, and should return a wxWindow.  This
        window will be shown as the only content of the child window.
        """
        child = self.getChild(cName)
        widget = handler(child)
        self.replaceInWindow(child,widget)


    def _connectAction_Activate(self,cName,handler):
        """Arrange to call <handler> when child <cName> is activated.
        The events connected by this method will be different depending on the
        precise type of the child.  The method to be called may expect the
        control itself as a default argument, passed depending on the type
        of the control.
        """
        cType = self.getChildType(cName)

        # enourmous switch on child widget type
        if cType == "wxButton":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_BUTTON(self,child.GetId(),handler)
        elif cType == "wxCheckBox":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_CHECKBOX(self,child.GetId(),handler)
        elif cType == "wxMenuItem":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_MENU(self,child.GetId(),handler)
        elif cType == "tool":
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_MENU(self,self.getChildId(cName),handler)
        elif cType == "wxListBox":
            child = self.getChild(cName)
            handler = lcurry(handler,child)
            handler = lcurry(_EvtHandle,handler)
            wx.EVT_LISTBOX_DCLICK(self,self.getChildId(cName),handler)
        else:
            eStr = "Widget type <%s> not supported by 'Activate' action."
            raise XRCWidgetsError(eStr % child.__class__)
        


########
##
##  XRCWidget subclasses for specific Widgets
##
########


class XRCPanel(wx.Panel,XRCWidget):
    """wx.Panel with XRCWidget behaviors."""

    def __init__(self,parent,id=-1,*args,**kwds):
        wx.Panel.__init__(self,parent,id,*args,**kwds)
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PrePanel()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnPanel(pre,parent,nm)



class XRCDialog(wx.Dialog,XRCWidget):
    """wx.Dialog with XRCWidget behaviors."""

    def __init__(self,parent,id=-1,title="Untitled Dialog",*args,**kwds):
        wx.Dialog.__init__(self,parent,id,title,*args,**kwds)
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PreDialog()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnDialog(pre,parent,nm)



class XRCFrame(wx.Frame,XRCWidget):
    """wx.Frame with XRCWidget behaviors."""

    def __init__(self,parent,id=-1,title="Untitled Frame",*args,**kwds):
        wx.Frame.__init__(self,parent,id,title,*args,**kwds)
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
        XRCFrame.__init__(self,parent,*args,**kwds)
        self.__app = wx.PySimpleApp(0)
        self.__app.SetTopWindow(self)
        wx.EVT_CLOSE(self,self.OnClose)

    def MainLoop(self):
        self.Show()
        self.__app.MainLoop()

    def ExitMainLoop(self):
        self.__app.ExitMainLoop()

    def OnClose(self,evnt):
        self.Destroy()


########
##
##  Miscellaneous Useful Functions
##
########


def _EvtHandle(toCall,evnt):
    """Handle an event by invoking <toCall> without arguments.
    The event itself is ignored.
    """
    toCall()

def _EvtHandleAndSkip(toCall,evnt):
    """Handle an event by invoking <toCall> then <evnt>.Skip().
    This function does *not* pass <evnt> as an argument to <toCall>,
    it simply invokes it directly.
    """
    toCall()
    evnt.Skip()



