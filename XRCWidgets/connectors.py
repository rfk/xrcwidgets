"""

    XRCWidgets.connectors:  Classes to connect events for XRCWidgets
    
This module provides subclasses of Connector, which are responsible
for hooking up event listeners for a particular type of action
within the XRCWidgets framework.  These are key to the "Magic Methods"
functionality of XRCWidgets.

For example, the method named:
    
        on_mytextbox_change()
        
Is connected using the ChangeConnector() class.  The class for a
given event action can be determined by inspecting the dictionary
returned by the function getConnectors().

"""

import wx
from XRCWidgets.utils import lcurry

class Connector:
    """Class responsible for connecting events within XRCWidgets
    Subclasses of this abstract base class provide the method
    connect() which will produce the necessary connection
    based on the named child type.
    """
    
    # Internally, the connections are managed by a dictionary of
    # methods, one per child type.  The entries are listed on
    # the class
    _cons_entries = ()
    
    def __init__(self):
        self._cons = {}
        for entry in self._cons_entries:
            self._cons[entry] = getattr(self,"connect_"+entry)
    
    def connect(self,cName,parent,handler):
        """Connect <handler> to the named child of the given parent.
        This method must return True if the connection succeeded,
        False otherwise.
        """
        cType = parent.getChildType(cName)
        if self._cons.has_key(cType):
            return self._cons[cType](cName,parent,handler)
        return False
    

class ChangeConnector(Connector):
    """Connector for the "change" event.
    This event is activated when the value of a control changes
    due to user input.  The handler should expect a reference
    to the control itself as its only argument.
    """

    _cons_entries = ("wxTextCtrl","wxCheckBox","wxListBox",
                     "wxComboBox","wxRadioBox","wxChoice",
                     "wxSlider")
    
    def connect_wxTextCtrl(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandleAndSkip,handler)
        wx.EVT_TEXT_ENTER(parent,child.GetId(),handler)
        wx.EVT_KILL_FOCUS(child,handler)
        return True
    
    def connect_wxCheckBox(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_CHECKBOX(parent,parent.getChildId(cName),handler)
        return True
        
    def connect_wxListBox(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_LISTBOX(parent,parent.getChildId(cName),handler)
        return True
        
    def connect_wxComboBox(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_COMBOBOX(parent,parent.getChildId(cName),handler)
        wx.EVT_TEXT_ENTER(parent,parent.getChildId(cName),handler)
        return True
        
    def connect_wxRadioBox(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_RADIOBOX(parent,parent.getChildId(cName),handler)
        return True
        
    def connect_wxChoice(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_CHOICE(parent,parent.getChildId(cName),handler)
        return True
        
    def connect_wxSlider(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
	child.Bind(wx.EVT_SCROLL,handler)
        return True


class ContentConnector(Connector):
    """Connector handling the 'content' event.
    This is a sort of pseudo-event that is only triggered
    once, at widget creation time.  It is used to programatically
    create the child content of a particular widget.  The
    event handler must expect the named child widget as its
    only argument, and return the newly created content for that
    child widget.
    """
    
    def connect(self,cName,parent,handler):
        child = parent.getChild(cName)
        widget = handler(child)
        parent.replaceInWindow(child,widget)
        return True


class ActivateConnector(Connector):
    """Connector handling the 'activate' event.
    This event is fired when a control, such as a button, is
    activated by the user - similar to a 'click' event.
    The events connected by this method will be different depending on the
    precise type of the child.  The method to be called may expect the
    control itself as a default argument, passed depending on the type
    of the control.
    """
    
    _cons_entries = ("wxButton","wxBitmapButton","wxCheckBox",
                     "wxMenuItem", "tool","wxListBox")
    
    def connect_wxButton(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_BUTTON(parent,child.GetId(),handler)
        return True
        
    def connect_wxBitmapButton(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_BUTTON(parent,child.GetId(),handler)
        return True
        
    def connect_wxCheckBox(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_CHECKBOX(parent,child.GetId(),handler)
        return True
        
    def connect_wxMenuItem(self,cName,parent,handler):
        handler = lcurry(_EvtHandleWithEvt,handler)
        cID = parent.getChildId(cName)
        wx.EVT_MENU(parent,cID,handler)
        return True
    
    def connect_tool(self,cName,parent,handler):
        handler = lcurry(_EvtHandleWithEvt,handler)
        wx.EVT_MENU(parent,parent.getChildId(cName),handler)
        return True
        
    def connect_wxListBox(self,cName,parent,handler):
        child = parent.getChild(cName)
        handler = lcurry(handler,child)
        handler = lcurry(_EvtHandle,handler)
        wx.EVT_LISTBOX_DCLICK(parent,parent.getChildId(cName),handler)
        return True


def getConnectors():
    """Construct and return dictionary of connectors."""
    cons = {}
    cons["change"] = ChangeConnector()
    cons["content"] = ContentConnector()
    cons["activate"] = ActivateConnector()
    return cons
    

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

def _EvtHandleWithEvt(toCall,evnt):
    """Handle an event by invoking <toCall> with the event as argument.
    """
    toCall(evnt)

def _EvtHandleAndSkip(toCall,evnt):
    """Handle an event by invoking <toCall> then <evnt>.Skip().
    This function does *not* pass <evnt> as an argument to <toCall>,
    it simply invokes it directly.
    """
    toCall()
    evnt.Skip()

        
        
