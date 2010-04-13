

import wx
from XRCWidgets import XRCApp, XRCDialog

from demo_widgets import DemoPanel

#  Simple frame to demonstrate the use of menus and toolbar.
#  Also shows how on_content() can be used to place widgets at creation time.
class DemoApp(XRCApp):

    def on_m_file_exit_activate(self,evt):
        """Close the application"""
        self.Close()

    def on_m_file_new_activate(self,evt):
        """Create a new DemoPanel in the display area."""
        dsp = self.getChild("displayarea")
        p = DemoPanel(dsp)
        self.replaceInWindow(dsp,p)

    def on_tb_new_activate(self,evt):
        self.on_m_file_new_activate(None)

    def on_m_help_about_activate(self,evt):
        """Show the About dialog."""
        dlg = AboutDemoDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_tb_about_activate(self,evt):
        self.on_m_help_about_activate(None)

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
    app = DemoApp()
    app.MainLoop()


