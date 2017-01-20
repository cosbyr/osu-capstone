from __future__ import print_function #debug
import sys,os #debug
import logging
import texHandler
import dbHandler
from flask import Flask, render_template, send_file

dbHandler.connectDB()

app = Flask(__name__)
		
@app.route('/')
def renderIndex():		
	return render_template('index.html')

	
@app.route('/latex')
def renderPDF():
		#just a test. changes will be made to this when we have a better idea how this function should... uh, function
		filename = 'test'
		pdf = texHandler.genAward(filename)
		return send_file(pdf)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

if __name__ == "__main__":
    app.run()