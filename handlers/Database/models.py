from handlers.Database import database
			
class Account (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	pword = database.db.Column(database.db.String(100), nullable=False)
	q1_id = database.db.Column(database.db.Integer, database.db.ForeignKey('question.id',ondelete='RESTRICT',onupdate='RESTRICT'), nullable=False)
	q2_id = database.db.Column(database.db.Integer, database.db.ForeignKey('question.id',ondelete='RESTRICT',onupdate='RESTRICT'), nullable=False)
	answer1 = database.db.Column(database.db.Text, nullable=False)
	answer2 = database.db.Column(database.db.Text, nullable=False)
	created = database.db.Column(database.db.DateTime, nullable=False)

	admin = database.db.relationship('Admin', backref='account',uselist=False,lazy='joined')
	manager = database.db.relationship('Manager', backref='account', uselist=False, lazy='joined')
	q1 = database.db.relationship('Question',foreign_keys=[q1_id])
	q2 = database.db.relationship('Question',foreign_keys=[q2_id])
	
	def __init__(self,pword,q1,q2,a1,a2,created):
		self.pword = pword
		self.q1_id = q1
		self.q2_id = q2
		self.answer1 = a1
		self.answer2 = a2
		self.created = created

	def __repr__(self):
		return '<Account {0}>'.format(self.id)

class Question(database.db.Model):
		id = database.db.Column(database.db.Integer, primary_key=True)
		prompt = database.db.Column(database.db.String(255), nullable=False)
		
		#account = database.db.relationship('Account',backref='questions',lazy='joined',foreign_keys=[id],primaryjoin=(Account.id == id))
		#account = database.db.relationship('Account',backref='questions',lazy='joined',foreign_keys=[Account.q1_id,Account.q2_id])
		
		def __init__(self,prompt):
			self.prompt = prompt
			
		def __repr__(self):
			return '{0}'.format(self.prompt)		
	
class Admin (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	account_id = database.db.Column(database.db.Integer, database.db.ForeignKey('account.id',ondelete='CASCADE',onupdate='RESTRICT'), nullable=False)
	email = database.db.Column(database.db.String(32), nullable=False, unique=True)
	
	def __init__(self,account,email):
		self.account = account
		self.email = email
		
	def __repr__(self):
		return '<Admin {0}>'.format(self.account_id)

    

class Manager (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	account_id = database.db.Column(database.db.Integer, database.db.ForeignKey('account.id',ondelete='CASCADE',onupdate='RESTRICT'), nullable=False)
	title = database.db.Column(database.db.String(32), nullable=False)
	fname = database.db.Column(database.db.String(32), nullable=False)
	lname = database.db.Column(database.db.String(32), nullable=False)
	signature = database.db.Column(database.db.Text, nullable=False)
	email = database.db.Column(database.db.String(32), nullable=False, unique=True)

	created = database.db.relationship('Award', backref='manager',lazy='dynamic')

	def __init__(self,account,title,fname,lname,signature,email):
		self.account = account
		self.title = title
		self.fname = fname
		self.lname = lname
		self.signature = signature
		self.email = email

	def __repr__(self):
		return '<Manager {0}>'.format(self.fname + ' ' + self.lname)


class AwardType (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	name = database.db.Column(database.db.String(32),nullable=False)

	award = database.db.relationship('Award', backref='award_type', lazy='dynamic')
	archive = database.db.relationship('AwardArchive', backref='award_type',lazy='dynamic')

	def __init__(self,name):
		self.name = name

	def __repr__(self):
		return '<AwardType {0}>'.format(self.name)

class Award (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	creator = database.db.Column(database.db.Integer, database.db.ForeignKey('manager.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False)
	type_id = database.db.Column(database.db.Integer, database.db.ForeignKey('award_type.id',ondelete='RESTRICT',onupdate='RESTRICT'),nullable=False)
	message = database.db.Column(database.db.String(255),nullable=False)
	recepient_fname = database.db.Column(database.db.String(32),nullable=False)
	recepient_lname = database.db.Column(database.db.String(32),nullable=False)
	background = database.db.Column(database.db.Text,nullable=False)
	issuedOn = database.db.Column(database.db.DateTime,nullable=False)
	
	def __init__(self,creator,typeId,message,fname,lname,background,issuedOn):
		self.creator = creator
		self.type_id = typeId
		self.message = message
		self.recepient_fname = fname
		self.recepient_lname = fname
		self.background = background
		self.issuedOn = issuedOn

	def __repr__(self):
		return '<Award {0} {1} {2}>'.format(self.creator,self.type_id,self.message)

class AwardArchive (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	fname = database.db.Column(database.db.String(32),nullable=False)
	lname = database.db.Column(database.db.String(32),nullable=False)
	type_id = database.db.Column(database.db.Integer, database.db.ForeignKey('award_type.id',ondelete='RESTRICT',onupdate='RESTRICT'),nullable=False)
	recvd = database.db.Column(database.db.DateTime,nullable=False)

	def __init__(self,fname,lname,typeId,recvd):
		self.fname = fname
		self.lname = lname
		self.type_id = typeId
		self.recvd = recvd

	def __repr__(self):
		return '<AwardArchive {0} {1} {2}>'.format(self.fname,self.lname,self.type_id)
