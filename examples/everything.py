
from XRCWidgets import XRCApp, XRCDialog, XRCFrame, XRCPanel



def run():
    app = MainFrame()
    app.MainLoop()


class MainFrame(XRCApp):

    def __init__(self,*args,**kwds):
        XRCApp.__init__(self,*args,**kwds)
        # Internal boolean for radio menu items
        self._reportTB = False
        # Set menus to initial values
        self.getChild("m_edit_reportcb").Check()
        self.getChild("m_edit_tb").Check()

    # Popup report frame showing message
    def report(self,msg):
        print msg

    # Show a SelectPanel inside the desired panel
    def on_select_panel_content(self,parent):
        return SelectPanel(parent)

    # Quit application when "Exit" is selected
    def on_m_file_exit_activate(self,chld):
        self.Close(True)

    # Popup the about dialog from the help menu item
    def on_m_help_about_activate(self,chld):
        dlg = AboutDialog(self)
        dlg.ShowModal()

    # Switch reporting modes on/off with activations
    def on_m_edit_reporttb_activate(self,chld):
        self._reportTB = True
    def on_m_edit_reportcb_activate(self,chld):
        self._reportTB = False

    # Enable/Disable editing of textbox contents
    def on_m_edit_tb_activate(self,chld):
        self.getChild("text_ctrl").Enable(chld.IsChecked())

    # Report value of textbox or combobox when button clicked
    def on_button_activate(self,chld):
        if self._reportTB:
            self.report(self.getChild("text_ctrl").GetValue())
        else:
            self.report(self.getChild("combo_box").GetValue())

    # Print out new values when textbox or combobox change
    def on_text_ctrl_change(self,chld):
        print "TEXTBOX NOW CONTAINS:", chld.GetValue()
    def on_combo_box_change(self,chld):
        print "COMBOBOX NOW CONTAINS:", chld.GetValue()

    # Print out selected value in listbox when changed
    def on_list_box_change(self,chld):
        print "LISTBOX HAS SELECTED:", chld.GetStringSelection()
    # An report it when it is double-clicked
    def on_list_box_activate(self,chld):
        self.report(chld.GetStringSelection())

class SelectPanel(XRCPanel):

    def __init__(self,*args,**kwds):
        XRCPanel.__init__(self,*args,**kwds)
        self.getChild("checkbox").SetValue(True)
 
    # Use checkbox to enable/disable radio buttons
    def on_checkbox_change(self,chld):
        self.getChild("radio_box").Enable(chld.IsChecked())


class AboutDialog(XRCDialog):
    pass


