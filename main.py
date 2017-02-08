from __future__ import print_function #debug
import sys,os #sys debug
import logging
import json, boto3
import time
from handlers.LaTex import award as ah
from handlers.Database import database
from handlers.Database import models
from handlers.Email import email
from string import replace
from flask import Flask, render_template, send_file, abort, request, redirect, url_for, jsonify, session, Response
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

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
models.Employee,
models.AwardBorder)

emailer = email.Emailer()

@app.route('/')
def renderIndex():
	#alchemist.createRootAdmin()
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
		account = alchemist.createAccount(payload)
		status = alchemist.save(account)
		
		if status == False:
			return render_template('new-account.html',status=status) #explain that account could not be created
		
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


@app.route('/latex', methods=['POST'])
@login_required
def renderPDF():
	#still just a testing LaTex functionality
	payload = request.form

	award = alchemist.createAward(payload, session['email'])
	status = alchemist.save(award)
	
	if status is False:
		abort(500)
	
	sigFile = session['email']
	sigFile = replace(sigFile,'@','_')
	sigFile = replace(sigFile,'.','_')
	sigFile += '_sig.png'
	
	details = alchemist.getUserDetails(session['email']) #get details in login route and add title to session var
	
	if payload['border'] == '1':
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
	
	awardDate = award.issuedOn
	awardDateString = awardDate.strftime("%m-%d-%Y")

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
	'signature':sigFile,
	'granted':awardDateString}
	
	employeeAward = ah.Award(awdDetails,filename)
	pdf = employeeAward.genAward()
	

	if pdf is not None:
		'''
		#if response code is not 202 then something bad happened... added error checking
		#the send award function takes two optional arguments: sub -> the email subject line | text -> the email body
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
		alchemist.remove(award)
		abort(500)

@app.route('/get-employee',methods=['POST'])
def getEmployees():
	if request.json:
		employees = alchemist.getEmployees(request.get_json())
		return jsonify(employees)
	else:
		abort(400) #put error on create page

#HAVE TO TEST!
@app.route('/get-password',methods=['POST'])
def getPassword(): #i need her to send me the email and reset value. then i can return the questions
	payload = request.form
	details = alchemist.getUserDetails(payload['email'])
	
	if details is None:
		abort(404) #put error feedback on reset password page - i.e. no such email is tied to an existing account
			
	if payload['reset-method'] == 'question':
		questions = {'1':details['question1'], '2':details['question2']}
		
		return jsonify(questions)
		
	if payload['reset-method'] == 'email':
		code = alchemist.genVerificationCode(details['account']) #remember to remove the code from the db after they reset their password
		
		if code is not None:
			response = emailer.sendPasswordReset(payload['email'],code)
		else:
			abort(500)

@app.route('/get-question',methods=['POST'])
def checkQuestions():
	pass
	
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

@app.errorhandler(404)
def resourceNotFoundError(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 400
	
@app.errorhandler(401)
def unauthorizedError(e):
    return '<h1>You are not authorized to access this page.</h1> \
	<p>Please login <a href=/login>here</a></p>', 401

@app.errorhandler(400)
def badRequestError(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: ' + str(e), 400
	
if __name__ == "__main__":
    app.run()




