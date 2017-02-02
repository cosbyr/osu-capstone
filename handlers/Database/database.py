from __future__ import print_function #debug
import os,sys #sys debug
import boto3
from string import replace
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from passlib.hash import argon2
from botocore.exceptions import ClientError
from boto3.s3.transfer import S3Transfer

db = SQLAlchemy()

#consider making this a singleton class
class PostgresDatabase(object):
	def __init__(self,clsQuestion,clsAccount,clsAdmin,clsManager,clsAwardType,clsAward,clsAwardArchive):
		self.Question = clsQuestion
		self.Account = clsAccount
		self.Admin = clsAdmin
		self.Manager = clsManager
		self.AwardType = clsAwardType
		self.Award = clsAward
		self.AwardArchive = clsAwardArchive
	
	def getQuestions(self):
		questions = {}
		results = db.session.query(self.Question).all()
		
		for r in results:
			questions[r.id] = r.prompt
			
		return questions
		
	def getUserDetails(self,email):
		'''
		bucket = os.environ.get('S3_BUCKET_NAME')
		accessKey = os.environ.get('AWS_ACCESS_KEY_ID')
		secretKey = os.environ.get('AWS_SECRET_ACCESS_KEY')
		
		transfer = S3Transfer(boto3.client('s3', 'us-west-1', aws_access_key_id=accessKey, aws_secret_access_key=secretKey))
		
		filename = replace(email,'@','_')
		filename = replace(filename,'.','_')
		filename += '_sig.png'
		
		try:
			transfer.download_file(bucket, filename, '/static/images/sig.png')
		except ClientError as e:
			print(e.response['Error']['Message'],file=sys.stderr)
			return None
		except IOError as e:
			print('Here: {0}'.format(e))
			return None
		'''
		user = self.Manager.query.filter_by(email=email).first()
		
		details = {
		'id':user.id,
		'fname':user.fname,
		'lname':user.lname,
		'email':user.email,
		'title':user.title,
		'question1':user.account.q1,
		'question2':user.account.q2,
		'answer1':user.account.answer1,
		'answer2':user.account.answer2,
		'signature':'/static/images/ex-sig.png'}#placeholder
		
		return details
		
			
	def login(self,payload):
		email = payload['userName']
		pword = payload['password']
		type = payload['account-type']
		
		#if the user is a manager, then get their first and last name an return that along with the boolean
		#indicating whether their password was verified or not. store this string in the session['name']
		user = self.Manager.query.filter_by(email=email).first()
		
		#we should indicate why the login failed on the login page
		if user is None:
			return False
		
		return argon2.verify(pword,user.account.pword)
		
		
	def createAccount(self,payload):
		fname = payload['firstName']
		lname = payload['lastName']
		email = payload['email']
		title = payload['jobTitle']
		sign = payload['signature']
		pword = argon2.using(rounds=4).hash(payload['password'])
		quest1 = int(payload['security-question-1'])
		quest2 = int(payload['security-question-2'])
		answ1 = payload['security-answer-1']
		answ2 = payload['security-answer-2']
		created = datetime.now() #add this to the model by putting this arg in the Column(...,default=db.func.current_timestamp())
		
		account = self.Account(pword,quest1,quest2,answ1,answ2,created)
		manager = self.Manager(account,title,fname,lname,sign,email)
		
		try:
			db.session.add_all([account,manager])
			db.session.commit()
		except IntegrityError:
			return False
		
		return True
		
	def updateAccount(self,payload,email):
		user = self.Manager.query.filter_by(email=email).first()
		
		user.fname = payload['firstName']
		user.lname = payload['lastName']
		user.email = payload['email']
		user.title = payload['jobTitle']
		#user.signature = payload['signature'] 
		
		try:
			db.session.commit()
		except IntegrityError:
			return False
			
		return True
		