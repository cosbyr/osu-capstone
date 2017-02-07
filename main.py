from __future__ import print_function #debug
import sys,os #sys debug
import logging
import json, boto3
from handlers.LaTex import award as ah
from handlers.Database import database
from handlers.Database import models
from handlers.Email import email
from string import replace
from flask import Flask, render_template, send_file, abort, request, redirect, url_for, jsonify, session, Response
from flask_cors import CORS, cross_origin
from flask.ext.login import LoginManager, login_required, current_user, login_user, logout_user

app = Flask('app',template_folder='./templates',static_folder='./static')
app.secret_key = os.environ['SECRET_KEY']

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
database.db.init_app(app)

loginManager = LoginManager()
loginManager.init_app(app)

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
models.AwardArchive,
models.AwardBackground,
models.AwardTheme,
models.Employee)

emailer = email.Emailer()
	
@app.route('/')
def renderIndex():
	return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def renderLogin():
	if request.method == 'GET':			
		return render_template('login.html')
	
	if request.method == 'POST':
		payload = request.form
		status,account = alchemist.login(payload)

		if status == False:
			return render_template('login.html',status=status)
		
		session['email'] = payload['userName']
		session['role'] = payload['account-type']
		
		status,account = alchemist.setAuthenticated(account,True)

		if status == True:
			login_user(account)
			if payload['account-type'] == 'admin':
				return redirect(url_for('renderAdmin'))
			else:
				session['name'] = '{0} {1}'.format(account.manager.fname,account.manager.lname)
				return redirect(url_for('renderUser'))			
		else:
			abort(401)
			

@app.route('/logout')
def renderLogout():
	#session.pop('email', None)
	alchemist.setAuthenticated(current_user,False)
	logout_user()
	return render_template('logout.html')

@app.route('/admin')
@login_required
def renderAdmin():
	if session['role'] == 'admin':
		return render_template('admin.html')
	else:
		abort(401)

@app.route('/user')
@login_required
def renderUser():
	#details = alchemist.getUserDetails(session['email'])
	#return render_template('user.html',details=details)
	if session['role'] == 'user':
		return render_template('user.html',username=session['name'],email=session['email'])
	else:
		abort(401)

@app.route('/update-account',methods=['GET','POST'])
@login_required
def renderUpdateAccount():	
	if session['role'] == 'user':
		if request.method == 'GET':
			details = alchemist.getUserDetails(session['email'])
			
			if details is None:
				abort(500) #this should flash a message rather than abort. will fix later
				
			return render_template('update-account.html',username=session['name'],details=details)
			
		if request.method == 'POST':
			payload = request.form
			status = alchemist.updateAccount(payload,session['email'])
			
			if status == False:
				#print some error message on the update page after the redirect as to why the account could not be updated
				return redirect(url_for('renderUpdateAccount'))
				
			session['name'] = '{0} {1}'.format(payload['firstName'],payload['lastName'])
			session['email'] = payload['email']
			return redirect(url_for('renderUser'))
	else:
		abort(401)
	

@app.route('/create')
@login_required
def renderCreate():
	if session['role'] == 'user':
		awardBackgrounds = alchemist.getAwardBackgrounds()
		awardThemes = alchemist.getAwardThemes()
		awardTypes = alchemist.getAwardTypes()
		return render_template('create.html', username=session['name'], awardBackgrounds=awardBackgrounds, awardThemes=awardThemes, awardTypes=awardTypes)
	else:
		abort(401)

@app.route('/history')
@login_required
def renderHistory():
	if session['role'] == 'user':
		#details = alchemist.getUserDetails(session['email'])	
		return render_template('history.html',username=session['name'])
	else:
		abort(401)

@app.route('/new-account',methods=['GET','POST'])
def renderNewAccount():
	if request.method == 'GET':
		questions = alchemist.getQuestions()
		return render_template('new-account.html',questions=questions)
	
	if request.method == 'POST':
		payload = request.form
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
@login_required
def renderPassword():
	return render_template('password.html')

@app.route('/latex', methods=['POST'])
@login_required
def renderPDF():
	#still just a testing LaTex functionality
	payload = request.form
	status,award = alchemist.createAward(payload, session['email'])
	
	if status == False:
		return abort(400) #instead of abort, redirect back to create page and inform user that the award could not be created (probably due to a bad email)
	
	sigFile = session['email']
	sigFile = replace(sigFile,'@','_')
	sigFile = replace(sigFile,'.','_')
	sigFile += '_sig.png'
	
	details = alchemist.getUserDetails(session['email']) #get details in login route and add title to session var
	
	if payload['border'] == 'border1':
		border = r'''{\border \char113} % up left
				{\border \char109} % up
				{\border \char112} % up right
				{\border \char108} % left 
				{\border \char110} % right
				{\border \char114} % lower left
				{\border \char111} % bottom
				{\border \char115} % lower right'''
	else:
		border = r'''{\border \char005} % up left
				{\border \char001} % up
				{\border \char004} % up right
				{\border \char002} % left 
				{\border \char000} % right
				{\border \char006} % lower left
				{\border \char003} % bottom
				{\border \char007} % lower right'''
	
	filename = 'award'
	awdDetails = {
	'background':'static/images/' + award.award_background.filename,
	'border': border,
	'color':award.award_theme.theme,
	'logo':'static/images/gateway.png',
	'company':'Gateway Mapping, Inc.',
	'message': award.message,
	'type': award.award_type.name,
	'employee':award.employee.fname + ' ' + award.employee.lname,
	'admin':session['name'],
	'adminTitle':details['title'],
	'signature':sigFile}
	
	award = ah.Award(awdDetails,filename)
	pdf = award.genAward()
	

	if pdf is not None:
		#testing email functionality
		#if response code is not 202 then something bad happened... added error checking
		#the send award function takes two optional arguments: sub -> the email subject line | text -> the email body
		'''
		sender = session['email']
		recepient = payload['recpEmail']
		response = emailer.sendAward(sender,recepient,pdf)
		
		#debug
		print('Code: {0}'.format(response.status_code,file=sys.stderr))
		sys.stdout.flush()
		print('Body: {0}'.format(response.body,file=sys.stderr))
		sys.stdout.flush()
		print('Headers: {0}'.format(response.headers,file=sys.stderr))
		sys.stdout.flush()
		#end debug
		'''
		return send_file(pdf)
	else:
		abort(500) #change to proper error code

@app.route('/get-employee',methods=['POST'])
def getEmployees():
	status,employees = alchemist.getEmployees(request.json['lname'])
	
	if status == False:
		abort(400) #replace with an error on the create award page
		
	return jsonify(employees)

@loginManager.user_loader
def accountLoader(id):
	return alchemist.getAccount(id)
	
@app.route('/jquery')
def jquerytest():
    return render_template('jquery.html')
	
@app.errorhandler(500)
def serverError(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 500

@app.errorhandler(401)
def unathorizedError(e):
    return '<h1>You are not authorized to access this page.</h1> \
	<p>Please login <a href=/login>here</a></p>', 401
	
if __name__ == "__main__":
    app.run()




