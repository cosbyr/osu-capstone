from __future__ import print_function #debug
import sys,os #sys debug
import logging
import json, boto3
from handlers.LaTex import award as ah
from handlers.Database import database
from handlers.Database import models
from flask import Flask, render_template, send_file, abort, request, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin


app = Flask('app',template_folder='./templates',static_folder='./static')
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

postgres = database.PostgresDatabase(
models.Question,
models.Account,
models.Admin,
models.Manager,
models.AwardType,
models.Award,
models.AwardArchive)

@app.route('/')
def renderIndex():
	return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def renderLogin():
	if request.method == 'GET':
		return render_template('login.html')
	
	if request.method == 'POST':
		payload = request.form
		status = postgres.login(payload)
		
		if status == False:
			return render_template('login.html',status=status)
		
		return redirect(url_for('renderUser'))

@app.route('/admin')
def renderAdmin():
	return render_template('admin.html')

@app.route('/user')
def renderUser():
	return render_template('user.html')

@app.route('/create')
def renderCreate():
	return render_template('create.html')

@app.route('/history')
def renderHistory():
	return render_template('history.html')

@app.route('/new-account',methods=['GET','POST'])
def renderNewAccount():
	if request.method == 'GET':
		return render_template('new-account.html')
	
	if request.method == 'POST':
		payload = request.form
		logging.warning(payload)
		status = postgres.createAccount(payload)
		
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
	'admin2':'Jane Smith',
	'adminTitle1':'Supervisor',
	'adminTitle2':'Head of Department'}
	
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




