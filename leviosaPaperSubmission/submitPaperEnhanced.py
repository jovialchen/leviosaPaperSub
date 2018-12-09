from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsFile,paperSubUtilsAttach
from flask import request, g, url_for, render_template, flash
import os

@app.route('/submit_paper_enhanced/<int:tjyear>', methods=['GET','POST'])
def submit_paper_enhanced(tjyear):
	error = ""
	displayStrings = paperSubUtils.display_strings()
	submitSuccess = True
	thisPaperInfo={}

	thisPaperInfoWithReview =  {}
	
	if request.method == 'POST':
		#Select the function area where the papers belong to in this TJ
		thisPaperInfo['tjSection'] = request.form['tjSection']
		#Select the function area where the papers belong to in this TJ
		
		thisPaperId = paperSubUtils.get_this_paper_id_for_submission(tjyear);
		thisPaperInfo['submissionSequence'] = thisPaperId	
		thisPaperInfo['publishSequence'] = 0
		thisPaperInfoWithReview['paperInfo'] = thisPaperInfo

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
		#Input Paper Title, Authors's email, manager's email, and department information




		if submitSuccess:
			thisPaperInfoWithReview = paperSubUtilsFile.unzip_uploaded_file_and_parse_info(tjyear, thisPaperInfoWithReview,True)	
			

			
			#Write paper information Into Database
			paperSubUtils.database_operation_update_paper(thisPaperInfoWithReview,tjyear,thisPaperId,True)
			#Write paper information Into Database
			paperSubUtilsAttach.generate_review_form_spreadsheet(thisPaperInfoWithReview, tjyear, True, True)
			paperSubUtilsAttach.generate_review_form_spreadsheet(thisPaperInfoWithReview, tjyear, False, True)
			flash('Thank you for your submission!')
			return render_template('blank.html')
		else:
			error += "Please submit again~"
	return render_template('submitPaperEnhanced.html', error=error,tjyear=tjyear, displayStrings = displayStrings)
