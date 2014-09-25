#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A Python class to format bibtex references.
# From a provided bibtex file, the class will adapt the format for the journal
#   name and the page numbers into short or long format.
# Give a new cleaned file with the minimal required fields displayed nicely.
#
# G.T. Vallet -- University Lyon 2
# 2012/07/04  -- v04
# GPLv3

import re
import os
import sys
import csv
import platform
import textwrap
from pybtex.database.input import bibtex
import pybtex

reload(sys)
sys.setdefaultencoding("utf-8")


class CleanFileBib():
    """ A class to clean a bibtex file to format the journal name and the pages
          numbers into long or short format.
        Create a new file with minimal required fields.
    """

    def __init__(self, fileBib, file_BibOk, fields, journal_style = "long",
                     page_style="long"):
        """ Extract the references from the bibtex file,
            Format the page numbers and the journal name,
            Log missing data,
            Write the correct fields according to the reference type.
        """
        # Initiate a list to log missing page numbers and journals
        log_pageNber = []
        log_journals = []
        noYear = ["in press", "accepted", "sous presse", "accepté"]
        noPage = ["book", "manual"]
        # Parse the bibtex file
        parser, citeKeys, log_bibkey = self.parseBib(fileBib)
        # For each reference, change the format if needed and select the
        #   remaining fields to use
        for citeKey in citeKeys:
            ref =  parser.data.entries[citeKey]  # Select the current reference
            if ref.type not in noPage:
                try:
                    pages = self.ChangePageNber(ref.fields['pages'], page_style)
                except KeyError:
                    log_pageNber.append(citeKey)
                    pages = []
            else:
                pages = []
            journal = ""
            # Format the articles
            if ref.type == 'article':
                journal, fieldsToFill, log_journals = self.cleanArticle(citeKey,
                                       ref, journal_style, fields, log_journals)
            else:
                # Fields to exclude according to the reference kind
                other_exclude = ['pages', 'volume']
                fieldsToFill = []
                for field in fields:
                    if field not in other_exclude:
                        fieldsToFill.append(field)
            data = self.fillRef(ref, fieldsToFill, journal, pages)
            lenMax = self.fieldLengthMax(fields)
            file_BibOk.write(self.refPrint(citeKey, ref, data, lenMax))
        if log_bibkey or len(log_journals)>0 or len(log_pageNber)>0:
            self.logFile(fileBib, log_bibkey, log_pageNber, log_journals)


# -------------------------------------------------------------
#  PARSE THE BIBTEX FILE
# -------------------------------------------------------------
    def parseBib(self, fileBib):
        """ Use the bibtex parser to retrieve the references of the input file
            Return the parser and the citeKeys sorted.
        """
        parser = bibtex.Parser()
        try:
            bibData = parser.parse_file(fileBib)
            log_bibkey = None
        except pybtex.database.BibliographyDataError as e:
            msg = str(e).capitalize() + "\nPlease clean your file and try again.\n"
            log_bibkey = msg
            print("\n------------------------WARNING ! -------------------\n"
                    + msg + "\n-------------------------------------------\n")
            self.logFile(fileBib, log_bibkey, [], [])
            raise SystemExit(0)
        return parser, sorted(bibData.entries.keys()), log_bibkey


# -------------------------------------------------------------
#  PREPARE ARTICLE FORMATING
# -------------------------------------------------------------
    def cleanArticle(self, citeKey, ref, journal_style, fields, log_journals):
        """ A function to prepare which fields will be used for articles and
              format the journal name.
            Return the journal name and the list of fields to use.
            Write a log if necessary.
        """
        # Load journal names database
        journals = self.Read_CSV('.img/Journals.csv', 0, 1)
        # Initiate the list of fields to use for the reference
        fieldsToFill = []
        # Define which fields should be exclude for an article
        article_exclude = ['booktitle', 'editor', 'publisher', 'address']
        # Change the format of the journal name
        try:
            journal = self.Journal_Format(ref.fields['journal'].lower(),
                                             journals, journal_style)
        except:
            log_journals.append(citeKey)
            journal = ""
        try:
            journal = self.Journal_Name(journal)
        except:
            log_journals.append(citeKey)
            journal = ""
        # Define the fields to keep and fill the data into a list
        for field in fields:
            if field not in article_exclude:
                fieldsToFill.append(field)
        return journal, fieldsToFill, log_journals


