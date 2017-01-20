from __future__ import print_function #debug
import sys,os #debug
import logging
import psycopg2
import urlparse
from flask import Flask, render_template, send_file
from latex import build_pdf

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
	database=url.path[1:],
	user=url.username,
	password=url.password,
	host=url.hostname,
	port=url.port
)

app = Flask(__name__)

#test for the PDF generation using LaTex and the latex library		
@app.route('/')
def renderIndex():
	min_latex = (r"\documentclass{article}"
             r"\begin{document}"
             r"Hello, world!"
             r"\end{document}")
			 
	pdf = build_pdf(min_latex)
	pdf.save_to('./test.pdf')
	
	'''debug - makes sure the PDF file exists
	if os.path.exists('./test.pdf') == True:
		print('FOUND FILE!!!',file=sys.stderr)
	else:
		print('NO FILE!!!',file=sys.stderr)'''
		
	#return send_file('./test.pdf')
	
	return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

if __name__ == "__main__":
    app.run()