#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import platform
import re
import csv
from PyQt4 import QtGui
from PyQt4 import QtCore
from CleanMyBib import CleanFileBib
from pybtex.database.input import bibtex

__version__ = "4.0.0"


# Allow to read the picture files in pyinstaller
datadir = ".img"
if not hasattr(sys, "frozen"):   # not packed
    datadir = os.path.join(os.path.dirname(__file__), datadir)
elif "_MEIPASS2" in os.environ:   # one-file temp's directory
    datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
else:   # one-dir
    datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)


# --------------------------------------------------------------
# GRAPHICAL INTERFACE FOR CLEAN MY BIB
# --------------------------------------------------------------
class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        """ Define the main widgets and options
        """
        super(MainWindow, self).__init__()
        # Default fields to keep in the cleaned file
        self.chx = ['abstract','author','year','title','booktitle', 'journal',\
                            'pages', 'volume', 'editor','publisher','address']
        # Create the main frame to handle the widgets
        self.mainWidget=QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.grid = QtGui.QGridLayout(self.mainWidget) # Define a grid
        self.setLayout(self.grid)
        # Create a status bar
        self.status = self.statusBar()
        self.status.showMessage("Ready", 5000)
        # Call the menu, options and status bar
        self.menu()
        self.style_block()
        self.bibFile()
        self.statusBib()
        # Define the main window size and name
        self.setWindowTitle('Clean My Bib')
        self.show()


    def menu(self):
        """ Define the action in the Menu and Toolbar
        """
        # Options
        options = QtGui.QAction(QtGui.QIcon('opt.jpeg'), 'Options', self)
        options.setShortcut('Ctrl+O')
        options.setStatusTip('Change the fields to ignore')
        options.triggered.connect(self.Opts)
        # Exit
        exitAction = QtGui.QAction(QtGui.QIcon('exit2.jpeg'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        # About
        aboutAction = QtGui.QAction(QtGui.QIcon('about.jpeg'), 'About', self)
        aboutAction.setStatusTip('About Clean My Bib')
        aboutAction.triggered.connect(self.about)
        # Fill the Menu
        menubar  = self.menuBar()
        mainMenu = menubar.addMenu('&Menu')
        mainMenu.addAction(options)
        mainMenu.addAction(aboutAction)
        mainMenu.addAction(exitAction)


    def style_block(self):
        """ Define the section of the GUI dedicated to the style format
            User can choose between the 'Long' and 'Short' style for the journal
              name and the page numbers.
            An option is provided to add or not the DOIs
        """
        # Create a ComboBox to select the journal name's style
        cx_journal_style = QtGui.QComboBox(self)
        list_style = [" Long format", "Short format"]
        cx_journal_style.addItems(list_style)
        cx_journal_style.SizeAdjustPolicy(1)
        # Create a ComboBox to select the page numbers' style
        cx_pages_style = QtGui.QComboBox(self)
        cx_pages_style.addItems(list_style)
        cx_pages_style.SizeAdjustPolicy(1)
        # Create a checkbox for the DOIs
        self.add_doi = QtGui.QCheckBox("Add DOIs")
        # Define some Logo and Labels to display information to the user
        logo1 = QtGui.QLabel(self)
        icon1 = QtGui.QPixmap(datadir+"/nb1.png")
        logo1.setPixmap(icon1)
        first_step  = QtGui.QLabel("<b><font color ='darkblue'><h2>&nbsp; \
                                  &nbsp; &nbsp; &nbsp; Define a style</b></h2>")
        lab_style   = QtGui.QLabel("<b>Journal</b>", self)
        lab_format  = QtGui.QLabel("<b>Pages</b>", self)
        lab_example = QtGui.QLabel("<b>DOI</b>", self)
        self.lab_empty = QtGui.QLabel("", self)
        self.lab_empty.setMinimumSize(90, 25)
        # Place the widgets on the grid.
        self.grid.addWidget(logo1, 0, 1, 1, 2)
        self.grid.addWidget(first_step, 0, 1, 1, 2)
        self.grid.addWidget(lab_style, 2, 1)
        self.grid.addWidget(cx_journal_style, 2, 2)
        self.grid.addWidget(lab_format, 3, 1)
        self.grid.addWidget(lab_example, 4, 1)
        self.grid.addWidget(cx_pages_style, 3, 2)
        self.grid.addWidget(self.add_doi, 4, 2)
        # Control the style and the choice done
        self.journal_style = "long"
        self.pages_style = "long"
        cx_journal_style.activated[int].connect(self.styleJournal)
        cx_pages_style.activated[int].connect(self.stylePages)
        self.mainWidget.connect(self.add_doi,
                                QtCore.SIGNAL('stateChanged(int)'), self.doi)


    def doi(self):
        """ Add and remove the doi fields in the list of fields to keep
        """
        if self.add_doi.isChecked():
            self.chx.append("doi")
        else:
            if "doi" in self.chx:
                self.chx.remove("doi")


    def styleJournal(self, style):
        if style == 0:
            self.journal_style = "long"
        else:
            self.journal_style = "short"


    def stylePages(self, style):
        if style == 0:
            self.pages_style = "long"
        else:
            self.pages_style = "short"


    def bibFile(self):
        """ GUI section to receive a dropped file
            And take it as the bib file to clean
        """
        self.setAcceptDrops(True)
        # Define a picture where to drop the file
        self.dropIcon = QtGui.QLabel(self)
        dragdrop = QtGui.QPixmap(datadir+"/drop.png")
        self.dropIcon.setPixmap(dragdrop)
        self.dropIcon.setAlignment(QtCore.Qt.AlignCenter)
        # Define some Logo and Labels to display information to the user
        logo2 = QtGui.QLabel(self)
        icon2 = QtGui.QPixmap(datadir+"/nb2.png")
        logo2.setPixmap(icon2)
        second_step = QtGui.QLabel("<b><font color ='darkblue'><h2>&nbsp; \
                                        &nbsp; &nbsp; &nbsp; Bibtex file</b></h2>")
        lab_drop  = QtGui.QLabel("<b><h3>Drop a bib file here</b></h3>", self)
        lab_drop.setAlignment(QtCore.Qt.AlignCenter)
        # Place the widgets on the grid
        self.grid.addWidget(self.lab_empty, 2, 3, 1, 5)  # Add an empty column
        self.grid.addWidget(self.lab_empty, 2, 4, 1, 5)  # Add an empty column
        self.grid.addWidget(logo2, 0, 6, 1, 2)
        self.grid.addWidget(second_step, 0, 6, 1, 2)
        self.grid.addWidget(self.dropIcon, 2, 6, 2, 3)
        self.grid.addWidget(lab_drop, 4, 6, 1, 3)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event):
        """ Extract the path of the dropped file
            Call the CleanMyBib script and update the status bar
        """
        for url in event.mimeData().urls():
            path = url.toLocalFile().toLocal8Bit().data()
            if os.path.isfile(path):
                # Extract the path and open the cleaned file
                rep, name  = os.path.split(path)
                name_bibOk = 'Cleaned_'+name
                fileBibOK  = open(os.path.join(rep, name_bibOk), 'w')
                # Update the status bar
                self.status.showMessage("File to clean: "+name, 5000)
                # Prepare the fields to keep in the final file
                fields = []
                for item in self.chx:
                    fields.append(item.lower())
                try:
                    CleanFileBib(path, fileBibOK, fields, self.journal_style, self.pages_style)
                    self.statusClean.setText("File cleaned successfully!")
                    icon4 = QtGui.QPixmap(datadir+"/success.png")
                    self.waitLogo.setPixmap(icon4)
                    self.status.showMessage("Drop another file", 5000)
                except:
                    self.statusClean.setText("An error has occurred.\
                        \nPlease check your bibtex file\nand the log file")
                    icon5 = QtGui.QPixmap(datadir+"/error.png")
                    self.waitLogo.setPixmap(icon5)
                fileBibOK.close()


    def statusBib(self):
        """ The third panel of the main frame is used to display the current
              status of the file to be cleaned
        """
        logo3 = QtGui.QLabel(self)
        icon3 = QtGui.QPixmap(datadir+"/nb3.png")
        logo3.setPixmap(icon3)
        third_step = QtGui.QLabel("<b><font color ='darkblue'><h2>&nbsp; &nbsp; \
                                     &nbsp; &nbsp; Clean my bib...</b></h2>")
        self.statusClean = QtGui.QLabel("<i>&nbsp;<BR>Ready to receive <BR>a bibtex file</i>")
        self.statusClean.setAlignment(QtCore.Qt.AlignCenter)
        self.waitLogo    = QtGui.QLabel(self)
        self.icon4 = QtGui.QPixmap(datadir+"/wait.png")
        self.waitLogo.setPixmap(self.icon4)
        self.waitLogo.setAlignment(QtCore.Qt.AlignCenter)
        # Display the widgets on the grid
        self.grid.addWidget(logo3, 0, 12, 1, 2)
        self.grid.addWidget(third_step, 0, 12, 1, 2)
        self.grid.addWidget(self.statusClean, 1, 12, 2, 3)
        self.grid.addWidget(self.waitLogo, 3, 12, 1, 2)


    def about(self):
        QtGui.QMessageBox.about(self, "About Clean My Bib",
        """<b>Clean My Bib</b> v %s
        <p><b>Licence:</b> GPLv3 by GT Vallet
        <p>This application can be used to prepare a bibtex
        file to prepare the journal name and page numbers format into short or
        long forms.
        <p>Python %s - on %s""" % (
            __version__, platform.python_version(), platform.system()))


    def Opts(self):
        """ Option panel to add/remove key words defining the fields
             to add in the cleaned bibtex file
        """
        opt = QtGui.QDialog(self)
        opt.setWindowTitle('Options -- Fields to keep')
        self.listOpt = QtGui.QListWidget(opt)
        for item in sorted(self.chx):
                self.listOpt.addItem(item.capitalize())
        # Define the buttons
        AddBt = QtGui.QPushButton('Add', opt)
        RemBt = QtGui.QPushButton('Remove', opt)
        QtBt  = QtGui.QPushButton('Quit', opt)
        Cl_Bt = QtGui.QPushButton('Cancel', opt)
        # Define the action associated to the buttons
        RemBt.clicked.connect(self.RemoveField)
        AddBt.clicked.connect(self.Add)
        Cl_Bt.clicked.connect(opt.close)
        QtBt.clicked.connect(opt.close)
        QtBt.clicked.connect(self.UpList)
        # Place the widgets on the grid
        grid_opt = QtGui.QGridLayout()
        grid_opt.addWidget(self.listOpt, 0, 0, 5, 3)
        grid_opt.addWidget(AddBt, 0, 3)
        grid_opt.addWidget(RemBt, 1, 3)
        grid_opt.addWidget(QtBt, 5, 3)
        grid_opt.addWidget(Cl_Bt, 5, 2)
        # Show the option window
        opt.setLayout(grid_opt)
        opt.show()


    def Add(self):
        """ Add a new field to the list
        """
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
            'Add a field:')

        if ok:
            self.listOpt.addItem(str(text))
            self.listOpt.sortItems(order = QtCore.Qt.AscendingOrder)


    def RemoveField(self):
        """ Remove a field for the list
        """
        index = self.listOpt.currentRow()
        self.listOpt.takeItem(index)
        self.listOpt.sortItems(order = QtCore.Qt.AscendingOrder)


    def UpList(self):
        """ Finally update the list of field to send back to the program
        """
        self.chx = []
        for index in xrange(self.listOpt.count()):
            self.chx.append(str(self.listOpt.item(index).text()))



# --------------------------------------------------------------
# START THE APPLICATION
# --------------------------------------------------------------
def main():
    """Define the main application
       Calling the UI
    """
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
