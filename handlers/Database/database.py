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
	def __init__(self,clsQuestion,clsAccount,clsAdmin,clsManager,clsAwardType,clsAward,clsAwardArchive,clsAwardBackground,clsAwardTheme,clsEmployee):
		self.Question = clsQuestion
		self.Account = clsAccount
		self.Admin = clsAdmin
		self.Manager = clsManager
		self.AwardType = clsAwardType
		self.Award = clsAward
		self.AwardArchive = clsAwardArchive
		self.AwardBackground = clsAwardBackground
		self.AwardTheme = clsAwardTheme
		self.Employee = clsEmployee

	def getAwardThemes(self):
		themes = {}
		results = db.session.query(self.AwardTheme).all()
		
		for r in results:
			themes[r.id] = r.theme
			
		return themes
		
	def getAwardBackgrounds(self):
		backgrounds = {}
		results = db.session.query(self.AwardBackground).all()
		
		for r in results:
			backgrounds[r.id] = r.filename
			
		return backgrounds
	
	def getAwardTypes(self):
		types = {}
		results = db.session.query(self.AwardType).all()
		
		for r in results:
			types[r.id] = r.name
			
		return types

	def getQuestions(self):
		questions = {}
		results = db.session.query(self.Question).all()
		
		for r in results:
			questions[r.id] = r.prompt
			
		return questions
	
	def downloadUserSig(self,email):
		bucket = os.environ.get('S3_BUCKET_NAME')
		
		filename = replace(email,'@','_')
		filename = replace(filename,'.','_')
		filename += '_sig.png'
		
		client = boto3.client('s3')
		
		try:
			client.download_file(bucket, filename, filename)
		except ClientError as e:
			print(e.response['Error']['Message'],file=sys.stderr)
			return None
		except IOError as e:
			print(e,file=sys.stderr)
			return None
		return True
		
	def getUserDetails(self,email):
		user = self.Manager.query.filter_by(email=email).first()
		
		self.downloadUserSig(email)
		
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
		'signature':user.signature}
		
		return details
		
			
	def login(self,payload):
		email = payload['userName']
		pword = payload['password']
		type = payload['account-type']
		
		if type == 'admin':
			admin = self.Admin.query.filter_by(email=email).first()
			if admin is None:
				return False, None #we should indicate why the login failed on the login page
			else:
				return argon2.verify(pword,admin.account.pword), admin.account
				
		if type == 'user':
			user = self.Manager.query.filter_by(email=email).first()
			if user is None:
				return False, None #we should indicate why the login failed on the login page
			else:
				return argon2.verify(pword,user.account.pword), user.account
				
		return False
		
		
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
		created = datetime.now()
		
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
		user.signature = payload['signature'] 
		print(user.signature,file=sys.stderr)
		try:
			db.session.commit()
		except IntegrityError:
			return False
			
		return True
		
	def createAward(self,payload,email):
		creator = self.Manager.query.filter_by(email=email).first()
		awardType = self.AwardType.query.get(payload['type'])
		recvdBy = self.Employee.query.filter_by(email=payload['recpEmail']).first()
		
		if recvdBy is None:
			return False, None
			
		creatorId = creator.id
		typeId = awardType.id
		message = payload['message']
		issuedOn = datetime.now()
		recepient = recvdBy.id
		background = int(payload['background'])
		theme = int(payload['theme'])
		
		
		award = self.Award(creatorId,typeId,message,issuedOn,recepient,background,theme)

		try:
			db.session.add(award)
			db.session.commit()
		except IntegrityError as e:
			print(e,file=sys.stderr)
			sys.stdout.flush()
			return False, None
			
		return True, award
	
	def getAccount(self,id):
		return self.Account.query.get(id)
		
	def setAuthenticated(self,account,val):		
		try:
			account.authenticated = val
			db.session.add(account)
			db.session.commit()
		except IntegrityError as e:
			print(e,file=sys.stderr)
			sys.stdout.flush()
			return False,None
			
		return True,account
	
	def getEmployees(self,lname):
		employees = {}
		results = self.Employee.query.filter(self.Employee.lname.ilike('%' + lname + '%')).all()
		
		if results is None:
			return False, None
			
		for r in results:
			employees[r.id] = [r.fname,r.lname,r.email]
			
		return True,employees
		
		
	'''
	def createRootAdmin(self):
		pword = argon2.using(rounds=4).hash('root')
		quest1 = 1
		quest2 = 2
		answ1 = 'root'
		answ2 = 'root'
		email = 'root@admin.com'
		created = datetime.now()
		
		account = self.Account(pword,quest1,quest2,answ1,answ2,created)
		admin = self.Admin(account,email)
		
		db.session.add(account)
		db.session.add(admin)
		db.session.commit()
	'''
