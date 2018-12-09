import urllib
import ssl
import re
from leviosaPaperSubmission import app
from flask import flash
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class personInfo(HTMLParser):
	def reset(self):
		self.email = []

		self.name=""
		self.isPersonName=False
		self.isDivInfo = False
		self.isDivInfoTag = False
		self.isEmailInfo = False
		HTMLParser.reset(self)

	def handle_starttag(self, tag, attrs):
		if tag == 'div':
			for k,v in attrs:
				if k == app.config['INFO_TAG_DIV_ATTR']['k'] and v == app.config['INFO_TAG_DIV_ATTR']['v']:
					self.isDivInfoTag=True
					#flash(app.config['INFO_TAG_DIV_ATTR']['v'])
				elif k == app.config['INFO_DIV_ATTR']['k'] and v == app.config['INFO_DIV_ATTR']['v']:
					self.isDivInfo=True
					#flash(app.config['INFO_DIV_ATTR']['v'])
				elif k == app.config['PERSON_DIV_ATTR']['k'] and v == app.config['PERSON_DIV_ATTR']['v']:
					self.isPersonName=True

	def handle_data(self, text):
		if self.isDivInfoTag == True and self.isDivInfo == False:
			#flash(text)
			if text == app.config['INFO_2B_EXTRACTED']['email']:
				#flash('email tag found')
				self.isEmailInfo = True
		elif self.isDivInfoTag == True and self.isDivInfo == True:
			#flash(text)
			if self.isEmailInfo == True:
				#flash('email saved')
				self.email.append(text)
				self.isEmailInfo = False

		if self.isPersonName == True:
			self.name = text	
	def handle_endtag(self, tag):
		if tag == 'div':
			if self.isDivInfo == True:
				self.isDivInfoTag = False
				self.isDivInfo = False
			self.isPersonName=False
 
	def get_person_name(self):
		name = re.search('^([a-zA-Z]+)\s([a-zA-Z]+)',self.name).group(2)+' '+re.search('^([a-zA-Z]+)\s([a-zA-Z]+)',self.name).group(1)
		return name
	def get_person_email(self):
		return self.email


class managerProfile(HTMLParser):
	def reset(self):
		self.managerURL = ""
		self.isManagerURL = False
		self.isURLFound = False
		HTMLParser.reset(self)

	# handle <div>
	def handle_starttag(self, tag, attrs):
		if tag == 'div':
			for k,v in attrs:
				if k == app.config['MANAGER_DIV_ATTR']['k'] and v == app.config['MANAGER_DIV_ATTR']['v']:
					self.isManagerURL=True
		if tag == 'a':
			if self.isManagerURL == True:
				self.isURLFound = True
				for k,v in attrs:
					if k == 'href':
						self.managerURL=app.config['ONLINE_INFO_ADDRESS'][0]+v
	def handle_endtag(self,tag):
		if tag == 'div':
			self.isManagerURL=False
		if tag == 'a':
			self.isURLFound = False
	
	def get_manager_URL(self):
		return self.managerURL


		
def get_manager_info(emailAddress):
 
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
 
	regexString = '(.*)@(.*)'

	
	linkInfo = app.config['ONLINE_INFO_ADDRESS'][0]+\
		app.config['ONLINE_INFO_ADDRESS'][1]+\
		re.search(regexString,emailAddress).group(1)+\
		app.config['ONLINE_INFO_ADDRESS'][2]+\
		re.search(regexString,emailAddress).group(2)


	f = urllib.urlopen(linkInfo,context=ctx)

	managerProfObj = managerProfile()
	managerProfObj.feed(f.read())
	managerURL = managerProfObj.get_manager_URL()
	

	f2 = urllib.urlopen(managerURL,context=ctx)
	managerObj = personInfo()
	managerObj.feed(f2.read())
	managerName=managerObj.get_person_name()
	managerEmail = managerObj.get_person_email()

	return {'name':managerName, 'email':managerEmail[0]}
	


	


