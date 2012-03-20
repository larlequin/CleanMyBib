#!/usr/bin/env python
# -*- coding: Utf-8 -*-
#
# A script (Tk GUI) to prepare a bibfile according to the APA/Vancoucer guidelines
#  The script remove the URL, the number and the month
#  Capitalize the journal's name (except for conjonctions)
#  Add missing page numbers
#
# Take a bibfile as input and create a Clean_filename as output
#
# GTV - v01  	- 07/11/2011
# GTV - v01.1 	- 11/02/2012 - Add a feedback of the processing of the file

###################
###    TO DO    ###
###################
# FIXME
# Re format all the file (no space...)
# Add options
# Add a log to record the name of journal not in the list
# Correct the upper / lower with the list
# Check for python 3

import os,sys   # Load library for the system and the current OS
import re       # Load library for the regular expressions
import csv      # Load library to work with csv file

# Adaptation of the code to deal with Python 2 and 3
try:
    import tkinter as Tkinter                   # Load library for graphical interface
    import tkinter.filedialog as tkFileDialog   # Load library for user dialog box
    import tkinter.constants as Tkconstants     # Load library to define some constants
except ImportError:
    import Tkinter		                        # Same library, but in Python 2.x
    import tkFileDialog
    import Tkconstants



#################################################################
#################################################################
#####                                                       #####
#####                    FUNCTIONS                          #####
#####                                                       #####
#################################################################
def Read_CSV(file_name, col1=1, col2=2):
    """ A function to read a csv file into a dictionary 
        Take the file name 'ex.csv' and the columns to read
        Give the dictionary as output
    """
    CSV_file = open(file_name, "rb")
    dico = {}                # Initiate the dictionnary
    reader = csv.reader(CSV_file, delimiter=',')  # Read the file
    for row in reader:
        dico[row[col1].lower()] = row[col2].lower()
    CSV_file.close()     # Close the file
    return dico


def Journal_Format(txt, journal_re, journals, log, style=1):
    """ Change name according to of the Journal 
	    Either as a long format (APA like)
     	Either as a short format (Vancouver like)
    	Take the journal information, the pattern of research,
          the dictionnary of names and the style to apply (1=APA)
    """
    # Style -> APA= 1; Vancouver= 2
    journal_name = journal_re.search(txt).groups()
    journal_name = journal_name[2].lower() 
    if style == 1:    # APA style
        if journal_name in journals.values():
            dico_inv = dict([(v, k) for (k, v) in journals.iteritems()])   # Reverse the dictionary to replace the long name by the short one 
            journal_ok = dico_inv[journal_name]
        elif journal_name in journals.keys():            
            journal_ok = journal_name
        else:
            log.write(journal_name+'\n')
            journal_ok = journal_name
    elif style == 2:
		if journal_name in journals.keys():
			journal_ok = journals[journal_name]
		elif journal_name in journals.values():
			journal_ok = journal_name
		else:
			log.write(journal_name+'\n')
			journal_ok = journal_name
    return journal_ok


def FindLine(line_to_find):
    """ A function to find the correct line in the bib file
        Take the key word to search (e.g. 'journal') 
        Compile a regular expression regardless of the case 
          and regardless of the possible spaces
    """
    # Regular expression: space [word to find] space = space { content }
    pattern = re.compile(r'\s*(%s)\s*(=)\s*{\s*(\D*S*|\d*\W*\d*)\s*}'\
                         %line_to_find, re.IGNORECASE)
    return pattern


def Journal_Name(journal_name):
    """ A function to add a capital letter of each words of the journal name
        Expect for the liaison words
    """
    # List of the words or strings to not capitalize
    to_pass = ['et', 'le', 'la', 'de', 'du', 'l', 'a', 'an', 'in', 'to', 'of',\
               'for', 'the', 'and', '-', '--', ':', '?']
    words 	 =  journal_name.split()                # Split the journal's name (single word)
    words_ok     =  []                                  # Initiate an empty list
    words_ok.append(words[0].capitalize())              # Always capitalize the first word
    for cur_word in words[1:]:  
        if cur_word in to_pass:                         # Capitalize the good words
            words_ok.append(cur_word)                   #  avoid the liaison words
        else:
            words_ok.append(cur_word.capitalize())
    journal_name_ok = "journal = {"                     # Prepare the final name
    for i in words_ok:
        if i == words_ok[len(words_ok)-1]:              # Construct the final name           
            journal_name_ok += i                        # Avoid to add a 'space' at the end
        else:
            journal_name_ok += i+" "
    return journal_name_ok


def PagesNberAPA(t1, t2):
    """ A function to add the missing numbers 
          in order to have the same length as in the APA format.
        First page is t1, last page is t2
        E.g.: 1128--35 transform to 1128--1135
    """
    while len(t1) > len(t2):    # Check if a correction should be applied
        t2= t1[-(1+len(t2))]+t2	# Add the missing numbers
    return t2	


