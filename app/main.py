from __future__ import print_function #debug
import sys,os #debug
import logging
from handlers.LaTex import award
from handlers.Database import database
from handlers.Database import models
from flask import Flask, render_template, send_file, abort, request, redirect


app = Flask('app',template_folder='./app/templates',static_folder='./app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
database.db.init_app(app)

postgres = database.PostgresDatabase(
models.Account,
models.Admin,
models.Employee,
models.Branch,
models.State,
models.Department,
models.AwardType,
models.Award,
models.AwardArchive)

'''
#this was used to create the database 
from handlers.Database import models
with app.app_context():
	database.db.create_all()
	database.db.session.commit()
'''

@app.route('/')
def renderIndex():
	return render_template('index.html')

@app.route('/login.html')
def renderLogin():
	return render_template('login.html')

@app.route('/admin.html')
def renderAdmin():
	return render_template('admin.html')

@app.route('/user.html')
def renderUser():
	return render_template('user.html')

@app.route('/create.html')
def renderCreate():
	return render_template('create.html')

@app.route('/history.html')
def renderHistory():
	return render_template('history.html')

@app.route('/new-account.html',methods=['GET','POST'])
def renderNewAccount():
	if request.method == 'GET':
		return render_template('new-account.html')
	
	if request.method == 'POST':
		payload = request.form
		postgres.createAccount(payload)
		return redirect('/login.html',code=201)

@app.route('/password.html')
def renderPassword():
	return render_template('password.html')

@app.route('/latex')
def renderPDF():
	#still just a testing LaTex functionality
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
	
	award = award.Award(details,filename)
	pdf = award.genAward()
	
	if pdf is not None:
		return send_file(pdf)
	else:
		abort(500) #change to proper error code


@app.errorhandler(500)
def serverError(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500
	
if __name__ == "__main__":
    app.run()