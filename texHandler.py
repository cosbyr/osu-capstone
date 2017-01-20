from latex import build_pdf

def genAward(tex,filename):
	filename = './' + filename + '.pdf'
	pdf = build_pdf(tex)
	pdf.save_to(filename)
	return filename