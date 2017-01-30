from __future__ import print_function #debug
import sys #debug
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from passlib.hash import argon2

db = SQLAlchemy()

#consider making this a singleton class
class PostgresDatabase(object):
	def __init__(self,clsQuestion,clsAccount,clsAdmin,clsManager,clsAwardType,clsAward,clsAwardArchive):
		self.Account = clsAccount
		self.Admin = clsAdmin
		self.Manager = clsManager
		self.AwardType = clsAwardType
		self.Award = clsAward
		self.AwardArchive = clsAwardArchive
			
	def login(self,payload):
		email = payload['userName']
		pword = payload['password']
		
		user = self.Manager.query.filter_by(email=email).first()
		
		if user is None:
			return False
		
		return argon2.verify(pword,user.account.pword)
		
		
	def createAccount(self,payload):
		fname = payload['firstName']
		lname = payload['lastName']
		email = payload['email']
		sign = payload['signature']
		pword = argon2.using(rounds=4).hash(payload['password'])
		quest1 = int(payload['security-question-1'])
		quest2 = int(payload['security-question-2'])
		answ1 = payload['security-answer-1']
		answ2 = payload['security-answer-1']
		created = datetime.now() #add this to the model by putting this arg in the Column(...,default=db.func.current_timestamp())
		title = 'boss' #this field needs to be added to the new account form
		
		account = self.Account(pword,quest1,quest2,answ1,answ2,created)
		manager = self.Manager(account,title,fname,lname,sign,email)
		
		try:
			db.session.add_all([account,manager])
			db.session.commit()
		except IntegrityError:
			return False
		
		return True
		