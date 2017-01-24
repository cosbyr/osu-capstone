from __future__ import print_function #debug
import os,sys #debug
#from latex import build_pdf, LatexBuildError
import latex

def genAward(texFile,filename):
	filename = './' + texFile[:-3] + 'pdf'
	'''pdf = build_pdf(tex)
	pdf.save_to(filename)'''
	
	'''builder = latex.build.PdfLatexBuilder()
	builder.build_pdf(tex)
	pdf.save_to(filename)'''
	
	os.system("pdflatex " + './' + texFile)
	#os.system("mv " + filename + './')
	return filename
	'''try:
		pdf = build_pdf(tex)
		pdf.save_to(filename)
		return filename
	except LatexBuildError as e:
		for err in e.get_errors():
			print('Error in {0[filename]}, line {0[line]}: {0[error]}'.format(err),file=sys.stderr)
			print('    {}'.format(err['context'][1]),file=sys.stderr)
			print()'''
			
	