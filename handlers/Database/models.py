from handlers.Database import database

employeeDepartment = database.db.Table(
'employee_department',
database.db.Column('employee_id',database.db.Integer, database.db.ForeignKey('employee.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False),
database.db.Column('department_id',database.db.Integer, database.db.ForeignKey('department.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False),
database.db.PrimaryKeyConstraint('employee_id', 'department_id'))

employeeAward = database.db.Table(
"employee_award",
database.db.Column('recepient', database.db.Integer, database.db.ForeignKey('employee.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False),
database.db.Column('award_id', database.db.Integer, database.db.ForeignKey('award.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False),
database.db.Column('recvd', database.db.DateTime,nullable=False),
database.db.Column('issued_by', database.db.Integer, database.db.ForeignKey('employee.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False),
database.db.PrimaryKeyConstraint('recepient', 'award_id','recvd'))
	
class Account (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	pword = database.db.Column(database.db.String(100), nullable=False)
	question1 = database.db.Column(database.db.Text, nullable=False)
	question2 = database.db.Column(database.db.Text, nullable=False)
	answer1 = database.db.Column(database.db.Text, nullable=False)
	answer2 = database.db.Column(database.db.Text, nullable=False)
	created = database.db.Column(database.db.DateTime, nullable=False)

	admin = database.db.relationship('Admin', backref='account',uselist=False,lazy='joined')
	employee = database.db.relationship('Employee', backref='account', uselist=False, lazy='joined')
	
	def __init__(self,pword,q1,q2,a1,a2,created):
		self.pword = pword
		self.question1 = q1
		self.question2 = q2
		self.answer1 = a1
		self.answer2 = a2
		self.created = created

	def __repr__(self):
		return '<Account %r>' % (self.id)
	
	
class Admin (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	account_id = database.db.Column(database.db.Integer, database.db.ForeignKey('account.id',ondelete='CASCADE',onupdate='RESTRICT'), nullable=False)
	fname = database.db.Column(database.db.String(32), nullable=False)
	lname = database.db.Column(database.db.String(32), nullable=False)
	email = database.db.Column(database.db.String(32), nullable=False)

	def __init__(self,account,fname,lname,email):
		self.account_id = account
		self.fname = fname
		self.lname = lname
		self.email = email

	def __repr__(self):
		return '<Admin %r>' % (self.fname + ' ' + self.lname)

    

class Employee (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	account_id = database.db.Column(database.db.Integer, database.db.ForeignKey('account.id',ondelete='CASCADE',onupdate='RESTRICT'), nullable=False)
	fname = database.db.Column(database.db.String(32), nullable=False)
	lname = database.db.Column(database.db.String(32), nullable=False)
	signature = database.db.Column(database.db.Text, nullable=False)
	email = database.db.Column(database.db.String(32), nullable=False, unique=True)

	creation = database.db.relationship('Award', backref='employee',lazy='dynamic')
	departments = database.db.relationship('Department',secondary=employeeDepartment,backref='employee')
	awards = database.db.relationship('Award',
		secondary=employeeAward,
		primaryjoin=(employeeAward.c.recepient == id),
		secondaryjoin=(employeeAward.c.issued_by == id),
		backref='recepient',
		foreign_keys=[id])

	def __init__(self,account,fname,lname,signature,email):
		self.account = account
		self.fname = fname
		self.lname = lname
		self.signature = signature
		self.email = email

	def __repr__(self):
		return '<Employee %r>' % (self.fname + ' ' + self.lname)

class Branch (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	name = database.db.Column(database.db.String(32), nullable=False)
	address = database.db.Column(database.db.String(100), nullable=False)
	city = database.db.Column(database.db.String(32), nullable=False)
	zip = database.db.Column(database.db.String(5), nullable=False)
	state_id = database.db.Column(database.db.Integer, database.db.ForeignKey('state.id',ondelete='CASCADE',onupdate='RESTRICT'), nullable=False)

	department = database.db.relationship('Department', backref='branch',lazy='dynamic')

	def __init__(self,name,address,city,zip,state):
		self.name = name
		self.address = address
		self.city = city
		self.zip = zip
		self.state_id = state

	def __repr__(self):
		return '<Branch %r>' % (self.name)

class State (database.db.Model):
	id = database.db.Column('id', database.db.Integer, primary_key=True)
	name = database.db.Column('name', database.db.String(2),nullable=False)

	branch = database.db.relationship('Branch', backref='state', lazy='joined')

	def __init__(self,name):
		self.name = name

	def __repr__(self):
		return '<State %r>' % (self.name)

class Department (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	branch_id = database.db.Column(database.db.Integer, database.db.ForeignKey('branch.id',ondelete='RESTRICT',onupdate='RESTRICT'),nullable=False)
	name = database.db.Column(database.db.String(32),nullable=False)

	def __init__(self,branchId,name):
		self.branch_id = branchId
		self.name = name

	def __repr__(self):
		return '<Department %r>' % (self.name)

class AwardType (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	name = database.db.Column(database.db.String(32),nullable=False)

	award = database.db.relationship('Award', backref='award_type', lazy='dynamic')
	archive = database.db.relationship('AwardArchive', backref='award_type',lazy='dynamic')

	def __init__(self,name):
		self.name = name

	def __repr__(self):
		return '<AwardType %r>' % (self.name)

class Award (database.db.Model):
	id = database.db.Column(database.db.Integer, primary_key=True)
	type_id = database.db.Column(database.db.Integer, database.db.ForeignKey('award_type.id',ondelete='RESTRICT',onupdate='RESTRICT'),nullable=False)
	creator = database.db.Column(database.db.Integer, database.db.ForeignKey('employee.id',ondelete='CASCADE',onupdate='RESTRICT'),nullable=False)
	title = database.db.Column(database.db.String(32),nullable=False)
	message = database.db.Column(database.db.String(255),nullable=False)
	background = database.db.Column(database.db.Text,nullable=False)

	#recepients = database.db.relationship('Employee',secondary=employeeAward,backref=database.db.backref('employees', lazy='dynamic'))
	
	def __init__(self,typeId,creator,title,message,background):
		self.type_id = typeId
		self.creator = creator
		self.title = title
		self.message = message
		self.background = background

	def __repr__(self):
		return '<Award %r>' % (self.title)

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
		return '<AwardArchive %r>' % (self.fname + ' ' + self.lname + ' ' + self.type_id)
