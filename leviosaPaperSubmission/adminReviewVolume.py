from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsAttach,paperSubUtilsFile,paperSubUtilsLatex
import sqlite3, copy, datetime, os, zipfile,shutil
from datetime import timedelta
from flask import request, session, g, redirect, url_for,\
	abort, render_template, flash, send_from_directory
from openpyxl import Workbook
from openpyxl.chart import Reference
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.descriptors.excel import CellRange



@app.route('/TJvolume/<int:tjyear>',methods=['GET','POST'])
def admin_review_tj(tjyear):
	error = None
	if not session.get('logged_in'):
		return redirect(url_for('login'))

	timeStampData = datetime.datetime.now()+ timedelta(days=15)
	timeStamp = timeStampData.strftime('%Y/%m/%d-%H:%M:%S')


	displayStrings = paperSubUtils.display_strings()
	tjinfo = paperSubUtils.get_tj_info(tjyear)	
	if request.method == 'POST':
		paperInfoOfTheYear = paperSubUtils.get_all_paper_info_with_review(tjyear)

		update_database_volume(tjyear, paperInfoOfTheYear)		
		paperInfoOfTheYear = paperSubUtils.get_all_paper_info_with_review(tjyear)	

		if request.form.get('generateSpreadsheet') != None:
			paperSubUtilsAttach.generate_spreadsheet(paperInfoOfTheYear,tjyear)
		if request.form.get('downloadArcive') != None:
			paperSubUtilsAttach.download_archive(paperInfoOfTheYear,tjyear)	
		if (request.form.get('SendEmail') != None):
			send_emails(paperInfoOfTheYear, tjyear)
		if need_to_delete_submission(paperInfoOfTheYear, tjyear) == True:
			delete_submission (paperInfoOfTheYear, tjyear)
		if request.form.get('generateLatexScript') != None:
			paperSubUtilsLatex.generate_this_year_journal(paperInfoOfTheYear, tjyear)
	
		return redirect(url_for("admin_review_tj",tjyear=tjyear))

	paperInfoOfTheYear = paperSubUtils.get_all_paper_info_with_review(tjyear)			
	return render_template('adminReviewVolume.html', tjyear=tjyear,\
	paperInfoOfTheYear=paperInfoOfTheYear,displayStrings=displayStrings,error=error,\
	tjinfo = tjinfo, timeStamp=timeStamp)

