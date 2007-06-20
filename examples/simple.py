

from XRCWidgets import XRCApp


class SimpleApp(XRCApp):

    def on_message_change(self,msg):
        print "MESSAGE IS NOW:", msg.GetValue()

    def on_ok_activate(self,bttn):
        print self.getChild("message").GetValue()


def run():
    app = SimpleApp()
    app.MainLoop()


