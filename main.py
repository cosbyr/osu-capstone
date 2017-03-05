from __future__ import print_function #debug
import sys,os #sys debug
import logging
import json, boto3
from handlers.LaTex import award as ah
from handlers.Database import database
from handlers.Database import models
from handlers.Email import email
from handlers.Report import report
from string import replace
from flask import Flask, render_template, send_file, abort, request, redirect, url_for, jsonify, session, Response, flash
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

ERROR = 'red'
SUCCESS = 'green'

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
models.AwardBackground,
models.AwardTheme,
models.Employee,
models.AwardBorder)

emailer = email.Emailer()

reporter = report.Reporter(alchemist.database)

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
		response = alchemist.login(payload)

		if response['status'] != 200:
			flash(response['message'],ERROR)
			return render_template('login.html')
		
		session['email'] = payload['userName']
		session['role'] = payload['account-type']

		status = alchemist.setAuthenticated(response['account'],True)

		if status == True:
			login_user(response['account'])
			if payload['account-type'] == 'admin':
				session['name'] = '{0} {1}'.format(response['account'].admin.fname,response['account'].admin.lname)
				return redirect(url_for('renderAdmin'))
			else:
				session['name'] = '{0} {1}'.format(response['account'].manager.fname,response['account'].manager.lname)
				session['title'] = response['account'].manager.title
				return redirect(url_for('renderUser'))			
		else:
			abort(401)
			

@app.route('/logout')
def renderLogout():
	alchemist.setAuthenticated(current_user,False)
	logout_user()
	return render_template('logout.html')

	
@app.route('/admin')
@login_required
def renderAdmin():
	if session['role'] == 'admin':
		return render_template('admin.html', username=session['name'],email=session['email'],updateRoute='update-admin-account')
	else:
		abort(401)

@app.route('/admins')
@login_required
def renderAdmins():
	if session['role'] == 'admin':
		admins = alchemist.getAdmins(session['email'])
		return render_template('admins-list.html', admins=admins, username=session['name'], email=session['email'],updateRoute='update-admin-account')
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
				abort(500)
				
			return render_template('update-account.html',username=session['name'],details=details)
			
		if request.method == 'POST':
			payload = request.form
			status = alchemist.updateAccount(payload,session['email'])
			
			if status == False:
				flash('Unable to update account. Either the email provided is already linked to an account or there was a server error. Please, try again.', ERROR)
				return redirect(url_for('renderUpdateAccount'))
				
			session['name'] = '{0} {1}'.format(payload['firstName'],payload['lastName'])
			session['email'] = payload['email']
			session['title'] = payload['jobTitle']
			##flash('Account was successfully updated.',SUCCESS) <---this is not displaying correctly
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

'''
#i think this functionality is actually handled by the awards route down below
@app.route('/history')
@login_required
def renderHistory():
	if session['role'] == 'user':
		return render_template('history.html',username=session['name'])
	else:
		abort(401)
'''

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
			flash('Unable to create account. The email provided is already linked to an account.',ERROR)
			return redirect(url_for('renderNewAccount'))
		
		flash('Account created.',SUCCESS)
		return redirect(url_for('renderLogin'))

		
@app.route('/new-admin-account',methods=['GET','POST'])
def renderNewAdminAccount():
	if request.method == 'GET':
		questions = alchemist.getQuestions()
		return render_template('new-admin-account.html',questions=questions, username=session['name'], email=session['email'],updateRoute='update-admin-account')
	
	if request.method == 'POST':
		payload = request.form
		account = alchemist.createAdminAccount(payload)
		status = alchemist.save(account)
		
		if status == False:
			flash('Unable to create admin account. The email provided is already linked to an account.',ERROR)
			return redirect(url_for('renderNewAdminAccount', username=session['name'], email=session['email']))###,updateRoute='update-admin-account' maybe
		
		flash('Admin account created.',SUCCESS)
		return redirect(url_for('renderAdmin', username=session['name'], email=session['email']))

		
@app.route('/update-admin-account/',methods=['GET','POST'])
@login_required
def renderUpdateAdminAccount():	
	if session['role'] == 'admin':
		if request.method == 'GET':
			details = alchemist.getAdminDetails(session['email'])
			
			if details is None:
				abort(500)
				
			return render_template('update-admin-account.html',username=session['name'], email=session['email'], details=details,updateRoute='update-admin-account')
			
		if request.method == 'POST':
			payload = request.form
			status = alchemist.updateAdminAccount(payload,session['email'])
			
			if status == False:
				flash('Unable to update admin account. Either the email provided is already linked to an account or there was a server error. Please, try again.', ERROR)
				return redirect(url_for('renderUpdateAdminAccount', username=session['name'], email=session['email'], details=details))
				
			session['email'] = payload['email']
			session['name'] = '{0} {1}'.format(payload['firstName'],payload['lastName'])
			flash('Admin account was successfully updated.',SUCCESS)
			return redirect(url_for('renderAdmins'))
	else:
		abort(401)