# -------------------------------------------------------------
#  JOURNAL NAME FORMATING
# -------------------------------------------------------------
    def Read_CSV(self, file_name, col1=1, col2=2):
        """ A function to read a csv file into a dictionary
            Take the file name 'ex.csv' and the columns to read
            Give the dictionary as output
        """
        CSV_file = open(file_name, "rb")
        dico = {}
        try:
            reader = csv.reader(CSV_file, delimiter=',')
            for row in reader:
                dico[row[col1].lower()] = row[col2].lower()
        finally:
            CSV_file.close()
        return dico


    def Journal_Format(self, journal_name, journals, style='long'):
        """ Change name of the Journal according to APA/Vancouver style
        """
        # Style 'long' like in APA or 'short' like in Vancouver
        journal_name = journal_name.replace(".","")
        if style == 'long':
            # Reverse the dictionary (replace long name by short one)
            if journal_name in journals.values():
                dico_inv   = dict([(v, k) for (k, v) in journals.iteritems()])
                journal_ok = dico_inv[journal_name]
            else:
                journal_ok = journal_name
        elif style == 'short':
            if journal_name in journals.keys():
                journal_ok = journals[journal_name]
            else:
                journal_ok = journal_name
            # journal_ok = journal_ok.split(' ')
            # journal_ok = ". ".join(journal_ok)
        else:
            journal_ok = journal_name
        return journal_ok


    def Journal_Name(self, journal_name):
        """ A function to add a capital letter of each words of the journal name
            Expect for the liaison words
        """
        # List of the words or strings to not capitalize
        to_pass = ['et', 'le', 'la', 'de', 'du', 'l', 'a', 'an', 'in', 'to', \
                    'of', 'for', 'the', 'and', '-', '--', ':', '?']
        words = journal_name.split() # Split the journal's name (single word)
        words_ok = []                # Initiate an empty list
        if words[0][0] == '{':
            words_ok.append( words[0][1:].capitalize() ) # Capitalized the first word       
        else:
            words_ok.append( words[0].capitalize() ) # Capitalized the first word       
        for curWord in words[1:]:
            if curWord in to_pass:          # Capitalize the good words
                words_ok.append( curWord )  # Avoid the liaison words
            else:
                words_ok.append( curWord.capitalize() )
        journal_name_ok = ""     # Prepare the final name
        for i in words_ok:
            if i == words_ok[len(words_ok)-1]: # Construct the final name
                if i[-1] == "}": 
                    journal_name_ok += i[:-1]        # Avoid adding a 'space' at the end
                else:
                    journal_name_ok += i
            else:
                journal_name_ok += i+" "
        return journal_name_ok


# -------------------------------------------------------------
#  PAGE NUMBERS FORMATING
# -------------------------------------------------------------
    def PagesNber(self, t1, t2, style='long'):
        """ A function to correct the pages numbers
            In the long style format both page numbers have the same length
            In the short style format, the repeated first numbers are deleted
            First page is t1, last page is t2
            E.g.   Long (APA): 1128--35   transformed to 1128--1135
            E.g. Short (Vanc): 1128--1135 transformed to 1128--35
        """
        if style == 'long':
            while len(t1) > len(t2):     # Check if a correction is needed
                t2 = t1[-(1+len(t2))]+t2 # Add the missing numbers
        else:
            x, done = 0, 0         # Initiate control variables
            if len(t1) >= len(t2): # Check the pages format
                while done < 1:
                    if t1[x] == t2[x]: # Find how many number are identical
                        x += 1         # Increment control variable
                    else:
                        done = 1   # Exit the loop when numbers are different
                t2 = t2[x:]        # Correct the last page number value
        return t2


    def ChangePageNber(self, txt, style='long'):
        """ A function to apply the correct change page number,
              either regarding the APA or Vancouver guidelines.
            Find the groups of pages and send them to the APA/Vancouver function
        """
        # Extract the page numbers
        pagePattern= re.compile(r'\D*(\d+)\D*(\d*)\D*$')
        if pagePattern.search(txt) != None:
            pages= pagePattern.search(txt).groups() # Find the groups of numbers
            p1 = pages[0]  # Define p1 and p2
            p2 = pages[1]  # p1= first page; p2= last page
            if len(p2) > 0: # Check if a number for t2 exists
                t2 = self.PagesNber(p1, p2, style) # t2 is the new value of p2
            else:         # If no number for t2, then print XXXX
                t2 = 'XXXX'
            total  = p1 + '--' + t2  # Construct the final pages line
        else:
            total = ""
        return total


