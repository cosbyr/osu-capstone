from handlers.Database import models

class Reporter(object):
	def __init__(self,database):
		self.db = database
		
	def getAwardsByType(self):
		awards = {}
		results = self.db.session.query(models.Award).all()
		
		if results is not None:
			for r in results:
				if r.award_type.name not in awards:
					awards[r.award_type.name] = 1
				else:
					awards[r.award_type.name] += 1
			
			awards['status'] = 200
		else:
			awards['status'] = 404 
			
		return awards
		
	def getAwardsByManager(self):
		#{id:{name:full name,type name: count[,type name: count,...]}}
		awards = {'types':[]}
		types = []
		resultAwards = self.db.session.query(models.Award).all()
		resultTypes = self.db.session.query(models.AwardType).all()
		
		for r in resultTypes:
			types.append(r.name)
			awards['types'].append(r.name)
			
		if resultAwards is not None:
			for r in resultAwards:
				if r.manager.id not in awards:
					awards[r.manager.id] = {'name':'{0} {1}'.format(r.manager.fname,r.manager.lname)}
					
					for t in types:
						awards[r.manager.id][t] = 0
						
					awards[r.manager.id][r.award_type.name] += 1
				else:
					awards[r.manager.id][r.award_type.name] += 1
						
			awards['status'] = 200
		else:
			awards['status'] = 404 
			
		return awards
					
		