def PagesNberMed(t1, t2):
    """ A function to delete the page numbers that are identical.
        First page is t1, last page is t2 
        E.g.: 1128--1135 transformed to 1128--35
        """
    x, done= 0, 0  		        # Initialise les variables contrôles
    if len(t1) >= len(t2):		# Vérifie que les pages ne soient pas déjà coupées
        while done<1:
            if t1[x] == t2[x]:  # Loop pour définir combien de chiffres sont identiques
                x+=1	        # Incrémente la variable de contrôle x
            else:
                done=1	        # Quite la boucle dès que les deux nombres sont différents
        t2=t2[x:]	        # Ajuste la nouvelle valeur pour la dernière page
    return t2


def ChangePageNber(txt, style=1):
    """ A function to apply the correct change page number,
          either regarding the APA or Vancouver guidelines.
        Find the groups of pages and send them to the APA/Vancouv function.
    """
    pagePattern= re.compile(r'\D*(\d+)\D*(\d*)\D*$')    # Space numbers other numbers other
    if pagePattern.search(txt) != None:
        pages= pagePattern.search(txt).groups()         # Find the groups of numbers
        p1= pages[0] 		    # Define p1 and p2 
        p2= pages[1]                # p1= first page; p2= last page
        if len(p2)>0:		    # Check if a number for t2 exists
            if style == 1:
                t2 = PagesNberAPA(p1, p2)    # t2 is the new value of p2
            elif style == 2:
                t2 = PagesNberMed(p1, p2)
        else:				     # If no number for t2, then print XXXX
            t2 = 'XXXX'
    else:
        p1 = 'XXXX'
        t2 = p1
    total = 'pages = {' + p1 + '--' + t2 + '},\n'       # Construct the final pages line	
    return total

    
def Clean_FileBib(fileBib, file_BibOK, style=1):
    """ A function to go line by line and clean the correct lines 
       
    """
    to_sup  = ['url', 'month', 'number']        # Line to suppress
    debut =  re.compile('^\s*(\w+)\s*(=)\D*')   # Search for space - word - space - '='
    txt = fileBib.readline()                    # Read the first line of the bib file
    linePage   = FindLine('pages')              # Define the search pattern for pages
    lineJournal= FindLine('journal')            # Id. for journal
    journals   = Read_CSV('Journaux.csv') 
    status = 0
    log = open('MissingJournal.log', 'w')
    while txt:                                  # Loop to read the file
        try:
		if debut.search(txt) and debut.search(txt).group(1).lower() in to_sup:
	            if txt[-3:-1] == '}}':              # Avoid the line specified
	                file_BibOK.write('}\n')         # Avoid to delete the last }
	            else:
	                pass
	        elif linePage.search(txt):              # For the pages
	            pages = ChangePageNber(txt, style)
	            if txt[-3:-1] == '}}':
	                file_BibOK.write(pages + '}\n')
	            else:
	                file_BibOK.write(pages)
	        elif lineJournal.search(txt):           # For the journals
	            journal = Journal_Format(txt, lineJournal, journals, style)
	            journal = Journal_Name(journal)
	            if txt[-3:-1] == '}}':
	                file_BibOK.write(journal + '}},\n')
	            else:
	                file_BibOK.write(journal + '},\n') 
	        else:
	            file_BibOK.write(txt)   
	        txt=fileBib.readline()                  # Read the next line of the bib file
	except:
		status = 1
	return status	# Return the status of the processing to check if an error has occured