# -------------------------------------------------------------
#  PREPARE THE FINAL FILE
# -------------------------------------------------------------
    def fillRef(self, ref, fieldsOK, journal_ok, pages_ok):
        data = {}
        for field in fieldsOK:
            if field == "journal" and len(journal_ok)>0:
                data[field] = journal_ok
            elif field == "pages" and len(pages_ok)>0:
                data[field] = pages_ok
            else:
                try:
                    data[field] = ref.fields[field]
                except KeyError:
                    pass
        return data


    def fieldLengthMax(self, fields):
        lenMax = 0
        for field in fields:
            if len(field)>lenMax:
                lenMax = len(field)
        return lenMax


    def refPrint(self, citeKey, ref, data, lenMax):
        """ A function to format the printed reference into the bibtex rules
            Give a nice readable organization of the file
            Capitalized the first letter of the field names
        """
        header = "@{0}{{{1},".format(ref.type, citeKey)
        body   = ""
        for field in sorted(data.keys()):  # Loop to fill the reference
            body = body + "\n\t"
            spaces = ""
            if len(field)<lenMax:  # Harmonization of the fields spaces
                index = 0
                while index < lenMax-len(field):
                    spaces = spaces + " "
                    index += 1
            body = body + field.capitalize() + spaces + "=  {" +data[field]+"},"
        body = body[0:-1]  # Deleted the last comma
        footer = "\n}\n\n"
        return header+body+footer


# -------------------------------------------------------------
#  LOG FILE
# -------------------------------------------------------------
    def logFile(self, fileBib, keys, pageNber, journals):
        # Create a log file for more information about the bibfile
        rep, name  = os.path.split(fileBib)
        log = open(os.path.join(rep,"CleanMyBib.log"), "w")
        log.write("Log file of Clean My Bib\n========================\n")
        if keys:
            log.write("\nDuplicate bibtex keys:\n----------------------\n")
            log.write(keys)        
        if  len(journals)>0:
            log.write("\nMissing Journal Name\n--------------------\n")
            for ref in journals:
                log.write("Missing journal name for the reference '{0}'\n"
                                                            .format(ref))
        if len(pageNber)>0:
            log.write("\nMissing Page Numbers\n--------------------\n")
            for ref in pageNber:
                log.write("Missing page numbers for the reference '{0}'\n"
                                                                .format(ref))
        log.close()


# --------------------------------------------------------------
# START THE APPLICATION
# --------------------------------------------------------------
def main():
    """ If the script is called as a main script, define general options and
          launch the class to clean the file.
    """
    # Initiate the script
    os.system("clear")
    print "Welcome to CleanMyBib!"
    try:
        fileBib = sys.argv[1]  # Input file
        file_input = True
    except IndexError:
        print "\nNo bibtex file provided"
        file_input = False
    # Ask for a file
    while file_input is False:
        fileBib = raw_input("Please enter the path of a bibtex file: ")
        if os.path.exists(fileBib):
            file_input = True
    # Prepare the file name 
    rep, name = os.path.split(fileBib)
    fileOK_name = os.path.join(rep, 'Cleaned_'+name)
    # File cleaned
    fileOK  = open(fileOK_name, 'w')
    fields = ['abstract','author','year','title', 'journal', 'booktitle', \
                'pages', 'volume', 'editor','publisher','address']
    # Define the options
    print "\nPlease define the following options:"
    journal_style = raw_input("Format for the journal names (long/short): ")
    while journal_style != "long" and journal_style != "short":
        print "Please enter 'long' or 'short'..."
        journal_style = raw_input("Format for the journal names (long/short): ")
    page_style = raw_input("Format for the page numbers (long/short): ")
    while page_style != "long" and page_style != "short":
        print "Please enter 'long' or 'short'..."
        page_style = raw_input("Format for the page numbers (long/short): ")
    doi = raw_input("Add the doi field (Y/N)? ")
    while doi != "y" and doi != "n":
        print "Please enter 'y' or 'n'..."
        doi = raw_input("Add the doi field (Y/N)? ")
    if doi == 'y':
        fields.append('doi')
    # Launch the app
    app = CleanFileBib(fileBib, fileOK, fields, journal_style, page_style)
    # Closing
    print "\nYour bibtex file is now cleaned and save as %s!\n" % (fileOK_name)

if __name__ == '__main__':
    main()
