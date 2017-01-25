from __future__ import print_function #debug
import sys,os #debug
import logging
from handlers import texHandler, dbHandler
#import texHandler
#import dbHandler
from flask import Flask, render_template, send_file

dbHandler.connectDB()

app = Flask(__name__)
		
@app.route('/')
def renderIndex():		
	return render_template('index.html')

@app.route('/latex')
def renderPDF():
	#just a test. changes will be made to this when we have a better idea how this function should... uh, function

	tex2 = (r"\documentclass{article}"
			 r"\begin{document}"
			 r"Hello, world!"
			 r"\end{document}")
	tex = (r"\documentclass[landscape]{article}"
			r"\usepackage{wallpaper}"
			r"\usepackage{niceframe}"
			r"\usepackage{xcolor}"
			r"\usepackage{ulem}"
			r"\usepackage{graphicx}"
			r"\usepackage{geometry}"
			r"\geometry{tmargin=.5cm,bmargin=.5cm,"
			r"lmargin=.5cm,rmargin=.5cm}"
			r"\usepackage{multicol}"
			r"\setlength{\columnseprule}{0.4pt}"
			r"\columnwidth=0.3\textwidth"
			r"\begin{document}"
			r"\centering"
			r"\scalebox{3.05}{\color{green!30!black!60}"
			r"\begin{minipage}{.33\textwidth}"
			r"\font\border=umrandb"
			r"\generalframe"
			r"{\border \char113} % up left"
			r"{\border \char109} % up"
			r"{\border \char112} % up right"
			r"{\border \char108} % left"
			r"{\border \char110} % right"
			r"{\border \char114} % lower left"
			r"{\border \char111} % bottom"
			r"{\border \char115} % lower right"
			r"{\centering"
			r"\begin{minipage}{.9\textwidth}"
			r"\centering"
			r"\includegraphics[height=0.9cm,natwidth=300,natheight=124{gateway.png}"
			r"\end{minipage}"
			r"\vspace{-8mm}"
			r"\curlyframe[.9\columnwidth]{"
			r"\textcolor{red!10!black!90}"
			r"{\small Gateway Mapping, Inc.}\\"
			r"\textcolor{green!10!black!90}{"
			r"\tiny In recognition of hardwork and passion we hereby award}"
			r"\smallskip"
			r"\textcolor{black}{\large \textsc{Employee of the Month}}"
			r"\vspace{2mm}"
			r"\small"
			r"{\textcolor{black}{"
			r"\uppercase{Employee Name}}}"
			r"\vspace{8mm}"
			r"{\color{blue!40!black}"
			r"\scalebox{.7}{"
			r"\begin{tabular}{ccc}"
			r"\cline{1-1}"
			r"\cline{3-3}"
			r"\ John Doe & & Bob Doe\\"
			r"\ Supervisor & & Head of Department\\"
			r"\end{tabular}"
			r"}}}}"
			r"\end{minipage}"
			r"}"
			r"\end{document}")
	filename = 'test'
	pdf = texHandler.genAward(tex,filename)
	return send_file(pdf)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

if __name__ == "__main__":
    app.run()