def construct_email_content(index, paperInfoWithReview,tjyear):
	paperInfo = paperInfoWithReview['paperInfo']
	if request.form.get('SendEmail') == None:
		return None

	expertEmailCheck = int((request.form.getlist('expertEmailCheck'))[index])
	managerEmailCheck = int((request.form.getlist('managerEmailCheck'))[index])
	authorEmailCheck = int((request.form.getlist('authorEmailCheck'))[index])

	recipientRole =  request.form['recipientRole']
	includeReviewLink = (request.form.get('generateReviewLink') != None)

	attachment = None
	if ( recipientRole == 'Expert' ):
		if(expertEmailCheck ==0):
			return None
	elif ( recipientRole == 'Manager'):
		if(managerEmailCheck == 0):
			return None
	elif ( recipientRole == 'Author' ):
		if(authorEmailCheck == 0):
			return None


	if ( recipientRole == 'Expert' and includeReviewLink):
		if app.config['USINGOPTION'] == "attach":
			file = app.config['EMAIL_TEXT']['ExpertReviewInvitationAttach']
			link = "n/a"
			filenameStr = paperSubUtilsFile.form_file_name(tjyear,paperInfo['submissionSequence'], paperInfo)
			attachment = "-a " + filenameStr + '.pdf' + " -a " + filenameStr + 'expert_Review'+'.xlsx' + "\n"
		else:
			file = app.config['EMAIL_TEXT']['ExpertReviewInvitation']
			link = (app.config['MAIN_EDITOR_INFO'])['ServerAddress']+\
					url_for('submit_review_comments',tjyear=tjyear, \
					paperId=paperInfo['submissionSequence'],isManagerReview=False)
		
		subject = app.config['EMAIL_SUBJECT']['ExpertReviewInvitation']
		toEmail = paperInfoWithReview['expertInfo']['email']
		ccEmail = app.config['EDITORIAL_COMMITEE_INFO']['email']

	elif ( recipientRole == 'Manager'	and includeReviewLink):
		if app.config['USINGOPTION'] == "attach":
			file = app.config['EMAIL_TEXT']['ManagerReviewInvitationAttach']
			link = "n/a"
			filenameStr = paperSubUtilsFile.form_file_name(tjyear,paperInfo['submissionSequence'], paperInfo)
			attachment = "-a " + filenameStr + '.pdf' + " " + "-a " + filenameStr + 'manager_Review'+'.xlsx' + "\n"
		else:
			file = app.config['EMAIL_TEXT']['ManagerReviewInvitation']
			link = (app.config['MAIN_EDITOR_INFO'])['ServerAddress']+\
					url_for('submit_review_comments',tjyear=tjyear, \
					paperId=paperInfo['submissionSequence'],isManagerReview=True)

		subject = app.config['EMAIL_SUBJECT']['ManagerReviewInvitation']
		toEmail = paperInfoWithReview['managerInfo']['email']
		ccEmail = app.config['EDITORIAL_COMMITEE_INFO']['email']

	elif ( recipientRole == 'Author' and includeReviewLink):
		paperSubUtilsLatex.update_compressed_file_for_authors(paperInfoWithReview, tjyear)
		if app.config['USINGOPTION'] == "attach":
			file = app.config['EMAIL_TEXT']['AuthorPaperAcceptedAttach']
			link = "n/a"

			filenameStr = paperSubUtilsFile.form_file_name(tjyear,paperInfo['submissionSequence'], paperInfo)
			attachment = " "
			filename = filenameStr + "manager_Review" +".xlsx"
			attachment += form_author_attachment_string(filename)
			filename = filenameStr + "expert_Review" +".xlsx"
			attachment += form_author_attachment_string(filename)
			filename = filenameStr + "manager_Review" +".pdf"
			attachment += form_author_attachment_string(filename)
			filename = filenameStr + "expert_Review" +".pdf"
			attachment += form_author_attachment_string(filename)

			attachment += "-a " + filenameStr + '.zip'

		else:
			file = app.config['EMAIL_TEXT']['AuthorPaperAccepted']
			link = (app.config['MAIN_EDITOR_INFO'])['ServerAddress']+\
					url_for('review_paper_info',tjyear=tjyear, \
					paperId=paperInfo['submissionSequence'])
		
		subject = app.config['EMAIL_SUBJECT']['AuthorPaperAccepted']

		toEmail = paperInfoWithReview['authorList'][0]['email']
		ccEmail = app.config['EDITORIAL_COMMITEE_INFO']['email']
		index = 0
		for authorInfo in paperInfoWithReview['authorList']:
			if(index != 0):
				ccEmail += ','+authorInfo['email']
			index += 1


	elif ( recipientRole == 'Expert' ):
		file = app.config['EMAIL_TEXT']['ExpertGift']
		subject = app.config['EMAIL_SUBJECT']['ExpertGift']
		toEmail = paperInfoWithReview['expertInfo']['email']
		ccEmail = app.config['EDITORIAL_COMMITEE_INFO']['email']
		link = "n/a"

	elif ( recipientRole == 'Author'):
		file = app.config['EMAIL_TEXT']['AuthorGift']
		subject = app.config['EMAIL_SUBJECT']['AuthorGift']
		toEmail = paperInfoWithReview['authorList'][0]['email']
		ccEmail = app.config['EDITORIAL_COMMITEE_INFO']['email']
		for authorInfo in paperInfoWithReview['authorList']:
			if(index != 0):
				ccEmail += ','+authorInfo['email']
			index += 1

		link = "n/a"

	else:
		return None
	with open(file, 'r') as contentTemp:
		content = contentTemp.read()
	if (request.form.get('reminder') != None):
		content = "Reminder ..."+"   "+"\n\n\n\n\n\n" + content
	area = ""
	for a in app.config['RESEARCHING_AREAS']:
		area = area + a +'\n'
	
	content = content.replace('$recipient', paperSubUtils.parse_email_name(toEmail).capitalize())
	content = content.replace('$tjyear', str(tjyear))
	content = content.replace('$link', link)
	content = content.replace('$seat', (app.config['MAIN_EDITOR_INFO'])['Seat'])
	content = content.replace('$deadline', request.form['deadline'])
	content = content.replace('$papertitle', paperInfo['paperTitle'])
	content = content.replace('$authorname',( paperInfoWithReview['authorList'][0]['name']).capitalize())
	content = content.replace('$name',(app.config['MAIN_EDITOR_INFO'])['EditorName'])
	content = content.replace('$committee',(app.config['EDITORIAL_COMMITEE_INFO']['name']))
	content = content.replace('$journal',(app.config['EDITORIAL_COMMITEE_INFO']['journal']))
	content = content.replace('$area',area)
	subject = subject.replace('$tjyear',str(tjyear))
	subject = subject.replace('$papertitle',paperInfo['paperTitle'])

	return {'toRecipient':toEmail,'ccRecipient':ccEmail, 'subject':subject, \
	'attachment':attachment,'emailContent':content}

