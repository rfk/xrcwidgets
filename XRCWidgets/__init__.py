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
        <parent> must be the parent of the to-be-created widget.
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


    ##  Methods for manipulating child widgets

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


