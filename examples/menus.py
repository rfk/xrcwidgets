

from wxPython import wx
from XRCWidgets import XRCFrame


class MenuFrame(XRCFrame):

    def on_m_file_exit_activate(self,ctrl):
        self.Close()

    def on_m_file_new_doc_activate(self,ctrl):
        print "NEW DOCUMENT"

    def on_m_file_new_tmpl_activate(self,ctrl):
        print "NEW TEMPLATE"



def run():
    app = wx.wxPySimpleApp(0)
    frame = MenuFrame(None)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()