@app.route('/update-other-admin-account/',methods=['GET','POST'])
@login_required
def renderUpdateOtherAdminAccount():	
	if session['role'] == 'admin':
		if request.method == 'GET':
			session['admin-email'] = request.args.get('adminemail')
			details = alchemist.getAdminDetails(session['admin-email'])
			
			if details is None:
				abort(500)
				
			return render_template('update-other-admin-account.html',username=session['name'], email=session['email'], details=details, updateRoute='update-admin-account')
		
	if request.method == 'POST':
		payload = request.form
		status = alchemist.updateAdminAccount(payload,session['admin-email'])		
		if status == False:
			flash('Unable to update admin account. Either the email provided is already linked to an account or there was a server error. Please, try again.', ERROR)
			return redirect(url_for('renderOtherUpdateAdminAccount', username=session['name'], email=session['email'], details=details, updateRoute='update-admin-account'))
			
		flash('Admin account was successfully updated.',SUCCESS)
		return redirect(url_for('renderAdmins'))
	else:
		abort(401)
		
@app.route('/remove-admin/')
def removeAdminUser():
	adminID = request.args.get('admin')
	admin = alchemist.getAdmin(adminID)
	status = alchemist.remove(admin.account)
	admins = alchemist.getAdmins(session['email'])
	if status == False:
		flash('Unable to remove admin. System Error.', ERROR)
		return redirect(url_for('renderAdmins', admins=admins, username=session['name'], email=session['email']))
	flash('Admin deleted.', SUCCESS)
	return redirect(url_for('renderAdmins', admins=admins, username=session['name'], email=session['email']))
		
		
@app.route('/new-manager-account',methods=['GET','POST'])
@login_required
def renderNewUserAccount():
	if session['role'] == 'admin':
		if request.method == 'GET':
			questions = alchemist.getQuestions()
			return render_template('new-manager-account.html',questions=questions, username=session['name'], email=session['email'],updateRoute='update-admin-account')
		
		if request.method == 'POST':
			payload = request.form
			account = alchemist.createAccount(payload)
			status = alchemist.save(account)
			
			if status == False:
				flash('Unable to create account. The email provided is already linked to an account.',ERROR)
				return redirect(url_for('renderNewUserAccount', username=session['name'], email=session['email']))
			
			flash('Account created.',SUCCESS)
			return redirect(url_for('renderAdmin', username=session['name'], email=session['email']))
	else:
		abort(401)
		

@app.route('/update-manager-account/',methods=['GET','POST'])
@login_required
def renderUpdateUserAccount():	
	if session['role'] == 'admin':
		if request.method == 'GET':
			session['manager-email'] = request.args.get('usremail')
			details = alchemist.getUserDetails(session['manager-email'])
			
			if details is None:
				abort(500)
				
			return render_template('update-manager-account.html',username=session['name'], email=session['email'], details=details,updateRoute='update-admin-account')
			
		if request.method == 'POST':
			payload = request.form
			status = alchemist.updateAccount(payload,session['manager-email'])
			
			if status == False:
				flash('Unable to update account. Either the email provided is already linked to an account or there was a server error. Please, try again.', ERROR)
				return redirect(url_for('renderUpdateUserAccount', username=session['name'], email=session['email'], details=details))
				
			flash('Account was successfully updated.',SUCCESS)
			return redirect(url_for('renderUsers'))
	else:
		abort(401)

@app.route('/new-employee', methods=['GET','POST'])
@login_required
def addNewEmployee():
	if request.method == 'GET':
		return render_template('new-employee.html', username=session['name'], email=session['email'], updateRoute='update-admin-account')
	
	if request.method == 'POST':
		payload = request.form
		employee = alchemist.createEmployee(payload)
		status = alchemist.save(employee)
		
		if status == False:
			flash('Unable to create employee. System Error.',ERROR)
			return redirect(url_for('addNewEmployee', username=session['name'], email=session['email']))
		
	flash('Employee Added: ' + employee.fname +' '+ employee.lname ,SUCCESS)
	return redirect(url_for('renderEmployees', username=session['name'], email=session['email']))

