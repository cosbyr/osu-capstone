from __future__ import print_function #debug
import sys,os #debug
import logging
from flask import Flask, render_template
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape, make_temp_dir

app = Flask(__name__)

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
			
@app.route('/')
def renderIndex():
	#print('FILEPATH----->' + str(fp), file=sys.stderr)
	fp = './test'
	doc = Document(fp)
	fill_document(doc)
	doc.generate_tex()
	if os.path.exists('./test.tex') == True:
		print('!!!FOUND FILE!!!',file=sys.stderr)
	else:
		print('NO FILE!!!',file=sys.stderr)
	'''doc.generate_pdf()
	if os.path.exists('./test.pdf') == True:
		print('!!!FOUND PDF!!!',file=sys.stderr)
	else:
		print('NO PDF!!!',file=sys.stderr)'''
	return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

if __name__ == "__main__":
    app.run()