def form_author_attachment_string(filename):
	file = os.path.join(app.config['UPLOAD_FOLDER'],filename)
	if (os.path.isfile(file)):
		return "-a " +filename + " "
	else:
		return " "

def create_send_email_script(emailInfo):
	scriptContent = "_to_list="
	scriptContent += emailInfo['toRecipient']+"\n"
	scriptContent += "_cc_list="
	scriptContent += emailInfo['ccRecipient']+"\n"
	#scriptContent += "_from_list="+(app.config['MAIN_EDITOR_INFO'])['EmailAddress']+"\n"
	scriptContent += "context="
	scriptContent += "\""+emailInfo['emailContent']+"\""+"\n"
	scriptContent += "echo" + " " +"$context |" 
	scriptContent += "mutt -s " + emailInfo['subject'] + " " +	 "$_to_list -c $_cc_list"
	if emailInfo['attachment'] != None:
		scriptContent += " " + emailInfo['attachment']+'\n\n\n\n\n'

	return scriptContent

def send_emails(paperInfoOfTheYear, tjyear):
	includeReviewLink = (request.form.get('generateReviewLink') != None)
	SendEmail = (request.form.get('SendEmail') != None)
	recipientRole = request.form['recipientRole']

	scriptName = str(tjyear)+"-"+"sendEmailScript_"+recipientRole+'_Link'+str(includeReviewLink)+datetime.datetime.now().strftime('%Y-%m-%d%H_%M_%S')
	f= open(os.path.join(app.config['UPLOAD_FOLDER'], scriptName),"w+")
	
	index = 0
	for paperInfo in paperInfoOfTheYear:
		#tempPaperInfo = paperInfo['paperInfo']
		emailInfo = construct_email_content(index, paperInfo, tjyear)
		if emailInfo != None:
			scriptContent = create_send_email_script(emailInfo);
			f.write(scriptContent)
			flash("Email Script Generated for index %d"%index)
		index = index +1
	f.close();
	return

def need_to_delete_submission(paperInfoOfTheYear, tjyear):
	toBeDeleted = request.form.getlist('deleteSubmission')
	index = 0
	for paperInfo in paperInfoOfTheYear:
		if int(toBeDeleted[index]) == 1:
			return True
 	index = index +1
	return False

def delete_submission (paperInfoOfTheYear, tjyear):
	toBeDeleted = request.form.getlist('deleteSubmission')
	indexToBeDeleted = []
	index = 0
	for paperInfo in paperInfoOfTheYear:
		tempPaperInfo = paperInfo['paperInfo']
		
		if  int(toBeDeleted[index]) == 1:
			indexToBeDeleted.append( tempPaperInfo['submissionSequence'])
			paperSubUtilsFile.delete_file(tjyear,tempPaperInfo['submissionSequence'], tempPaperInfo)
			flash('You can only delete one submission one time')
			break;
		index = index +1
	for paperId in indexToBeDeleted:
		paperSubUtils.database_operation_delete_paper(tjyear,paperId)
	return

