from __future__ import print_function #debug
import os,sys #debug
#from latex import build_pdf, LatexBuildError
import latex

def genAward(texFile):
	os.system('pdflatex ' + texFile)
	pdf = texFile[:-3] + 'pdf'
	if os.path.exists(pdf):
		print('FILE EXISTS!!!',file=sys.stderr)
	else:
		print('NOTHING!!!',file=sys.stderr)
	#os.system('mv ' + pdf + '~/')
	return pdf