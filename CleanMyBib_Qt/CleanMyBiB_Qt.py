#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import platform
import re
import csv
from PyQt4 import QtGui
from PyQt4 import QtCore

__version__ = "1.0.0"


# Allow to read the picture file in pyinstaller
datadir = ".img"
if not hasattr(sys, "frozen"):   # not packed
    datadir = os.path.join(os.path.dirname(__file__), datadir)
elif "_MEIPASS2" in os.environ:   # one-file temp's directory
    datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
else:   # one-dir
    datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)



class CleanFileBib():
    def __init__(self, fileBib, file_BibOk, to_sup, style=1):
        """ A function to go line by line and clean the correct lines"""
        self.BibOK = file_BibOk
        self.style = style
        debut = re.compile('^\s*(\w+)\s*(=)\D*') # Search for space - word - space - '='
        txt = fileBib.readline() # Read the first line of the bib file
        linePage = self.FindLine('pages') # Define the search pattern for pages
        lineJournal= self.FindLine('journal') # Id. for journal
        journals = self.Read_CSV('.img/Journals.csv', 0, 1)
        while txt: # Loop to read the file
            if debut.search(txt) and debut.search(txt).group(1).lower() in to_sup:
                if txt[-3:-1] == '}}': # Avoid the line specified
                    self.BibOK.write('}\n') # Avoid to delete the last }
                else:
                    pass
            elif linePage.search(txt): # For the pages
                pages = self.ChangePageNber(txt, self.style)
                if txt[-3:-1] == '}}':
                    self.BibOK.write(pages + '}\n')
                else:
                    self.BibOK.write(pages)
            elif lineJournal.search(txt): # For the journals
                journal = self.Journal_Format(txt, lineJournal, journals, self.style)
                journal = self.Journal_Name(journal)
                if txt[-3:-1] == '}}':
                    self.BibOK.write(journal + '}},\n')
                else:
                    self.BibOK.write(journal + '},\n')
            else:
                self.BibOK.write(txt)
            txt=fileBib.readline() # Read the next line of the bib file
            
            
    def Read_CSV(self, file_name, col1=1, col2=2):
        """ A function to read a csv file into a dictionary
            Take the file name 'ex.csv' and the columns to read
            Give the dictionary as output
        """
        cur_dir = sys.path[0]
        CSV_file = open(file_name, "rb")
        dico = {}
        try:
            reader = csv.reader(CSV_file, delimiter=',')
            for row in reader:
                dico[row[col1].lower()] = row[col2].lower()
        finally:
            CSV_file.close()
        return dico
    
    
    def Journal_Format(self, txt, journal_re, journals, style=1):
        """ Change name according to..."""
        # Style -> APA= 1; Vancouver= 2
        journal_name = journal_re.search(txt).groups()
        journal_name = journal_name[2].lower()
        if style == 1:
            if journal_name in journals.values():
                dico_inv   = dict([(v, k) for (k, v) in journals.iteritems()]) # Reverse the dictionary to replace the long name by the short one
                journal_ok = dico_inv[journal_name]
            else:
                journal_ok = journal_name
        elif style == 2:
            if journal_name in journals.keys():
                journal_ok = journals[journal_name]
            else:
                journal_ok = journal_name
            journal_ok = [word+"." for word in journal_ok.split()]
            journal_ok = " ".join(journal_ok)
        else:
            journal_ok = journal_name
        return journal_ok
    
    
    def FindLine(self, line_to_find):
        """ A function to find the correct line in the bib file
            Take the key word to search (e.g. 'journal')
              and compile a regular expression regardless of the case
              and regardless of the possible spaces
        """
        # Regular expression: space [word to find] space = space { content }
        pattern = re.compile(r'\s*(%s)\s*(=)\s*{\s*(\D*S*|\d*\W*\d*)\s*}'\
                             %line_to_find, re.IGNORECASE)
        return pattern
    
    
    def Journal_Name(self, journal_name):
        """ A function to add a capital letter of each words of the journal name
            Expect for the liaison words
        """
        # List of the words or strings to not capitalize
        to_pass = ['et', 'le', 'la', 'de', 'du', 'l', 'a', 'an', 'in', 'to', 'of',\
                   'for', 'the', 'and', '-', '--', ':', '?']
        words = journal_name.split() # Split the journal's name (single word)
        words_ok = [] # Initiate an empty list
        words_ok.append( words[0].capitalize() ) # Always capitalize the first word
        for curWord in words[1:]:
            if curWord in to_pass:          # Capitalize the good words
                words_ok.append( curWord )  # Avoid the liaison words
            else:
                words_ok.append( curWord.capitalize() )
        journal_name_ok = "journal = {"     # Prepare the final name
        for i in words_ok:
            if i == words_ok[len(words_ok)-1]: # Construct the final name
                journal_name_ok += i        # Avoid to add a 'space' at the end
            else:
                journal_name_ok += i+" "
        return journal_name_ok


    def PagesNberAPA(self, t1, t2):
        """ A function to add the missing numbers
              in order to have the same length as in the APA format.
            First page is t1, last page is t2
            E.g.: 1128--35 transform to 1128--1135
        """
        while len(t1) > len(t2): # Check if a correction should be applied
            t2= t1[-(1+len(t2))]+t2 # Add the missing numbers
        return t2


    def PagesNberMed(self, t1, t2):
        """ A function to delete the page numbers that are identical.
            First page is t1, last page is t2
            E.g.: 1128--1135 transformed to 1128--35
        """
        x, done= 0, 0 # Initialise les variables controles
        if len(t1) >= len(t2): # Verifie que les pages ne soient pas deja coupees
            while done<1:
                if t1[x] == t2[x]: # Loop pour definir combien de chiffres sont identiques
                    x+=1 # Incremente la variable de controle x
                else:
                    done=1 # Quite la boucle des que les deux nombres sont differents
            t2=t2[x:] # Ajuste la nouvelle valeur pour la derniere page
        return t2


    def ChangePageNber(self, txt, style=1):
        """ A function to apply the correct change page number,
              either regarding the APA or Vancouver guidelines.
            Find the groups of pages and send them to the APA/Vancouv function.
        """
        pagePattern= re.compile(r'\D*(\d+)\D*(\d*)\D*$') # Space numbers other numbers other
        if pagePattern.search(txt) != None:
            pages= pagePattern.search(txt).groups() # Find the groups of numbers
            p1= pages[0] # Define p1 and p2
            p2= pages[1] # p1= first page; p2= last page
            if len(p2)>0: # Check if a number for t2 exists
                if style == 1:
                    t2 = self.PagesNberAPA(p1, p2) # t2 is the new value of p2
                elif style == 2:
                    t2 = self.PagesNberMed(p1, p2)
            else: # If no number for t2, then print XXXX
                t2 = 'XXXX'
        else:
            p1 = 'XXXX'
            t2 = p1
        total = 'pages = {' + p1 + '--' + t2 + '},\n' # Construct the final pages line
        return total