#################################################################
#################################################################
#####                                                       #####
#####              Tk GUI and MAIN PROGRAMM                 #####
#####                                                       #####
#################################################################
class FormAPA_GUI(Tkinter.Frame):       # A class for the GUI

  def __init__(self, root):
    self.root = root
    Tkinter.Frame.__init__(self, root)
    root.title("-- CleanMyBib --")      # Title for the main window
    self.style = Tkinter.IntVar()
    self.style.set(1)
    # options for buttons
    button_opt = {'fill': Tkconstants.BOTH, 'padx': 15, 'pady': 5}
    # define buttons
    Tkinter.Button(self, text='Choose a biblatex file and clean my bib',\
                   bg="lightblue", command=self.on_open_filename).pack(**button_opt)
    Tkinter.Button(self, text='Options', command=self.on_open_options_panel).pack(**button_opt)
    Tkinter.Button(self, text='About CleanMyBib', command=self.on_open_about_panel)\
            .pack(**button_opt)
    Tkinter.Button(self, text="Quit", fg="red", command=root.quit)\
            .pack(**button_opt)
    # define options for opening or saving a file
    self.file_opt = options = {}
    options['filetypes'] = [('Bibtex Files', '.bib')]
    options['parent'] = root
    options['title'] = 'Choose a Bibtex File'

  def on_open_options_panel(self):      # Options section
    win_opt = Tkinter.Toplevel()
    win_opt.title("Options")
    Tkinter.Label(win_opt, text='Please choose the style to use', fg='darkblue',\
                  font=('Helvetica',11)).grid(row=1, column=1, columnspan=2, padx=5, pady=5)
    apa = Tkinter.Radiobutton(win_opt, text='Style APA (format long)', \
                              variable=self.style, value=1)
    apa.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
    apa.select()
    Tkinter.Radiobutton(win_opt, text='Style Vancouver (short)', variable=self.style,\
                        value=2).grid(row=3, column=1, columnspan=2, padx=5, pady=5)
    Tkinter.Label(win_opt, text='APA= Journal name in long format (e.g. Psychology of\
                  Aging).\nAll pages are indicated (e.g. 1135 -- 1142)',\
                  wraplength=320, justify='left', anchor='w').grid(row=5, column=2, padx=5, pady=8)
    Tkinter.Label(win_opt, text='VANCOUVER= Journal name in short format\
                  (e.g. Psychol. of Aging).\nLast page numbers trunked if identical\
                  to the first page (e.g. 1135 -- 42)', wraplength=320,\
                  justify='left', anchor='w').grid(row=6, column=2, padx=5, pady=8)

    
  def on_open_about_panel(self):        # About section 
    win_abt = Tkinter.Toplevel()
    win_abt.title("-- About CleanMyBib --")
    labels_abt = {'fill': Tkconstants.BOTH, 'padx': 3, 'pady': 3}
    author = Tkinter.Label(win_abt, text="Author: G.T. Vallet", fg="darkblue",\
                           font=("Helvetica", 12)).pack(**labels_abt)
    license =  Tkinter.Label(win_abt, text="Licence: GPLv3", fg="darkblue").pack(**labels_abt)
    big_use1 =  Tkinter.Label(win_abt, text="CleanMyBib is a simple interface\
                              to format the bibliography file (bibtex file) according\
                              to the APA or Vancouver guideline.", wraplength=290,\
                              justify='left').pack(**labels_abt)
    big_use2 = Tkinter.Label(win_abt, text= "I) Delete the URL, number and month\
                             information,\nII) Transform into long or short format\
                             and then capitalize the name of the journal,\nIII)\
                             Complete or remove the page numbers of the last page.",\
                             anchor='w', wraplength=370, justify='left').pack(**labels_abt)                      
    big_use3 =  Tkinter.Label(win_abt, text="Thanks to Arnaud Fournel for his\
                              help").pack(**labels_abt)

  def on_open_filename(self):           # Open file section
    filename   = tkFileDialog.askopenfilename(**self.file_opt)  # Open the file selected txt=fileBibself.
    fileBib    = open(filename, 'r')         # Convert file into text lines 
    rep, name  = os.path.split(filename)
    name_bibOk = 'Clean-'+name
    BibOK      = os.path.join(rep, name_bibOk)
    file_BibOK = open(BibOK, 'w')
    status = Clean_FileBib(fileBib, file_BibOK, self.style.get())
    fileBib.close()
    file_BibOK.close()
    if status == 1: 	# Display a windows with the current status. Work done or error
        win_ttt = Tkinter.Toplevel()
	win_ttt.title("-- Error --")
	labels_ttt = {'fill': Tkconstants.BOTH, 'padx': 3, 'pady': 3}
	error = Tkinter.Label(win_ttt, text="\n\nAn error has occured, \nplease check your bibfile.\n\n", fg="darkblue",\
	                           font=("Helvetica", 12)).pack(**labels_ttt)	
        Tkinter.Button(win_ttt, text="OK", fg="black", command=win_ttt.destroy)\
            .pack(**labels_ttt)

    else:
        win_ttt = Tkinter.Toplevel()
	win_ttt.title("-- Done --")
	labels_ttt = {'fill': Tkconstants.BOTH, 'padx': 3, 'pady': 3}
	error = Tkinter.Label(win_ttt, text="\n\nYour file has been succefully proceed!\n\n", fg="darkblue",\
	                           font=("Helvetica", 14)).pack(**labels_ttt)
	Tkinter.Button(win_ttt, text="OK", fg="black", command=win_ttt.destroy)\
            .pack(**labels_ttt)



#################################################################
#################################################################
#####                                                       #####
#####                   RUN THE PROGRAM                     #####
#####                                                       #####
#################################################################
if __name__=='__main__':
  root = Tkinter.Tk()
  FormAPA_GUI(root).pack()
  root.mainloop()


