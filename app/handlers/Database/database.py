from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#consider making this a singleton class
class PostgresDatabase(object):
	def __init__(self,clsAccount,clsAdmin,clsEmployee,clsBranch,clsState,clsDepartment,clsAwardType,clsAward,clsAwardArchive):
		self.Account = clsAccount
		self.Admin = clsAdmin
		self.Employee = clsEmployee
		self.Branch = clsBranch
		self.State = clsState
		self.Department = clsDepartment
		self.AwardType = clsAwardType
		self.Award = clsAward
		self.AwardArchive = clsAwardArchive
			
	def createAccount(self,payload):
		fname = payload['firstName']
		lname = payload['lastName']
		email = payload['email']
		sign = payload['signature']
		pword = payload['password']
		quest1 = payload['security-question-1']
		quest2 = payload['security-question-2']
		answ1 = payload['security-answer-1']
		answ2 = payload['security-answer-1']
		created = datetime.now() #add this to the model by putting this arg in the Column(...,default=db.func.current_timestamp())
		
		account = self.Account(pword,quest1,quest2,answ1,answ2,created)
		employee = self.Employee(account,fname,lname,sign,email)
		
		db.session.add_all([account,employee])
		db.session.commit()