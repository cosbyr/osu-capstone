from __future__ import print_function #debug
import sys,os #sys debug
import logging
import json, boto3
from handlers.LaTex import award as ah
from handlers.Database import database
from handlers.Database import models
from flask import Flask, render_template, send_file, abort, request, redirect, url_for, jsonify, session
from flask_cors import CORS, cross_origin


app = Flask('app',template_folder='./templates',static_folder='./static')
app.secret_key = os.environ['SECRET_KEY']
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
database.db.init_app(app)

'''
#this was used to create the database 
from handlers.Database import models
with app.app_context():
	database.db.create_all()
	database.db.session.commit()
'''

alchemist = database.PostgresDatabase(
models.Question,
models.Account,
models.Admin,
models.Manager,
models.AwardType,
models.Award,
models.AwardArchive)

#the login link should only be present on the index and perhaps the login page. when logged in, this link should change to logout

@app.route('/')
def renderIndex():
	if 'email' in session:
		session.pop('email', None)
		
	return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def renderLogin():
	if request.method == 'GET':
		if 'email' in session:
			session.pop('email', None)
			
		return render_template('login.html')
	
	if request.method == 'POST':
		payload = request.form
		status = alchemist.login(payload)
		
		if status == False:
			return render_template('login.html',status=status)
		
		session['email'] = payload['userName']
		if payload['account-type'] == 'user':
			return redirect(url_for('renderUser'))
		
		if payload['account-type'] == 'admin':
			return redirect(url_for('renderAdmin'))

@app.route('/logout')
def renderLogout():
	session.pop('email', None)
	return render_template('logout.html')

@app.route('/admin')
def renderAdmin():
	return render_template('admin.html')

@app.route('/user')
def renderUser():
	if 'email' not in session:
		return redirect(url_for('renderLogin'))
		
	return render_template('user.html',user=session['email'])

@app.route('/update-account',methods=['GET','POST'])
def renderUpdateAccount():	
	if request.method == 'GET':
		if 'email' not in session:
			return redirect(url_for('renderLogin'))
			
		details = alchemist.getUserDetails(session['email'])
		
		if details is None:
			abort(500) #this should flash a message rather than abort. will fix later
			
		return render_template('update-account.html',details=details)
		
	if request.method == 'POST':
		payload = request.form
		status = alchemist.updateAccount(payload,session['email'])
		
		if status == False:
			return redirect(url_for('renderUpdateAccount'))
			
		return redirect(url_for('renderUser'))
	

@app.route('/create')
def renderCreate():
	if 'email' not in session:
		return redirect(url_for('renderLogin'))
		
	return render_template('create.html')

@app.route('/history')
def renderHistory():
	return render_template('history.html')

@app.route('/new-account',methods=['GET','POST'])
def renderNewAccount():
	if request.method == 'GET':
		questions = alchemist.getQuestions()
		return render_template('new-account.html',questions=questions)
	
	if request.method == 'POST':
		payload = request.form
		logging.warning(payload)
		status = alchemist.createAccount(payload)
		
		if status == False:
			return render_template('new-account.html',status=status)
		
		return redirect(url_for('renderLogin',status=status))

		
@app.route('/sign_s3/')
def sign_s3():
	S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

	file_name = request.args.get('file_name')
	file_type = request.args.get('file_type')

	s3 = boto3.client('s3')

	presigned_post = s3.generate_presigned_post(
		Bucket = S3_BUCKET,
		Key = file_name,
		Fields = {"acl": "public-read", "Content-Type": file_type},
		Conditions = [
			{"acl": "public-read"},
			{"Content-Type": file_type}
		],
		ExpiresIn = 3600
	)
	return json.dumps({
		'data': presigned_post,
		'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
	})
	
@app.route('/password')
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
	'type':'Employee of the Month',
	'employee':'Aristotle Jones',
	'admin1':'John Doe',
	'adminTitle1':'Supervisor',
	'signature':'static/images/ex-sig.png'}
	
	award = ah.Award(details,filename)
	pdf = award.genAward()
	
	if pdf is not None:
		return send_file(pdf)
	else:
		abort(500) #change to proper error code



@app.route('/jquery')
def jquerytest():
    return render_template('jquery.html')

@app.errorhandler(500)
def serverError(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500
	
if __name__ == "__main__":
    app.run()




