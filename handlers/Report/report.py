from handlers.Database import models

class Reporter(object):
	def __init__(self,database):
		self.db = database
		
	def getAwardsByType(self):
		awards = {}
		results = self.db.session.query(models.Award).all()
		
		if results is not None:
			for r in results:
				type = str(r.award_type).replace('AwardType ','').replace('<','').replace('>','')
				if type not in awards:
					awards[type] = 1
				else:
					awards[type] += 1
			
			awards['status'] = 200
		else:
			awards['status'] = 404 
			
		return awards
		