def update_database_volume(tjyear, paperInfoOfTheYear):
	managerEmail = request.form.getlist('managerEmail')
	expertEmail = request.form.getlist('expertEmail')
	approvedStatus = request.form.getlist('approvedStatus')

	publishSequence = request.form.getlist('pubId')
	tjSection = request.form.getlist('functionArea')

	index = 0


	for paperInfoWithReview in paperInfoOfTheYear:
		tempPaperInfo = paperInfoWithReview['paperInfo']
		tempManagerReviewInfo = paperInfoWithReview['managerReviewInfo']
		tempExpertReviewInfo = paperInfoWithReview['expertReviewInfo']
		tempManagerInfo = paperInfoWithReview['managerInfo']
		tempExpertInfo = paperInfoWithReview['expertInfo']
		
		updatedPaperInfoWithReview = {}
		tempUpdatedPaperInfo = copy.deepcopy(tempPaperInfo)
		tempUpdatedManagerReviewInfo = copy.deepcopy(tempManagerReviewInfo)
		tempUpdatedExpertReviewInfo = copy.deepcopy(tempExpertReviewInfo)
		tempUpdatedManagerInfo = copy.deepcopy(tempManagerInfo)
		tempUpdatedExpertInfo = copy.deepcopy(tempExpertInfo)

		tempUpdatedManagerInfo['email'] = managerEmail[index]
		tempUpdatedExpertInfo['email']= expertEmail[index]

		tempUpdatedPaperInfo['approvedStatus'] = approvedStatus[index]
		tempUpdatedPaperInfo['publishSequence'] = int(publishSequence[index])
		tempUpdatedPaperInfo['tjSection'] = int(tjSection[index])	



		if paperSubUtils.information_updated(tempUpdatedPaperInfo['tjSection'], \
			tempPaperInfo['tjSection'])\
		or paperSubUtils.information_updated(tempUpdatedPaperInfo['publishSequence'], \
			tempPaperInfo['publishSequence']):
			tempUpdatedPaperInfo = paperSubUtilsFile.update_file_name(tjyear, \
				tempPaperInfo['submissionSequence'], tempPaperInfo, tempUpdatedPaperInfo)
			tempUpdatedManagerReviewInfo = paperSubUtilsFile.update_review_file_name(tjyear, \
				tempPaperInfo['submissionSequence'], tempPaperInfo, tempUpdatedPaperInfo,tempUpdatedManagerReviewInfo, True)

			tempUpdatedExpertReviewInfo = paperSubUtilsFile.update_review_file_name(tjyear, \
				tempPaperInfo['submissionSequence'], tempPaperInfo, tempUpdatedPaperInfo,\
				tempUpdatedExpertReviewInfo, False)
			
		updatedPaperInfoWithReview['paperInfo'] = tempUpdatedPaperInfo  
		updatedPaperInfoWithReview['managerReviewInfo'] = tempUpdatedManagerReviewInfo
 		updatedPaperInfoWithReview['expertReviewInfo'] = tempUpdatedExpertReviewInfo
		updatedPaperInfoWithReview['managerInfo'] = tempUpdatedManagerInfo
		updatedPaperInfoWithReview['expertInfo'] = tempUpdatedExpertInfo
		updatedPaperInfoWithReview['authorList'] = paperInfoWithReview['authorList']
		updatedPaperInfoWithReview['noOfAuthors'] = paperInfoWithReview['noOfAuthors']
		paperSubUtils.database_operation_update_paper(updatedPaperInfoWithReview,tjyear,\
			tempUpdatedPaperInfo['submissionSequence'],False)
		paperSubUtilsAttach.generate_review_form_spreadsheet(updatedPaperInfoWithReview, tjyear, True)
		paperSubUtilsAttach.generate_review_form_spreadsheet(updatedPaperInfoWithReview, tjyear, False)


		index = index+1


	return


 
	