# --------------------------------------------------------------
# GUI AND MAIN PROGRAM
# -------------------------------------------------------------- 
class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.chx = ['url', 'month', 'number'] # Line to suppress
        self.mainWidget=QtGui.QWidget(self)   # Widget to contain the layout manager
        self.setCentralWidget(self.mainWidget)
        self.grid = QtGui.QGridLayout(self.mainWidget) # Define a grid to display
        self.setLayout(self.grid)                      #  the widgets 
        
        self.status = self.statusBar()
        self.status.showMessage("Ready", 5000)

        # Call the menu/status bar and the partS of the GUI                
        self.menu()
        self.style_block()
        self.bibFile()
        self.statusBib()

        # Define the main window size and name
        #self.setGeometry(300, 300, 350, 150)
        self.setWindowTitle('Clean My Bib')    
        self.show()
       
       
    def menu(self):    
        # Define the action in the Menu and Toolbar
        options = QtGui.QAction(QtGui.QIcon('opt.jpeg'), 'Options', self)
        options.setShortcut('Ctrl+O')
        options.setStatusTip('Change the fields to ignore')
        options.triggered.connect(self.Opt)

		exitAction = QtGui.QAction(QtGui.QIcon('exit2.jpeg'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        
        aboutAction = QtGui.QAction(QtGui.QIcon('about.jpeg'), 'About', self)
        aboutAction.setStatusTip('About Clean My Bib')
        aboutAction.triggered.connect(self.about)

        # Fill the Menu
        menubar  = self.menuBar()
        mainMenu = menubar.addMenu('&Menu')
		mainMenu.addAction(options)
        mainMenu.addAction(aboutAction)
        mainMenu.addAction(exitAction)

        #toolbar = self.addToolBar('Exit')
        #toolbar.addAction(exitAction)
        
        
    def style_block(self):
        """ 
            Define the section of the GUI dedicated to the format
            User can choose between the 'APA' and 'Vancouver' style
            The format is defined under the choice as well as an example
        """   
        # Create a ComboBox to select the style to apply
        self.styleCx = 1
        cx_style = QtGui.QComboBox(self)
        list_style = [" APA like", "Vancouver"]
        cx_style.addItems(list_style)  
        cx_style.SizeAdjustPolicy(1)

        # Prepare the texts to display as format rule and examples
        format_APA   = "Journal format= long<BR>"+ \
                         "Page number= long"	
        ex_APA  = "'Experimental Psychology'<BR>"+"'1325-1333'"
        format_Vanc  = "&nbsp; Journal format= short<BR>"+ \
                         "&nbsp; Page number= short"	
        ex_Vanc = "&nbsp; &nbsp; &nbsp; 'Exp. Psychol.'&nbsp; &nbsp;<BR>"\
                    +"&nbsp; &nbsp; &nbsp; &nbsp; '1325-33' &nbsp; &nbsp;"
        # Regroup the texts into lists
        self.formatBib  = [format_APA, format_Vanc]
        self.exampleBib = [ex_APA, ex_Vanc]
        
        # Define some Labels to display information to the user
        logo1 = QtGui.QLabel(self)
        icon1 = QtGui.QPixmap(datadir+"/nb1.png")
        logo1.setPixmap(icon1)
        first_step  = QtGui.QLabel("<b><font color ='darkblue'><h2>&nbsp; \
                                        &nbsp; &nbsp; &nbsp; Define a style</b></h2>")
        lab_style   = QtGui.QLabel("<b>Style</b>", self)
        lab_format  = QtGui.QLabel("<b>Format</b>", self)
        lab_example = QtGui.QLabel("<b>Example</b>", self)
        self.lab_empty = QtGui.QLabel("", self)
        self.lab_empty.setMinimumSize(90, 25)

        self.lab_format_style = QtGui.QLabel(self.formatBib[0], self)
        self.lab_ex_style = QtGui.QLabel(self.exampleBib[0], self)

        # Place the widgets on the grid. 
        self.grid.addWidget(logo1, 0, 1, 1, 2)      
        self.grid.addWidget(first_step, 0, 1, 1, 2)
        self.grid.addWidget(lab_style, 2, 1)
        self.grid.addWidget(cx_style, 2, 2)
        self.grid.addWidget(lab_format, 3, 1)
        self.grid.addWidget(lab_example, 4, 1)        
        self.grid.addWidget(self.lab_format_style, 3, 2)
        self.grid.addWidget(self.lab_ex_style, 4, 2)

        cx_style.activated[int].connect(self.styleChoose)  
                
          
    def styleChoose(self, style):
        """
            Display the format rule and an example
              according to the selection of the user
        """
        if style == 0:
            self.lab_format_style.setText(self.formatBib[0])
            self.lab_ex_style.setText(self.exampleBib[0])
            self.styleCx = 1
            self.statusClean = QtGui.QLabel("<i>&nbsp;<BR>Ready to receive <BR>a bibtex file</i>")
            self.waitLogo.setPixmap(self.icon4)
        elif style == 1:
            self.lab_format_style.setText(self.formatBib[1])
            self.lab_ex_style.setText(self.exampleBib[1])
            self.styleCx = 2
            self.statusClean = QtGui.QLabel("<i>&nbsp;<BR>Ready to receive <BR>a bibtex file</i>")
            self.waitLogo.setPixmap(self.icon4)
        else:
            pass
    

    def bibFile(self):
        """
            GUI section to receive a droped file
            And take it as the bib file to clean 
        """
        self.setAcceptDrops(True)
           
        # Define a picture where to drop the file
        self.dropIcon = QtGui.QLabel(self)
        dragdrop = QtGui.QPixmap(datadir+"/drop.png")
        self.dropIcon.setPixmap(dragdrop)    
        self.dropIcon.setAlignment(QtCore.Qt.AlignCenter)
        
        # Define some Labels to display information to the user
        logo2 = QtGui.QLabel(self)
        icon2 = QtGui.QPixmap(datadir+"/nb2.png")
        logo2.setPixmap(icon2)
        
        second_step = QtGui.QLabel("<b><font color ='darkblue'><h2>&nbsp; \
                                        &nbsp; &nbsp; &nbsp; Bibtex file</b></h2>")        
                
        
        lab_drop  = QtGui.QLabel("<b><h3>Drop a bib file here</b></h3>", self)
        lab_drop.setAlignment(QtCore.Qt.AlignCenter)
        
        # Place the widgets on the grid
        self.grid.addWidget(self.lab_empty, 2, 3, 1, 5)        # Add an empty column
        self.grid.addWidget(self.lab_empty, 2, 4, 1, 5)        # Add an empty column

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
        for url in event.mimeData().urls():
            path = url.toLocalFile().toLocal8Bit().data()
            if os.path.isfile(path):
                try:
                    fileBib    = open(path, 'r')
                except IOError:
                    QtGui.QMessageBox.warning(self, "Warning",
"Failed to open\n%s" % "\n".join(path))
                rep, name  = os.path.split(path)
                name_bibOk = 'Clean-'+name
                self.status.showMessage("File to clean: "+name, 5000)
                BibOK      = os.path.join(rep, name_bibOk)
                fileBibOK  = open(BibOK, 'w')
                try:
                    CleanFileBib(fileBib, fileBibOK, self.chx, self.styleCx)
                    self.statusClean.setText("File cleaned succefully!")
                    icon4 = QtGui.QPixmap(datadir+"/success.png")
                    self.waitLogo.setPixmap(icon4)
                    self.status.showMessage("Drop another file", 5000)
                except:
                    self.statusClean.setText("An error has occured.\
                        \nPlease check your bibtex file")
                    icon5 = QtGui.QPixmap(datadir+"/error.png")
                    self.waitLogo.setPixmap(icon5)

                fileBib.close()
                fileBibOK.close()


    def statusBib(self):
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

        self.grid.addWidget(logo3, 0, 12, 1, 2)      
        self.grid.addWidget(third_step, 0, 12, 1, 2)
        self.grid.addWidget(self.statusClean, 1, 12, 2, 3)
        self.grid.addWidget(self.waitLogo, 3, 12, 1, 2)
        
    def about(self):
        QtGui.QMessageBox.about(self, "About Clean My Bib",
        """<b>Clean My Bib</b> v %s
        <p><b>Licence:</b> GPLv3 by GT Vallet
        <p>This application can be used to prepare a bibtex 
        file according to the APA like or Vancouver like guidlines.
        <p>Python %s - on %s""" % (
            __version__, platform.python_version(), platform.system()))
        

   	def Opt(self):
        opt = QtGui.QDialog(self)
        opt.setWindowTitle('Options -- Fields to delete') 
        self.listOpt = QtGui.QListWidget(opt)
        for item in self.chx:
                self.listOpt.addItem(item)

        AddBt = QtGui.QPushButton('Add', opt)
        RemBt = QtGui.QPushButton('Remove', opt)
        QtBt  = QtGui.QPushButton('Quit', opt)
        Cl_Bt = QtGui.QPushButton('Cancel', opt)

        RemBt.clicked.connect(self.RemoveField)
        AddBt.clicked.connect(self.Add)
        Cl_Bt.clicked.connect(opt.close)
        QtBt.clicked.connect(opt.close)
        QtBt.clicked.connect(self.UpList)   

        grid_opt = QtGui.QGridLayout()
        grid_opt.addWidget(self.listOpt, 0, 0, 5, 3)
        grid_opt.addWidget(AddBt, 0, 3)
        grid_opt.addWidget(RemBt, 1, 3)
        grid_opt.addWidget(QtBt, 5, 3)
        grid_opt.addWidget(Cl_Bt, 5, 2)

        opt.setLayout(grid_opt)
        opt.show()


    def Add(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Add a field:')

        if ok:
            self.listOpt.addItem(str(text))
            self.listOpt.sortItems(order = QtCore.Qt.AscendingOrder)

    def RemoveField(self):
            index = self.listOpt.currentRow()
            self.listOpt.takeItem(index)
            self.listOpt.sortItems(order = QtCore.Qt.AscendingOrder)

    def UpList(self):
        self_chx = []
        for index in xrange(self.listOpt.count()):
            self.chx.append(str(self.listOpt.item(index).text()))


def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    
