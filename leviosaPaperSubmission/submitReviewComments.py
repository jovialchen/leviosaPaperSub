from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsFile,paperSubUtilsAttach
import sqlite3,os, datetime
from flask import request, session, g, redirect, url_for, abort, render_template, flash,send_from_directory
from werkzeug import secure_filename
import os,copy

@app.route('/submit_review_comments/<int:tjyear>/<int:paperId>/<int:isManagerReview>', methods=['GET','POST'])
def submit_review_comments(tjyear,paperId,isManagerReview):
	error = ""
	displayStrings = paperSubUtils.display_strings()

	thisPaperInfoWithReview = paperSubUtils.get_paper_info_with_review(tjyear,paperId)
	thisPaperInfo = thisPaperInfoWithReview['paperInfo']
	lastUpdatedReviewInfo = paperSubUtils.get_review_info(isManagerReview,paperId,tjyear)


	reviewInfo = copy.deepcopy(lastUpdatedReviewInfo)
	if(isManagerReview):
		reviewerInfo = "manager_review"
		reviewerEmail = thisPaperInfoWithReview['managerInfo']['email']
		role = 'Manager'
	else:
		reviewerInfo = "expert_review"
		reviewerEmail = thisPaperInfoWithReview['expertInfo']['email']
		role = 'Expert'

	if not session.get('logged_in') and not session.get('verified'):
		return redirect(url_for('verify_email',tjyear=tjyear,paperId=paperId,role=role))

	submitSuccess = True

	if request.method != 'POST':	
		flash("Please help complete the "+reviewerInfo+" for  - "+thisPaperInfo['paperTitle'])	

	if request.method == 'POST':
		#Construct Reviewer Items
		index = 0 
		for eachReviewItem in reviewInfo['itemList']:
			eachReviewItem['reviewItemGrade'] = int(request.form.getlist('reviewItemName')[index])
			index = index + 1
		#Construct Reviewer Items

	
		#Read the review result from reviewer
		reviewInfo['Overall'] = request.form['Overall']	   
		#Read the review result from reviewer

		#Construct Reviewer Comments
		index = 0 

		for eachReviewQuestion in reviewInfo['questionList']:
			eachReviewQuestion['answer'] = request.form.getlist('answer')[index]
			index = index + 1
		#Construct Reviewer Comments

		 
		#Upload file with comments
		file = request.files['xlsx2Bsubmitted']
		if app.config['USINGOPTION'] == "attach":
			uploadResult = paperSubUtilsFile.upload_file("XLSX", False, True, isManagerReview, thisPaperInfo,\
							file,tjyear,paperId, reviewInfo)
			if uploadResult['needsToUpdate'] == True:
				reviewInfo = paperSubUtilsAttach.extract_info_from_review_spreadsheet(thisPaperInfoWithReview, tjyear, isManagerReview, reviewInfo)

				reviewInfo['excelURL'] = uploadResult['filesUrl']
		file = request.files['pdf2Bsubmitted']
		uploadResult = paperSubUtilsFile.upload_file("PDF", False, True, isManagerReview, thisPaperInfo,\
							file,tjyear,paperId, reviewInfo)
				
		reviewInfo['commentedVersionURL'] = uploadResult['filesUrl']
		#Upload file with comments
		reviewInfo['reviewSubmitted'] = True
		paperSubUtils.database_operation_update_paper_review_info(reviewInfo,paperId,tjyear,\
			isManagerReview)

		flash('Thanks for your support to '+app.config['EDITORIAL_COMMITEE_INFO']['journal']+' '+str(tjyear))
		return render_template('blank.html')

	return render_template('submitReviewComments.html', error=error,tjyear=tjyear,\
	paperId=paperId,isManagerReview=isManagerReview,thisPaperInfo=thisPaperInfoWithReview,\
	reviewerEmail=reviewerEmail,displayStrings=displayStrings, lastUpdatedReviewInfo\
	=lastUpdatedReviewInfo)