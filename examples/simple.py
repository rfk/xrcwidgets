

from wxPython import wx
from XRCWidgets import XRCFrame


class SimpleFrame(XRCFrame):

    def on_message_change(self,msg):
        print "MESSAGE IS NOW:", msg.GetValue()


    def on_ok_activate(self,bttn):
        print self.getChild("message").GetValue()



def run():
    app = wx.wxPySimpleApp(0)
    frame = SimpleFrame(None)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()

