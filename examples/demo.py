
from wxPython import wx

from XRCWidgets import XRCFrame, XRCDialog
from demo_widgets import DemoPanel

#  Simple frame to demonstrate the use of menus and toolbar.
#  Also shows how on__content() can be used to place widgets at creation time.
class DemoFrame(XRCFrame):

    def on_m_file_exit_activate(self,ctrl):
        """Close the application"""
        self.Close()

    def on_m_file_new_activate(self,ctrl):
        """Create a new DemoPanel in the display area."""
        dsp = self.getChild("displayarea")
        p = DemoPanel(dsp)
        self.replaceInWindow(dsp,p)

    def on_m_help_about_activate(self,ctrl):
        """Show the About dialog."""
        dlg = AboutDemoDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_displayarea_content(self,ctrl):
        """Initialise display area to contain a DemoPanel."""
        return DemoPanel(ctrl)


# About Dialog demonstrates how to explicitly set widget name
# Other properies such as filename (_xrcfilename) and file location
# (_xrcfile) can be set similarly
class AboutDemoDialog(XRCDialog):
    _xrcname = "about"


# Instantiate and run the application
def run():
    app = wx.wxPySimpleApp(0)
    frame = DemoFrame(None)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()