@app.route('/update-employee/',methods=['GET','POST'])
@login_required
def renderUpdateEmployee():	
	if session['role'] == 'admin':
		if request.method == 'GET':
			employeeID = request.args.get('employee')
			employee = alchemist.getEmployee(employeeID)
			
			if employee is None:
				abort(500)
				
			return render_template('update-employee.html',username=session['name'], email=session['email'], employee=employee,updateRoute='update-admin-account')
			
		if request.method == 'POST':
			payload = request.form
			status = alchemist.updateEmployee(payload)
			
			if status == False:
				flash('Unable to employee information. System Error', ERROR)
				return redirect(url_for('renderUpdateEmployee', username=session['name'], email=session['email']))
				
			flash('Employee information was successfully updated',SUCCESS)
			return redirect(url_for('renderEmployees',username=session['name'], email=session['email']))
	else:
		abort(401)	

@app.route('/awards')
@login_required
def renderAwards():
	if session['role'] == 'user':
		awards = alchemist.getAwards(session['email'])
		return render_template('user-awards-list.html', awards=awards, username=session['name'], email=session['email'])
	else:
		abort(401)
	
	
@app.route('/users')
@login_required
def renderUsers():
	if session['role'] == 'admin':
		users = alchemist.getUsers()
		return render_template('users-list.html', users=users, username=session['name'], email=session['email'],updateRoute='update-admin-account')
	else:
		abort(401)
	
	
@app.route('/remove-award/')
def removeAward():
	awardID = request.args.get('awd')
	award = alchemist.getAward(awardID)
	status = alchemist.remove(award)
	awards = alchemist.getAwards(session['email'])
	if status == False:
		flash('Unable to remove award. System Error.', ERROR)
		return redirect(url_for('renderAwards', awards=awards, username=session['name'], email=session['email']))
	flash('Award record deleted', SUCCESS)
	return redirect(url_for('renderAwards', awards=awards, username=session['name'], email=session['email']))
	
	
@app.route('/remove-user/')
def removeUser():
	userID = request.args.get('usr')
	user = alchemist.getUser(userID)
	users = alchemist.getUsers()
	
	sigFilename = user.signature
	sigFilename = sigFilename.replace('https://camelopardalis-assets.s3.amazonaws.com/',"")
	
	if alchemist.remove(user.account) == False:
		flash('Unable to remove user. System Error.', ERROR)
		return redirect(url_for('renderUsers', users=users, username=session['name'], email=session['email']))
	else:
		alchemist.deleteUserSig(sigFilename)

	awards = alchemist.getAllAwards()
	if awards is not None:
		for a in awards:
			if a.check_row() == True:
				alchemist.remove(a)
	
	flash('User deleted.', SUCCESS)
	return redirect(url_for('renderUsers', users=users, username=session['name'], email=session['email']))
		

@app.route('/award-types',methods=['GET','POST'])
@login_required
def renderAwardTypes():
	if session['role'] == 'admin':
		if request.method == 'GET':
			types = alchemist.getAwardTypes()
			return render_template('add-award-type.html',types=types,username=session['name'], email=session['email'],updateRoute='update-admin-account')
		
		if request.method == 'POST':
			if alchemist.addAwardType(request.form) == False:
				flash('Unable to create award type. Make sure your are not trying to create a duplicate type.',ERROR)
			else:
				flash('New award type created.',SUCCESS)
				
			return redirect(url_for('renderAwardTypes'))
	else:
		abort(401)

@app.route('/reports',methods=['GET','POST'])
@login_required
def renderReports():
	if session['role'] == 'admin':
		if request.method == 'GET':
			return render_template('reports.html',username=session['name'], email=session['email'],updateRoute='update-admin-account')
		
		if request.method == 'POST':
			if request.json:
				payload = request.get_json()
				
				if payload['report'] == '1':
					response = reporter.getAllAwards()
				elif payload['report'] == '2':
					response = reporter.getAwardsByManager()
				else:
					abort(400)
					
				return jsonify(response)
					
			else:
				abort(400)
	else:
		abort(401)


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
	
@app.route('/delete_s3/')
def delete_s3():
	file_name = request.args.get('file_name')
	print (file_name)
	alchemist.deleteUserSig(file_name);
	return json.dumps({'status': "success"})
	

	
@app.route('/password')
def renderPassword():
	return render_template('password.html')


