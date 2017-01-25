from __future__ import print_function #debug
import sys,os #debug
import logging
from handlers import award as ah, database as dbh
from flask import Flask, render_template, send_file, abort

db = dbh.connectDB()
app = Flask(__name__)
		
@app.route('/')
def renderIndex():		
	return render_template('index.html')

@app.route('/latex')
def renderPDF():
	filename = 'test'
	details = {
	'background':'static/images/tiling.png',
	'logo':'static/images/gateway.png',
	'company':'Gateway Mapping, Inc.',
	'message':'In recognition of hard work and passion we hereby award',
	'title':'Employee of the Month',
	'employee':'Aristotle Jones',
	'admin1':'John Doe',
	'admin2':'Jane Smith',
	'adminTitle1':'Supervisor',
	'adminTitle2':'Head of Department'}
	
	award = ah.Award(details,filename)
	pdf = award.genAward()
	
	return send_file(pdf)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

if __name__ == "__main__":
    app.run()