from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsFile
from flask import request, session, g, redirect, url_for, abort, render_template, flash
import copy


@app.route('/review_paper_info_enhanced/<int:tjyear>/<int:paperId>', methods=['GET','POST'])
def review_paper_info_enhanced(tjyear,paperId):
	error = ""

	if not (session.get('logged_in') or session.get('verified')):
		return redirect(url_for('verify_email',tjyear=tjyear,paperId=paperId,role='Author'))

	needsToUpdate = False
	displayStrings = paperSubUtils.display_strings()

	thisPaperInfoWithReview = paperSubUtils.get_paper_info_with_review(tjyear,paperId)

	thisPaperInfo = thisPaperInfoWithReview['paperInfo']
	managerReviewInfo = thisPaperInfoWithReview['managerReviewInfo']
	expertReviewInfo = thisPaperInfoWithReview['expertReviewInfo']

	tempThisPaperInfoWithReview = copy.deepcopy(thisPaperInfoWithReview)
	tempThisPaperInfo = tempThisPaperInfoWithReview['paperInfo']
	if request.method == 'POST':

		#Update the function area where the papers belong to in this TJ			
		tempThisPaperInfo['tjSection'] = int(request.form['tjSection'])
		if(paperSubUtils.information_updated(thisPaperInfo['tjSection'],tempThisPaperInfo['tjSection'])):
			flash('function area updated')
			needsToUpdate = True
		#Update the function area where the papers belong to in this TJ	

		#The parameters represent fileType, isFirstSub, isReviewer, isManager

		#submit ZIP document
		fileForReview = request.files['zip2Bsubmitted']
		uploadResult = paperSubUtilsFile.upload_file("ZIP", False, False, False, thisPaperInfo,fileForReview,tjyear,paperId)
		error += uploadResult['error']
		tempThisPaperInfo['zipURL'] = uploadResult['filesUrl']
		if not needsToUpdate:
			needsToUpdate = uploadResult['needsToUpdate']
		#submit ZIP document
		
		#submit PDF document
		fileForReview = request.files['pdf2Bsubmitted']
		uploadResult = paperSubUtilsFile.upload_file("PDF", False, False, False, thisPaperInfo,fileForReview,tjyear,paperId)
		error += uploadResult['error']
		tempThisPaperInfo['pdfURL'] = uploadResult['filesUrl']
		if not needsToUpdate:
			needsToUpdate = uploadResult['needsToUpdate']
		#submit PDF document

		if needsToUpdate:
			#Keep values for rows not required for review 
			tempThisPaperInfo['approvedStatus'] = thisPaperInfo['approvedStatus']
			tempThisPaperInfo['publishSequence'] = thisPaperInfo['publishSequence']
			#Update file names
			paperSubUtilsFile.update_file_name(tjyear, paperId, thisPaperInfo, tempThisPaperInfo)
			
			#update database info
			thisPaperInfoWithReview = copy.deepcopy(tempThisPaperInfoWithReview)
			thisPaperInfoWithReview = paperSubUtilsFile.unzip_uploaded_file_and_parse_info(tjyear, thisPaperInfoWithReview,True)	
			paperSubUtils.database_operation_update_paper(thisPaperInfoWithReview,tjyear,paperId,False)
			flash('The information of this paper is updated!')
			return render_template('blank.html')
		else:
			flash('The information of this paper is not updated!')
			return render_template('blank.html')
	return render_template('reviewPaperInfoEnhanced.html', error=error,tjyear=tjyear,paperId=paperId,\
	thisPaperInfo=thisPaperInfoWithReview,managerReviewInfo=managerReviewInfo, \
	expertReviewInfo=expertReviewInfo, displayStrings = displayStrings)	   

