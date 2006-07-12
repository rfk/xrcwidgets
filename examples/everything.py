#
#  everything.py - large, useless app for demonstrating the functionality
#                  of the XRCWidgets toolkit
#

from XRCWidgets import XRCApp, XRCDialog, XRCFrame, XRCPanel



def run():
    app = MainFrame()
    app.MainLoop()


#  The main application window
class MainFrame(XRCApp):

    def __init__(self,*args,**kwds):
        XRCApp.__init__(self,*args,**kwds)
        # Internal boolean for radio menu items
        self._reportTB = False
        # Set menus to initial values
        # This is currently broken on my Linux machine...
        self.getChild("m_edit_reportcb").Check()
        self.getChild("m_edit_tb").Check()

    # Popup report frame showing message
    def report(self,msg):
        frm = ReportFrame(msg,self)
        frm.Show()

    # Show a SelectPanel inside the desired panel
    def on_select_panel_content(self,parent):
        return SelectPanel(parent)

    # Quit application when "Exit" is selected
    def on_m_file_exit_activate(self,evt):
        self.Close(True)

    # Popup the about dialog from the help menu item
    def on_m_help_about_activate(self,evt):
        dlg = AboutDialog(self)
        dlg.ShowModal()

    def on_t_about_activate(self,evt):
        dlg = AboutDialog(self)
        dlg.ShowModal()

    def on_t_report_activate(self,evt):
        self.report("Reporting from the toolbar!")

    # Switch reporting modes on/off with activations
    def on_m_edit_reporttb_activate(self,evt):
        self._reportTB = True
    def on_m_edit_reportcb_activate(self,evt):
        self._reportTB = False

    # Enable/Disable editing of textbox contents
    def on_m_edit_tb_activate(self,evt):
        self.getChild("text_ctrl").Enable(evt.IsChecked())

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


# Panel containing some additional widgets
class SelectPanel(XRCPanel):

    def __init__(self,*args,**kwds):
        XRCPanel.__init__(self,*args,**kwds)
        self.getChild("checkbox").SetValue(True)
 
    # Use checkbox to enable/disable radio buttons
    def on_checkbox_change(self,chld):
        self.getChild("radio_box").Enable(chld.IsChecked())

    # Print radiobox selections to the screen
    def on_radio_box_change(self,chld):
        print "RADIOBOX HAS SELECTED:", chld.GetStringSelection()

    # Simialr for the wxChoice
    def on_choice_change(self,chld):
        print "CHOICE HAS SELECTED:", chld.GetStringSelection()


# Simple static about dialog
class AboutDialog(XRCDialog):
    pass


# Popup Frame for reporting Values
class ReportFrame(XRCFrame):

    def __init__(self,msg,*args,**kwds):
        XRCFrame.__init__(self,*args,**kwds)
        self.getChild("value_text").SetLabel(msg)

    def on_done_button_activate(self,evt):
        self.Destroy()


