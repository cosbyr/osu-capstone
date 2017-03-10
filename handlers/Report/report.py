from __future__ import print_function #debug
import sys #debug
from datetime import datetime

from handlers.Database import models

class Reporter(object):
	def __init__(self,database):
		self.db = database
	
	
	def getAllAwards(self):
		TYPE_INDEX = 0
		COUNT_INDEX = 1
		
		response = {}
		
		#awards = self.db.session.query(models.Award).all()
		#get award count grouped by type
		awardCount = self.db.session \
		.query(models.AwardType.name,self.db.func.count(models.Award.type_id)) \
		.select_from(models.AwardType) \
		.join(models.Award,models.AwardType.id==models.Award.type_id) \
		.group_by(models.AwardType.name).all()
		
		#get awards grouped by date
		awardDates = self.db.session \
		.query(models.AwardType.name,models.Award.issuedOn,self.db.func.count(models.Award.type_id)) \
		.select_from(models.AwardType) \
		.join(models.Award,models.AwardType.id==models.Award.type_id) \
		.group_by(models.AwardType.name,models.Award.issuedOn) \
		.order_by(models.Award.issuedOn).all()
		
		if awardCount is not None and awardDates is not None:
			for a in awardCount:
				response[a[TYPE_INDEX]] = a[COUNT_INDEX]
			
			response['dates'] = awardDates
			response['status'] = 200
		else:
			response['status'] = 404
		
		return response
	
	
	def getAwardsByEmployee(self):
		ID = 0
		FNAME = 1
		LNAME = 2
		EMAIL = 3
		TYPE = 4
		COUNT = 5
		
		#get award types
		types = self.db.session.query(models.AwardType).all()
		
		#get award type count by employee
		awards = self.db.session \
		.query(models.Award.recipient,models.Employee.fname,models.Employee.lname, models.Employee.email, models.AwardType.name,self.db.func.count(models.Award.type_id)) \
		.select_from(models.Award) \
		.join(models.Employee,models.Award.recipient==models.Employee.id) \
		.join(models.AwardType,models.AwardType.id==models.Award.type_id) \
		.group_by(models.Award.recipient,models.Employee.fname,models.Employee.lname, models.Employee.email, models.AwardType.name).all()
		
		#get award grouped by date and type
		awardDates = self.db.session \
		.query(models.Employee.fname,models.Employee.lname,models.AwardType.name,models.Award.issuedOn,self.db.func.count(models.Award.type_id)) \
		.select_from(models.Employee) \
		.join(models.Award,models.Employee.id==models.Award.recipient) \
		.join(models.AwardType,models.Award.type_id==models.AwardType.id) \
		.group_by(models.Employee.fname,models.Employee.lname,models.AwardType.name,models.Award.issuedOn) \
		.order_by(models.Employee.lname,models.Award.issuedOn).all()
		
		if types is not None and awards is not None:
			#init data dict
			data = {'employees':[['Name', 'Email']],'awards':[['Employee'] + [t.name for t in types] + [{'role':'annotation'}]],'dates':awardDates}
			
			history = []
			for a in awards:			
				if a[ID] not in history:
					name = '{0} {1}'.format(a[FNAME],a[LNAME])
					data['employees'].append([name, a[EMAIL]])
					data['awards'].append([name] + [0] * len(types) + [''])
					typeIndex = data['awards'][0].index(a[TYPE])
					data['awards'][-1][typeIndex] = a[COUNT]
					history.append(a[ID])
				else:
					userIndex = history.index(a[ID]) + 1
					typeIndex = data['awards'][0].index(a[TYPE])
					data['awards'][userIndex][typeIndex] = a[COUNT]
			
			data['status'] = 200
		else:
			data['status'] = 404
			
		return data
	
	
	def getAwardsByManager(self):
		ID = 0
		FNAME = 1
		LNAME = 2
		TITLE = 3
		TYPE = 4
		COUNT = 5
		
		#get award types
		types = self.db.session.query(models.AwardType).all()
		
		#get award type count by manager
		awards = self.db.session \
		.query(models.Award.creator,models.Manager.fname,models.Manager.lname,models.Manager.title,models.AwardType.name,self.db.func.count(models.Award.type_id)) \
		.select_from(models.Award) \
		.join(models.Manager,models.Award.creator==models.Manager.id) \
		.join(models.AwardType,models.AwardType.id==models.Award.type_id) \
		.group_by(models.Award.creator,models.Manager.fname,models.Manager.lname,models.Manager.title,models.AwardType.name).all()
		
		#get award grouped by date and type
		awardDates = self.db.session \
		.query(models.Manager.fname,models.Manager.lname,models.AwardType.name,models.Award.issuedOn,self.db.func.count(models.Award.type_id)) \
		.select_from(models.Manager) \
		.join(models.Award,models.Manager.id==models.Award.creator) \
		.join(models.AwardType,models.Award.type_id==models.AwardType.id) \
		.group_by(models.Manager.fname,models.Manager.lname,models.AwardType.name,models.Award.issuedOn) \
		.order_by(models.Manager.lname,models.Award.issuedOn).all()
		
		
		if types is not None and awards is not None:
			#init data dict
			data = {'managers':[['Name','Title']],'awards':[['Manager'] + [t.name for t in types] + [{'role':'annotation'}]],'dates':awardDates}

			history = []
			for a in awards:			
				if a[ID] not in history:
					name = '{0} {1}'.format(a[FNAME],a[LNAME])
					data['managers'].append([name,a[TITLE]])
					data['awards'].append([name] + [0] * len(types) + [''])
					typeIndex = data['awards'][0].index(a[TYPE])
					data['awards'][-1][typeIndex] = a[COUNT]
					history.append(a[ID])
				else:
					userIndex = history.index(a[ID]) + 1
					typeIndex = data['awards'][0].index(a[TYPE])
					data['awards'][userIndex][typeIndex] = a[COUNT]
			
			data['status'] = 200
		else:
			data['status'] = 404
			
		return data
		
			
			
			
			
			
			
			
			