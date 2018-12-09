from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsFile,paperSubUtilsAttach
from flask import request, g, url_for, render_template, flash
import os

@app.route('/submit_paper/<int:tjyear>', methods=['GET','POST'])
def submit_paper(tjyear):
	error = ""
	displayStrings = paperSubUtils.display_strings()
	submitSuccess = True
	thisPaperInfo={}
	thisPaperInfoWithReview = {}
	thisPaperInfo['publishSequence'] = 0

	
	authorList = []
	authorInfo = {}
	managerInfo = {}
	expertInfo = {}
	noOfAuthors = 0

	if request.method == 'POST':
		#Input Paper Title, Authors's email, manager's email, and department information
		thisPaperInfo['paperTitle'] = request.form['paperTitle']
		if ( not thisPaperInfo['paperTitle']):
			thisPaperInfo['paperTitle'] = 'No PaperTitle'
			error+='Invalid paper title - '
			submitSuccess = False 

		for i in range(5):
			authorEmail = 'authorEmail'+str(i+1)
			tempEmail = request.form[authorEmail]
			if (paperSubUtils.validate_email(tempEmail) == False):
				flash('Invalid format: author email - '+str(i+1))
			else:
				noOfAuthors = noOfAuthors + 1
				authorInfo = {}
				authorInfo['email']  = tempEmail				
				authorInfo['name'] = paperSubUtils.parse_email_name(authorInfo['email']).capitalize()
				authorInfo['authorOrder'] = noOfAuthors

				authorList.append(authorInfo)



		managerInfo['email'] = request.form['managerEmail']
		if (paperSubUtils.validate_email(managerInfo['email']) == False):
			managerInfo['email'] = app.config['DEFAULT_INFO']['email']
			error+='Invalid format:	 manager email	- '
			submitSuccess = False
		else:
			
			managerInfo['name'] = paperSubUtils.parse_email_name(managerInfo['email']).capitalize()
			

		thisPaperInfo['department'] = request.form['department']
		#Input Paper Title, Authors's email, manager's email, and department information
		
		#Select the function area where the papers belong to in this TJ
		thisPaperInfo['tjSection'] = request.form['tjSection']
		#Select the function area where the papers belong to in this TJ

		thisPaperId = paperSubUtils.get_this_paper_id_for_submission(tjyear);
		thisPaperInfo['submissionSequence'] = thisPaperId

		#submit ZIP document
		fileForReview = request.files['zip2Bsubmitted']
		uploadResult = paperSubUtilsFile.upload_file("ZIP", True, False, False, thisPaperInfo,fileForReview,tjyear,thisPaperId)
		error += uploadResult['error']
		thisPaperInfo['zipURL'] = uploadResult['filesUrl']
		if submitSuccess:
			submitSuccess = uploadResult['needsToUpdate']
		#submit ZIP document
		
		#submit PDF document
		fileForReview = request.files['pdf2Bsubmitted']
		uploadResult = paperSubUtilsFile.upload_file("PDF", True, False, False, thisPaperInfo,fileForReview,tjyear,thisPaperId)
		error += uploadResult['error']
		thisPaperInfo['pdfURL'] = uploadResult['filesUrl']
		if submitSuccess:
			submitSuccess = uploadResult['needsToUpdate']
		#submit PDF document




		if submitSuccess:
			#Assign values for rows not required for submission
			expertInfo['email'] = app.config['DEFAULT_INFO']['email']
			expertInfo['name'] = app.config['DEFAULT_INFO']['name']
			
			thisPaperInfo['approvedStatus'] = False
			#Assign values for rows not required for submission
			
			#people info
			thisPaperInfoWithReview['authorList'] = authorList
			thisPaperInfoWithReview['managerInfo'] = managerInfo
			thisPaperInfoWithReview['expertInfo'] = expertInfo
			thisPaperInfoWithReview['noOfAuthors'] = noOfAuthors
			thisPaperInfoWithReview['paperInfo'] = thisPaperInfo
			#people Info
			

			
			#Write paper information Into Database
			paperSubUtils.database_operation_update_paper(thisPaperInfoWithReview,tjyear,thisPaperId,True)
			#Write paper information Into Database
			paperSubUtilsAttach.generate_review_form_spreadsheet(thisPaperInfoWithReview, tjyear, True, True)
			paperSubUtilsAttach.generate_review_form_spreadsheet(thisPaperInfoWithReview, tjyear, False, True)
			flash('Thank you for your submission!')
			return render_template('blank.html')
		else:
			error += "Please submit again~"
	return render_template('submitPaper.html', error=error,tjyear=tjyear, displayStrings = displayStrings)
