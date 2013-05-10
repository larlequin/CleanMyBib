CleanMyBib
==========

CleanMyBib is a Python script to automatically format a bibtex file.
The script will change the journal name and the page numbers format and will create a new bibtex file nicely formatted.

Created by Guillaume T. Vallet 

Improved version --2011/11/22-- v02  
Add a Qt version --2011/03/10-- v03  
New version of the script (Pybtex) --2012/07/05-- v04  
Interactive script --2012/07/26-- v04.1  

Laval University (Quebec city, Canada) / Lyon 2 University (Lyon, France)

Copyright Vallet 2011-2012
Licence: GPL v3


Functions
=========

From an input bibtex file, the script will create a new and nicely formated bibtex file.
The journal name could be formated into a long (complete) or short (abbreviate) format based on the PubMed database
[Pubmed](http://www.ncbi.nlm.nih.gov/nlmcatalog/journals).
The page numbers could also be formatted into a long (e.g. 1125--1138) or short (1125--38) version.

The new file is called "Clean-*original_filename*" if you use the Qt graphical user interface (GUI) or "bibcleaned.bib" if you use the script version.
The references are sorted by citation keys and only the minimum needed fields remaine displayed.

The format options and the fields to keep could be chosen in the script or in the GUI version.

If page numbers or journal names are missing, a log file (CleanMyBib.log) will be created and will indicate the citation keys of the references involved. The script is smart enough to detect if the references should not have pages numbers as "in press" articles or books.


Dependences
===========

The script is based on [Python](http://http://www.python.org/) 2.x.
If you don't have a working version of Python, you can download it [here](http://http://www.python.org/download/).

The bibtex references are parsed by the Pybtex module. You can download a version of [Pybtex](http://pybtex.sourceforge.net/#download), it's free and works on all platforms.
To install Pybtex, go the folder downloaded and simply run this command:

    python setup.py install

For the GUI version, you need to have a working version of [Qt](http://qt.nokia.com/) and [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro).


