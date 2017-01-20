from __future__ import print_function #debug
import sys,os #debug
import logging
from flask import Flask, render_template, send_file
from latex import build_pdf
#import smtplib
#from email.mime.text import MIMEText
#from pylatex import Document, Section, Subsection, Command
#from pylatex.utils import italic, NoEscape

app = Flask(__name__)

'''
def fill_document(doc):
    """Add a section, a subsection and some text to the document.

    :param doc: the document
    :type doc: :class:`pylatex.document.Document` instance
    """
    with doc.create(Section('A section')):
        doc.append('Some regular text and some ')
        doc.append(italic('italic text. '))

        with doc.create(Subsection('A subsection')):
            doc.append('Also some crazy characters: $&#{}')
'''
			
@app.route('/')
def renderIndex():
	min_latex = (r"\documentclass{article}"
             r"\begin{document}"
             r"Hello, world!"
             r"\end{document}")
	# this builds a pdf-file inside a temporary directory
	pdf = build_pdf(min_latex)
	pdf.save_to('./test.pdf')
	if os.path.exists('./test.pdf') == True:
		print('FOUND FILE!!!',file=sys.stderr)
	else:
		print('NO FILE!!!',file=sys.stderr)
		
	return send_file('./test.pdf')
	'''fp = './basic'
	doc = Document(fp)
	fill_document(doc)
	if os.path.exists('./basic.tex') == True:
		print('FOUND FILE!!!',file=sys.stderr)
	else:
		print('NO FILE!!!',file=sys.stderr)
		
	doc.generate_pdf(filepath='./basic',clean_tex=False)
	if os.path.exists('./basic.pdf') == True:
		print('FOUND PDF!!!',file=sys.stderr)
	else:
		print('NO PDF!!!',file=sys.stderr)
	'''
	#return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

if __name__ == "__main__":
    app.run()