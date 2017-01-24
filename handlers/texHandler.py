from __future__ import print_function #debug
import os,sys #debug
#from latex import build_pdf, LatexBuildError
import latex

def genAward(texFile):
	os.system('pdflatex ' + texFile)
	pdf = texFile[:-3] + 'pdf'
	return pdf