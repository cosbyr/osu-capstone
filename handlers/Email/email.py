from __future__ import print_function #debug
import sendgrid
import base64
from sendgrid.helpers.mail import *
import os,sys #sys debug

class Emailer(object):
	def __init__(self):
		self.key = os.environ['SENDGRID_API_KEY']
		
	def sendAward(self,sentBy,sendTo,image,sub='Your Award',text='Congrats!'):
		sg = sendgrid.SendGridAPIClient(apikey=self.key)
		sender = Email(sentBy)
		subject = sub
		recepient = Email(sendTo)
		content = Content("text/plain", text)
		
		with open(image,'rb') as file:
			data = file.read()

		encoded = base64.b64encode(data)

		attachment = Attachment()
		attachment.set_content(encoded)
		attachment.set_type("application/pdf")
		attachment.set_filename("award.pdf")
		attachment.set_disposition("attachment")
		attachment.set_content_id("Award")
		
		mail = Mail(sender,subject,recepient,content)
		mail.add_attachment(attachment)
		
		response = sg.client.mail.send.post(request_body=mail.get())
		return response
		
		
	def sendPasswordReset(self,sendTo,code):
		text = '''
		<p>You have elected to reset your password by email. Please, click the link below and enter the verification code.<p>
		<p>Verification Code: {0}</p>
		<p>link to deployed site goes here...'''.format(code) #change link to heroku url
		
		sg = sendgrid.SendGridAPIClient(apikey=self.key)
		sender = Email('root@admin.com') #may want to use more descriptive email... even though its fake
		subject = 'Employee Awards Password Reset' #should put title of app
		recepient = Email(sendTo)
		content = Content('text/html',text)
		
		mail = Mail(sender,subject,recepient,content)
		response = sg.client.mail.send.post(request_body=mail.get())
		
		return {'status':response.status_code,'message':'An email has been sent to ' + sendTo + '. Please, check your email and reset your password.'}
		
	
		