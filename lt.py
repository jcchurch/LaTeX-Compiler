#!/usr/bin/env python

"""
Filename: lt.py
Date:     July 3, 2010
Author:   James Church
Description:

This program will convert LaTeX documents into PDF. It checks to see
if there is also a BibTeX file in the same directory and if so will
run additional commands to make sure the BibTeX file is included.

To see the options, run "lt.py -h".

This program comes with no warrenty. This code belongs to you.
"""

import optparse
import subprocess
import sys
import os.path
import os

class LaTeX:

    def __init__(self, filename, papersize, verbose):

        # This can be changed to fit the user's preferences
        self.latex = "latex"
        self.bibtex = "bibtex"
        self.dvipdf = "dvipdfm"
        self.pdfview = "evince" # This is a PDF reader that comes installed by default on most Linux distros.

        self.verbose = verbose
        self.papersize = papersize

        # We first assume that the filename does not end with ".tex"
        self.basename = filename
        self.filename = filename + ".tex"

        # Then we check to see if this is true.
        if filename[-4:] == ".tex":
            self.basename = filename[:-4]
            self.filename = filename

        # Does the LaTeX file exist?
        if os.path.exists(self.filename) == False:
            print "Error: File "+self.filename+" not found."
            sys.exit(1)

        # Assume that there is no BibTeX file in the directory
        self.bibtexFound = False

        # Then check to see if true
        for fn in os.listdir("."):
            if fn[-4:] == ".bib":
                self.bibtexFound = True
                break

    def execute(self, run, ignoreErrors=False):
        if self.verbose:
            print "Command: ",run

        p = subprocess.Popen(run.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        output, error = p.communicate()
        p.stdin.close()
        exit_code = p.wait()

        if self.verbose:
            print output

        if exit_code != 0 and ignoreErrors == False:
            print "Errors generated: "
            print output
            print error
            return False
        return True

    def compile(self):
        success = self.execute(self.latex+" "+self.basename)
        if success == False:
            return False

        if self.bibtexFound:
            self.execute(self.bibtex+" "+self.basename)
            self.execute(self.latex+" "+self.basename)
            self.execute(self.latex+" "+self.basename)

        if os.path.exists(self.basename+".dvi"):
            self.execute(self.dvipdf+" -p "+self.papersize+" "+self.basename+".dvi", True)
        else:
            print "DVI Document ",self.basename+".dvi not found."
            return False
        return True

    def clean(self):
        extensions = ["aux", "bbl", "dvi", "log", "blg", "toc"]
        for ext in extensions: 
            try: os.unlink(self.basename+"."+ext)
            except: pass

    def show(self):
        if os.path.exists(self.basename+".pdf"):
            self.execute(self.pdfview+" "+self.basename+".pdf")
        else:
            print "PDF Document ",self.basename+".pdf not found."

def main():

    desc = """This program is used to convert LaTeX documents into PDF documents."""

    p = optparse.OptionParser(usage="%prog [options] [latex file]", version="%prog 1.0", description=desc)
    p.add_option('-s', '--show',    default=False, action='store_true', help="Show the completed PDF.")
    p.add_option('-v', '--verbose', default=False, action='store_true', help="Be verbose. Print what is going on.")
    p.add_option('-C', '--noclean', default=False, action='store_true', help="Delete intermediate files if typesetting successful.")
    p.add_option('-p', '--papersize', default="letter", help="Desired papersize handled by dvipdfm. Uses 'letter' by default.")
    options, arguments = p.parse_args()

    if len(arguments) != 1:
        print "Requires at least 1 textfile argument."
        return 0;

    filename = arguments[0]

    doc = LaTeX(filename, options.papersize, options.verbose)
    doc.clean()
    successfulCompile = doc.compile()

    if options.noclean == False and successfulCompile:
        doc.clean()

    if options.show and successfulCompile:
        doc.show()

    if successfulCompile == False:
        print "Failed to compile the LaTeX document."
        return 1

if __name__ == '__main__':
    sys.exit(main())
