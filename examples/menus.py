

from wxPython import wx
from XRCWidgets import XRCFrame


class MenuFrame(XRCFrame):

    pass



def run():
    app = wx.wxPySimpleApp(0)
    frame = MenuFrame(None)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()

