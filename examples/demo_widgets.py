
from XRCWidgets import XRCPanel

class DemoPanel(XRCPanel):
    """Simple panel allowing two numbers to be added.
    The values in the textboxes are tracked as they are changed, reverting
    to previous values if a non-number is entered.  The result is updated
    when 'add' is pressed.
    """

    def __init__(self,*args,**kwds):
        XRCPanel.__init__(self,*args,**kwds)
        self._val1 = 0
        self._val2 = 0

    def on_val1_change(self,ctrl):
        newVal = ctrl.GetValue()
        try:
            newVal = float(newVal)
            self._val1 = newVal
        except ValueError:
            ctrl.SetValue(str(self._val1))

    def on_val2_change(self,ctrl):
        newVal = ctrl.GetValue()
        try:
            newVal = float(newVal)
            self._val2 = newVal
        except ValueError:
            ctrl.SetValue(str(self._val2))

    def on_add_activate(self,ctrl):
        result = self._val1 + self._val2
        self.getChild("result").SetValue(str(result))

