from __future__ import print_function #debug
import sendgrid
import base64
from sendgrid.helpers.mail import *
import os,sys #sys debug

class Emailer(object):
	def __init__(self):
		self.key = os.environ['SENDGRID_API_KEY']
		
	def sendAward(self,sentBy,sentTo,image,sub='Your Award',text='Congrats!'):
		sg = sendgrid.SendGridAPIClient(apikey=self.key)
		sender = Email(sentBy)
		subject = sub
		recepient = Email(sentTo)
		content = Content("text/plain", text)
		
		with open(image,'rb') as file:
			data = file.read()
			#f.close()

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
		
		
	
		