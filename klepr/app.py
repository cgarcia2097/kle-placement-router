#!/usr/bin/env python
import sys
from sys import flags

import wx
from wx.__version__ import VERSION
from wx.core import ButtonNameStr, DD_DEFAULT_STYLE, EVT_LIST_DELETE_ALL_ITEMS, EVT_LIST_DELETE_ITEM, EVT_LIST_ITEM_FOCUSED, EVT_LIST_ITEM_SELECTED, MessageBox, Panel

from klepr.kleprtools import pcb
from klepr.kleprtools import key

import json
import random
import math

APP_WIDTH = 640
APP_HEIGHT = 600

layout = []
layoutFile = ""
layoutText = ""

class EditDialog(wx.Dialog):
    """ Dialog box for editing table entries. Only called when editing """

    def __init__(self, *args, **kwargs):
        super(EditDialog, self).__init__(*args, **kwargs)
        
        self.SetSize((240,240))
        self.Center()
        self.SetTitle("Change Reference Entry")

    def LoadEntryValues(self, entry):
        """ Loads the values of current entry into dialog """
        self.entry = entry
        self.reference = self.entry.reference
        self.off_x = str(self.entry.off_x)
        self.off_y = str(self.entry.off_y)
        self.angle = str(self.entry.angle)

        print(self.reference, self.off_x, self.off_y, self.angle)

    def InitUI(self):
        """ Initialize the dialog box """

        vbox = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        ########## Add the text entry fields

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        refTxt = wx.StaticText(self, label="Reference", style=wx.ALIGN_LEFT)
        refTxt.SetFont(font)
        self.refTxtCtrl = wx.TextCtrl(self)
        self.refTxtCtrl.write(self.reference)
        hbox1.Add(refTxt, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        hbox1.Add(self.refTxtCtrl, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        vbox.Add(hbox1, flag=wx.ALL | wx.EXPAND, border=5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        xTxt = wx.StaticText(self, label="X Offset (mm)", style=wx.ALIGN_LEFT)
        xTxt.SetFont(font)
        self.xTxtCtrl = wx.TextCtrl(self)
        self.xTxtCtrl.write(self.off_x)
        hbox2.Add(xTxt, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        hbox2.Add(self.xTxtCtrl, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALL | wx.EXPAND, border=5)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        yTxt = wx.StaticText(self, label="Y Offset (mm)", style=wx.ALIGN_LEFT)
        yTxt.SetFont(font)
        self.yTxtCtrl = wx.TextCtrl(self)
        self.yTxtCtrl.write(self.off_y)
        hbox3.Add(yTxt, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        hbox3.Add(self.yTxtCtrl, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        vbox.Add(hbox3, flag=wx.ALL | wx.EXPAND, border=5)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        aTxt = wx.StaticText(self, label="Angle (deg)", style=wx.ALIGN_LEFT)
        aTxt.SetFont(font)
        self.aTxtCtrl = wx.TextCtrl(self)
        self.aTxtCtrl.write(self.angle)
        hbox4.Add(aTxt, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        hbox4.Add(self.aTxtCtrl, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        vbox.Add(hbox4, flag=wx.ALL | wx.EXPAND, border=5)

        ########## Add the bottom buttons

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        save = wx.Button(self, label='Save')
        cancel = wx.Button(self, label='Close')

        save.Bind(wx.EVT_BUTTON, self.OnSave, id=save.GetId())
        cancel.Bind(wx.EVT_BUTTON, self.OnCancel, id=cancel.GetId())

        ########## Position the buttons accordingly

        hbox.Add(save, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        hbox.Add(cancel, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        vbox.Add(hbox, flag=wx.ALL | wx.EXPAND, border=5)

        self.SetSizer(vbox)

    def ClearTextLines(self):
        """ Erase the contents of all text boxes """

        self.refTxtCtrl.Remove(0,self.refTxtCtrl.GetLineLength(0))
        self.xTxtCtrl.Remove(0,self.xTxtCtrl.GetLineLength(0))
        self.yTxtCtrl.Remove(0,self.yTxtCtrl.GetLineLength(0))
        self.aTxtCtrl.Remove(0,self.aTxtCtrl.GetLineLength(0))        

    def OnSave(self, event):
        """ Save entry for use outside the dialog """

        # Save contents of textCtrl
        try:
            self.reference = self.refTxtCtrl.GetLineText(0)
            self.off_x = float(self.xTxtCtrl.GetLineText(0))
            self.off_y = float(self.yTxtCtrl.GetLineText(0))
            self.angle = float(self.aTxtCtrl.GetLineText(0))
            
            print("Saving data...",self.reference, self.off_x, self.off_y, self.angle)
            self.Destroy()

        except ValueError as e:
            wx.MessageBox(str(e),e.__class__.__name__, wx.OK | wx.ICON_ERROR)
            self.ClearTextLines()
            
            # Write old values back to the text entry
            self.LoadEntryValues(self.entry)
            self.refTxtCtrl.write(self.reference)
            self.xTxtCtrl.write(self.off_x)
            self.yTxtCtrl.write(self.off_y)
            self.aTxtCtrl.write(self.angle)
           
    def OnCancel(self, event):
        """ Cancel text entry """

        self.Destroy()

class AppFunctions(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(AppFunctions, self).__init__(*args, **kwargs)

    def initPanel(self):

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.refTable = pcb.ReferenceTable()

        self.cur_index = 0
        self.cur_id = 0
        self.rowDict = {}

        self.InputFile = ""
        self.OutputDir = ""

    def displayHeading(self):
        """ Display main heading onto app """

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        title = '''KLE Placement Router'''

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading = wx.StaticText(self, label=title)
        heading.SetFont(font)
        self.vbox.Add(heading, flag=wx.ALL | wx.EXPAND, border=10)

        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        
        heading2 = wx.StaticText(
            self, 
            label="Position clusters of components by prefix, using XY coordinates from a KLE layout"
        )

        heading2.SetFont(font)
        #hbox.Add(heading2, flag=wx.ALL | wx.EXPAND, border=10)
        self.vbox.Add(heading2, flag=wx.ALL | wx.EXPAND, border=10)

        heading3 = wx.StaticText(
            self, 
            label="Make sure your footprint prefixes and numbers are seperated by an underscore '_'\n(For example: K_1, LED_37, C_34, etc.)"
        )

        heading3.SetFont(font)
        self.vbox.Add(heading3, flag=wx.LEFT | wx.EXPAND, border=10)

        line = wx.StaticLine(self)
        self.vbox.Add(line, flag=wx.ALL | wx.EXPAND, border=10)

    def chooseImportMethod(self):
        """ Choose how the KLE layout is imported to the program """

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Add heading
        line = wx.StaticText(self, label=" Import KLE file ")
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        line.SetFont(font)
        self.vbox.Add((-1, 10))
        self.vbox.Add(line, flag=wx.LEFT | wx.EXPAND, border=10)

        button = wx.Button(self, label='Browse..')
        button.Bind(wx.EVT_BUTTON, self.selectInputFile, id=button.GetId())
        hbox.Add(button, flag=wx.ALL | wx.EXPAND, border=10)

        self.inputFileTxt = wx.TextCtrl(self, 
            value = "Select KLE JSON file...",
            style = wx.TE_READONLY|wx.TE_LEFT
        )

        hbox.Add(self.inputFileTxt, proportion=1,flag=wx.ALL | wx.EXPAND, border=10)

        self.vbox.Add(hbox, flag=wx.LEFT | wx.EXPAND, border=10)

        # TODO: Add a text box option for adding raw data instead

        self.vbox.Add((-1, 10))

    def selectInputFile(self, e):
        """ Handler for importing the KLE file using a directory dialog """

        title = "Choose KLE file..."
        msg = wx.FileDialog(self,title, ".", "KLE Layout File (*.json)|*.json")

        if msg.ShowModal() == wx.ID_OK:
            self.InputFile = msg.GetPath()
            self.inputFileTxt.ChangeValue(self.InputFile)
        msg.Destroy()

    def selectOutputDirectory(self, e):
        """ Handler for choosing the output directory """

        title = "Select the output directory"
        msg = wx.DirDialog(self,title, ".")

        if msg.ShowModal() == wx.ID_OK:
            self.OutputDir = msg.GetPath()
            self.OutputDirTxt.ChangeValue(self.OutputDir)
        msg.Destroy()

    def trackFptReferences(self):
        """ Track footprint references to be placed """

        ########## Add additional headings
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        h1 = 'Add references below'
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading = wx.StaticText(self, label=h1)
        heading.SetFont(font)
        hbox.Add(heading, flag=wx.LEFT | wx.EXPAND, border=10)

        h2 = 'Add the prefixes with the underscore "_"'
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        heading = wx.StaticText(self, label=h2)
        heading.SetFont(font)
        hbox.Add(heading, flag=wx.LEFT | wx.EXPAND, border=10)

        ########## Render the box

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.list = wx.ListCtrl(
            self, 
            wx.ID_ANY, 
            style=wx.LC_REPORT | wx.LC_EDIT_LABELS | wx.LC_HRULES | wx.LC_VRULES
        )

        self.list.InsertColumn(0, 'Reference', width=100)
        self.list.InsertColumn(1, 'X Offset (mm)', width=100)
        self.list.InsertColumn(2, 'Y Offset (mm)', width=100)
        self.list.InsertColumn(3, 'Angle (deg)', width=100)
        self.list.InsertColumn(4, 'Number of Parts', width=125)

        hbox1.Add(self.list, 1)

        new = wx.Button(self, label='New')
        edit = wx.Button(self, label='Edit')
        delete = wx.Button(self, label='Delete')
        clear = wx.Button(self, label='Clear')

        new.Bind(wx.EVT_BUTTON, self.OnNew, id=new.GetId())
        edit.Bind(wx.EVT_BUTTON, self.OnEdit, id=edit.GetId())
        delete.Bind(wx.EVT_BUTTON, self.OnDelete, id=delete.GetId())
        clear.Bind(wx.EVT_BUTTON, self.OnClear, id=clear.GetId())
        
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.UpdateCursor)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.ResetCursor)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(new    , flag=wx.LEFT | wx.EXPAND, border=10)
        vbox.Add(edit    , flag=wx.LEFT | wx.EXPAND, border=10)
        vbox.Add(delete , flag=wx.LEFT | wx.EXPAND, border=10)
        vbox.Add(clear  , flag=wx.LEFT | wx.EXPAND, border=10)
        hbox1.Add(vbox   , flag=wx.LEFT | wx.EXPAND, border=10)

        self.vbox.Add(hbox, flag=wx.ALL | wx.EXPAND, border=10)
        self.vbox.Add(hbox1, flag=wx.ALL | wx.EXPAND, border=10)
        self.vbox.Add((-1, 10))

    def UpdateCursor(self, event):
        """ Updates the index of the currently selected object """

        print("Updating cursor position...")

        self.cur_index = event.GetIndex()
        self.cur_id = self.list.GetItemData(self.cur_index)

    def ResetCursor(self, event):
        """ Resets the cursor to the end of the list """

        print("Resetting cursor position...")

        self.cur_index = self.list.GetItemCount() - 1
        self.cur_id = self.list.GetItemData(self.cur_index)

    def RefreshRows(self):
        """ Refreshes the current list of values based on the reference table """

        print("Refreshing Table...")

        # Don't bother when the list is empty
        if (self.list.GetItemCount() <= 0) or (len(self.refTable.table) <= 0):
            print("List is empty...")
            return        

        # Clear the list
        if self.list.DeleteAllItems() != True:
            print("Error deleting items")

        # Repopulate the table
        index = 0
        numParts = 0
        for item in self.refTable.table.values():
            self.list.InsertItem(index, item.reference)
            self.list.SetItem(index, 1, str(item.off_x))
            self.list.SetItem(index, 2, str(item.off_y))
            self.list.SetItem(index, 3, str(item.angle))
            self.list.SetItemData(index, item.id)

            # Get the number of parts matching the reference
            numParts = pcb.GetNumOfPrefixedParts(item.reference)
            self.list.SetItem(index, 4, str(numParts))
            index += 1

    def OnNew(self, event):
        """ Add new reference to be tracked """

        print("Creating new reference...")

        # Create a new instance of Reference
        newRef = pcb.Reference()
        newRef.id = math.ceil(random.random()*sys.maxsize)
        newRef.reference = newRef.reference + str(self.list.GetItemCount()) + '_'

        # Add a new entry onto the end of the list
        index = self.list.GetItemCount()
        self.cur_id = newRef.id

        # Populate the entry with the default values
        self.refTable.table[newRef.id] = newRef
        self.list.InsertItem(index, str(newRef.reference))
        self.list.SetItem(index, 1, str(newRef.off_x))
        self.list.SetItem(index, 2, str(newRef.off_y))
        self.list.SetItem(index, 3, str(newRef.angle))
        self.list.SetItemData(index, self.cur_id)

        self.RefreshRows()

    def OnEdit(self, event):
        """ Handler for editing entries """

        # Don't bother when the list is empty
        if (self.list.GetItemCount() <= 0) or (len(self.refTable.table) <= 0):
            print("List is empty...")
            return   

        # Get the current instance of the chosen entry
        entry = self.refTable.table[self.list.GetItemData(self.cur_index)]

        # Forward the entry to the editing dialog
        editBox = EditDialog(self)
        editBox.LoadEntryValues(entry)
        editBox.InitUI()
        editBox.ShowModal()

        # Process output of the dialog back into the chosen entry
        print("Received: ",editBox.reference, editBox.off_x, editBox.off_y, editBox.angle)

        entry.reference = editBox.reference
        entry.off_x = editBox.off_x
        entry.off_y = editBox.off_y
        entry.angle = editBox.angle

        # Write the modified entry back to the reference table
        self.refTable.table[entry.id] = entry

        self.RefreshRows()

    def OnDelete(self, event):
        """ Handler for deleting references """

        # Don't bother when the list is empty
        if self.list.GetItemCount() <= 0:
            print("List is empty...")
            return

        print("Deleting selected reference...", self.cur_index)

        # Delete entry from reference table
        self.cur_id = self.list.GetItemData(self.cur_index)
        self.refTable.table.pop(self.cur_id)

        # Delete entry from ListCtrl
        self.list.DeleteItem(self.cur_index)

        # Don't bother when the list is empty afterwards
        listSize = self.list.GetItemCount()
        if (listSize <= 0) or (len(self.refTable.table) <= 0):
            self.cur_index = 0
            print("List is empty...")
            return

        # Set the cursor to the last entry of the list, for use with consecutive deletes
        self.cur_index = self.list.GetItemCount() - 1
        self.RefreshRows()

    def OnClear(self, event):
        """ Clear all references in the table """

        # Don't bother when the list is empty
        if self.list.GetItemCount() <= 0:
            print("List is empty...")
            return

        print("Deleting all references...")

        # Delete list items completely
        if self.list.DeleteAllItems() != True:
            print("Error deleting items")

        # Delete reference table entirely
        self.refTable.table.clear()

        # Reset index cursor to 0
        self.cur_index = 0

    def generateLayout(self):
        """ Generate the module placements for the PCB footprints """

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        ########## Render the elements

        heading = wx.StaticText(self, label="Output directory", size=(200, -1))

        self.OutputDirBtn = wx.Button(self, label='Browse...')
        self.OutputDirTxt = wx.TextCtrl(self, value='Select output directory',style=wx.TE_READONLY)
        self.generate = wx.Button(self, label='Generate Layout')

        self.OutputDirBtn.Bind(wx.EVT_BUTTON, self.selectOutputDirectory, id=self.OutputDirBtn.GetId())
        self.generate.Bind(wx.EVT_BUTTON, self.OnGenerate, id=self.generate.GetId())

        hbox.Add(self.OutputDirBtn, flag=wx.LEFT | wx.EXPAND, border=10)
        hbox.Add(self.OutputDirTxt, proportion=1,flag=wx.LEFT | wx.EXPAND, border=10)
        self.vbox.Add(heading,flag=wx.ALL | wx.EXPAND, border=10)
        self.vbox.Add(hbox,flag=wx.ALL | wx.EXPAND, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.generate,proportion=1,flag=wx.LEFT | wx.EXPAND, border=10)
        self.vbox.Add(hbox2,flag=wx.ALL | wx.EXPAND, border=10)

        self.vbox.Add((-1, 10))

    def OnGenerate(self, event):
        """ Generates the PCB placement """

        print("Generating footprint placements...")
        # print(self.InputFile, self.OutputDir, self.refTable.table)

        # Generate the footprint placements and save to new file
        with open(self.InputFile, 'r') as fp:
            layout = json.load(fp)
            keeb = key.Keyboard()

            # Get coordinate maps for the components
            keeb.parseLayout(layout)
            # keeb.exportCoordinateMap(self.OutputDir)
            pcb.placeComponents(keeb.getCoordinateMap(), self.refTable.table, self.OutputDir)

    def finalizeWidgets(self):
        self.SetSizer(self.vbox)

class App(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.InitUI()
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.cursor= wx.Cursor(wx.CURSOR_ARROW)
        self.panel.SetCursor(self.cursor)

    def InitUI(self):

        panel = AppFunctions(self)
        panel.initPanel()
        panel.displayHeading()
        panel.chooseImportMethod()
        panel.trackFptReferences()
        panel.generateLayout()        
        panel.finalizeWidgets()

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.SetSize((APP_WIDTH, APP_HEIGHT))
        self.SetTitle('KLE Placement Router')
        self.Centre()

    def OnCloseWindow(self, e):

        dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Question',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
            return
        else:
            e.Veto()

def main():

    app = wx.App()
    ex = App(None)
    ex.Show()
    status = app.MainLoop()

if __name__ == '__main__':
    main()
