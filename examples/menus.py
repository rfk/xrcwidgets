

from wxPython import wx
from XRCWidgets import XRCApp


class MenuApp(XRCApp):

    def on_m_file_exit_activate(self,ctrl):
        self.Close()

    def on_m_file_new_doc_activate(self,ctrl):
        print self.getChild("m_file_new_doc").GetLabel()
        print "NEW DOCUMENT"

    def on_m_file_new_tmpl_activate(self,ctrl):
        print "NEW TEMPLATE"

    def on_m_help_about_activate(self,ctrl):
        print "SHOWING ABOUT DIALOG..."



def run():
    app = MenuApp()
    app.MainLoop()

