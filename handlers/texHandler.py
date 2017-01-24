from __future__ import print_function #debug
import os,sys #debug

def genAward(texFile):
	os.system('pdflatex ' + texFile)
	pdf = texFile[:-3] + 'pdf'
	return pdf