@app.route('/latex', methods=['POST'])
@login_required
def renderPDF():
	payload = request.form
	print('HERE-----> {0}'.format(payload),file=sys.stderr)
	sys.stdout.flush()
	
	award = alchemist.createAward(payload, session['email'])
	status = alchemist.save(award)
			
	if status == False:
		abort(500)
				
	sigFile = session['email']
	sigFile = replace(sigFile,'@','_')
	sigFile = replace(sigFile,'.','_')
	sigFile += '_sig.png'
	

	alchemist.downloadUserSig(session['email'])
	
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
	'adminTitle':session['title'],
	'signature':sigFile,
	'granted':awardDateString}
	
	employeeAward = ah.Award(awdDetails,filename)
	pdf = employeeAward.genAward()
	

	if pdf is not None:
		if 'preview-btn' in payload:
			alchemist.remove(award)
			return send_file(pdf, as_attachment=True)
		elif 'email-btn' in payload:				
			sender = session['email']
			recipient = award.employee.email
			response = emailer.sendAward(sender,recipient,pdf)
			
			if response.status_code != 200 and response.status_code != 202:
				flash('An error occured and the email was not sent. Please, try again.',ERROR)
			else:
				flash('The award has been emailed.',SUCCESS)
				
			return redirect(url_for('renderCreate'))
	else:
		alchemist.remove(award)
		abort(500)

	
@app.route('/get-employee',methods=['POST'])
def getEmployees():
	print(type(request))
	sys.stdout.flush()
	if request.json:
		payload = request.get_json()
		employees = alchemist.getEmployees(payload)
		return jsonify(employees)
	else:
		abort(400)
		
@app.route('/employees-list')
def renderEmployees():
	if session['role'] == 'admin':
		employees = alchemist.getAllEmployees()
		return render_template('employees-list.html', employees=employees, username=session['name'], email=session['email'],updateRoute='update-admin-account')
	else:
		abort(401)

@app.route('/remove-employee/')
def removeEmployee():
	userID = request.args.get('employee')
	employee = alchemist.getEmployee(userID)
	employees = alchemist.getAllEmployees()
	
	if alchemist.remove(employee) == False:
		flash('Unable to remove employee. System Error.', ERROR)
		return redirect(url_for('renderEmployees', employees=employees, username=session['name'], email=session['email']))
	
	awards = alchemist.getAllAwards()
	if awards is not None:
		for a in awards:
			if a.check_row() == True:
				alchemist.remove(a)
	
	flash('Employee deleted.', SUCCESS)
	return redirect(url_for('renderEmployees', employees=employees, username=session['name'], email=session['email']))
		
@app.route('/get-password',methods=['POST'])
def getPassword():
	if request.json:
		payload = request.get_json()
		user = alchemist.findUser(payload['email'])
		
		if user['role'] == None:
			response = {'status':404,'message':'The email you provided is not linked to an account.'}
			return jsonify(response)
			
		if user['role'] == 'user':
			details = alchemist.getUserDetails(payload['email'])	
		elif user['role'] == 'admin':
			details = alchemist.getAdminDetails(payload['email'])
			
		if payload['reset-method'] == 'question':
			response = {'one':str(details['question1']), 'two':str(details['question2']),'status':200}
			return jsonify(response)
		elif payload['reset-method'] == 'email':
			code = alchemist.genVerificationCode(details['account'])
			
			if code is not None:
				response = emailer.sendPasswordReset(payload['email'],code)
			else:
				abort(500)
			
			return jsonify(response)
	else:
		abort(400)


@app.route('/reset-password', methods=['GET', 'POST'])
def resetPasswordViaEmail():
	if request.method == 'GET':
		return render_template('/reset-password.html')
		
	if request.method == 'POST':
		payload = request.form
		response = alchemist.resetPasswordByEmail(payload)
		
		if response['status'] != 200:
			flash(response['message'],ERROR)
			return redirect(url_for('resetPasswordViaEmail'))
		
		flash(response['message'],SUCCESS)		
		return redirect(url_for('renderLogin'))
		

@app.route('/reset-pass-via-question', methods=['POST'])
def resetPasswordViaQuestion():
	payload = request.form
	status = alchemist.resetPasswordByQuestions(payload)
	
	if status == False:
		abort(500)
	
	flash('Password was reset.',SUCCESS)
	return redirect(url_for('renderLogin'))
		
		
@app.route('/check-questions',methods=['POST'])
def checkQuestions():
	if request.json:
		payload = request.get_json()
		response = alchemist.verifyAnswers(payload)
		
		return jsonify(response)
	else:
		abort(400)

		
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




