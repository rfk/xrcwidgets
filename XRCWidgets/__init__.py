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

from utils import lcurry


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


    def __init__(self,parent):
        self._xrcfile = self._findXRCFile()
        self._loadXRCFile(self._xrcfile,parent)
        self._connectEventMethods()


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
        filePath = "/".join(cls.__module__.split(".")) + ".xrc"
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
        yield os.normpath(os.join(sys.prefix,"share/XRCWidgets/data"))
    _getXRCFileLocations = staticmethod(_getXRCFileLocations)


    def _loadXRCFile(self,fileNm,parent):
        """Load this object's definitions from an XRC file.
        The file at <fileNm> should be an XRC file containing a resource
        with the same name as this class.  This resource's definition
        will be loaded into the current object using two-stage initialisation,
        abstracted by the object's '_getPre' and '_loadOn' methods.
        <parent> must be the desired parent of the to-be-created widget.
        """
        self._xrcres = xrc.XmlResource(fileNm)
        pre = self._getPre()
        self._loadOn(self._xrcres,pre,parent,self.__class__.__name__)
        self.PostCreate(pre)

    ##  wxPython 2.5 introduces the PostCreate method to wrap a lot
    ##  of ugliness.  Check the wx version and implement this method
    ##  for versions less than 2.5
    if wx.VERSION[0] <= 2 and not wx.VERSION[1] >= 5:
        def PostCreate(self,pre):
            self.this = pre.this
            self._setOORInfo(self)


    ##
    ##  Methods for manipulating child widgets
    ##

    def _getChildName(self,cName):
        """This method allows name-mangling to be inserted, if required."""
        return cName


    def getChild(self,cName):
        """Lookup and return a child widget by name."""
        chld = xrc.XRCCTRL(self,self._getChildName(cName))
        if chld is None:
            raise XRCWidgetsError("Child '%s' not found" % (cName,))


    def createInChild(self,cName,toCreate,*args):
        """Create a Widget inside the named child.
        <toCreate> should be a callable returning the widget instance (usually
        its class) that takes the new widget's parent as first argument. It
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
            for c in window.GetChildren():
                sizer.Remove(c)
                c.Hide()
                oldChildren.append(c)
        sizer.Add(widget,1,wx.EXPAND|wx.ADJUST_MINSIZE)
        widget.Show()
        sizer.Layout()
        window.SetSizer(sizer,False)
        window.Layout()
 
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
                        chldName = mName[len(prfx):-1*len(sffx)]
                        chld = self.getChild(chldName)
                        cnctFuncName = self._EVT_ACTIONS[action]
                        cnctFunc = getattr(self,cnctFuncName)
                        cnctFunc(chld,mName)
                        break

    ##  _EVT_ACTIONS is a dictionary mapping the names of actions to the names
    ##  of methods of this class that should be used to connect events for
    ##  that action.  Such methods must take the child widget in question
    ##  and the name of the method to connect to, and need not return any
    ##  value.

    _EVT_ACTIONS = {
                   "change": "_connectAction_Change",
                   "content": "_connectAction_Content",
                   }


    def _connectAction_Change(self,chld,mName):
        """Arrange to call method <mName> when <chld>'s value is changed.
        The events connected by this method will be different depending on the
        precise type of <chld>.  The method to be called should expect the
        control itself as its only argument.  It will be wrapped so that the
        event is skipped in order to avoid a lot of cross-platform issues.
        """
        # retreive the method to be called and wrap it appropriately
        handler = getattr(self,mName)
        handler = lcurry(handler,chld)
        handler = lcurry(_EvtHandleAndSkip,handler)

        # enourmous switch on child widget type
        if isinstance(chld,wx.TextCtrl) or isinstance(chld,wx.TextCtrlPtr):
            EVT_TEXT_ENTER(self,ctrl.GetId(),handler)
            EVT_KILL_FOCUS(ctrl,handler)
        elif isinstance(chld,wx.CheckBox) or isinstance(chld,wx.CheckBoxPtr):
            EVT_CHECKBOX(self,ctrl.GetId(),handler)
        elif isinstance(chld,wx.CheckBox) or isinstance(chld,wx.CheckBoxPtr):
            pass
        else:
            eStr = "Widget type not supported by 'Change' action."
            raise XRCWidgetsError(eStr)
        


########
##
##  XRCWidget subclasses for specific Widgets
##
########


class XRCPanel(wx.Panel,XRCWidget):
    """wx.Panel with XRCWidget behaviors."""

    def __init__(self,parent,*args):
        wx.Panel.__init__(self,parent,*args)
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PrePanel()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnPanel(pre,parent,nm)



class XRCFrame(wx.Frame,XRCWidget):
    """wx.Frame with XRCWidget behaviors."""

    def __init__(self,parent,*args):
        wx.Frame.__init__(self,parent,*args)
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PreFrame()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnFrame(pre,parent,nm)



class XRCDialog(wx.Dialog,XRCWidget):
    """wx.Dialog with XRCWidget behaviors."""

    def __init__(self,parent,*args):
        wx.Dialog.__init__(self,parent,*args)
        XRCWidget.__init__(self,parent)

    def _getPre(self):
        return wx.PreDialog()

    def _loadOn(self,XRCRes,pre,parent,nm):
        return XRCRes.LoadOnDialog(pre,parent,nm)


########
##
##  Miscellaneous Useful Functions
##
########

def _EvtHandleAndSkip(toCall,evnt):
    """Handle an event by invoking <toCall> then <evnt>.Skip().
    This function does *not* pass <evnt> as an argument to <toCall>,
    it simply invokes it directly.
    """
    toCall()
    evnt.Skip()



