from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsFile
from flask import request, session, g, redirect, url_for, abort, render_template, flash
import copy


@app.route('/review_paper_info/<int:tjyear>/<int:paperId>', methods=['GET','POST'])
def review_paper_info(tjyear,paperId):
	error = ""

	if not (session.get('logged_in') or session.get('verified')):
		return redirect(url_for('verify_email',tjyear=tjyear,paperId=paperId,role='Author'))

	needsToUpdate = False
	displayStrings = paperSubUtils.display_strings()
	flash("Review paper info")
	thisPaperInfoWithReview = paperSubUtils.get_paper_info_with_review(tjyear,paperId)
	flash(thisPaperInfoWithReview)
	thisPaperInfo = thisPaperInfoWithReview['paperInfo']
	managerReviewInfo = thisPaperInfoWithReview['managerReviewInfo']
	expertReviewInfo = thisPaperInfoWithReview['expertReviewInfo']

	tempThisPaperInfoWithReview = copy.deepcopy(thisPaperInfoWithReview)
	tempThisPaperInfo = tempThisPaperInfoWithReview['paperInfo']
	if request.method == 'POST':
		#Update Paper Title, Authors' email, managers' email, and department information
		tempThisPaperInfo['paperTitle'] = request.form['paperTitle']
		if ( not tempThisPaperInfo['paperTitle'] ):
			flash('Please update again: invalid paper title')
		elif(paperSubUtils.information_updated(thisPaperInfo['paperTitle'],tempThisPaperInfo['paperTitle'])):
			flash('Paper title updated')
			needsToUpdate = True			

		for i in range(thisPaperInfoWithReview['noOfAuthors']):
			authorEmail = 'authorEmail'+str(i+1)
			tempEmail = request.form[authorEmail]
			if (paperSubUtils.validate_email(tempEmail) == False):
				flash('Invalid format: author email - '+str(i+1))
			elif(paperSubUtils.information_updated(tempEmail,thisPaperInfoWithReview['authorList'][i]['email'])):
				
				authorInfo = {}
				authorInfo['email']  = tempEmail				
				authorInfo['name'] = paperSubUtils.parse_email_name(authorInfo['email']).capitalize()
				authorInfo['authorOrder'] = i + 1
				needsToUpdate = True	
				tempThisPaperInfoWithReview['authorList'][i] = authorInfo
				i = i+1
		
				




		#Update the function area where the papers belong to in this TJ			
		tempThisPaperInfo['tjSection'] = int(request.form['tjSection'])
		if(paperSubUtils.information_updated(thisPaperInfo['tjSection'],tempThisPaperInfo['tjSection'])):
			flash('function area updated')
			needsToUpdate = True
		#Update the function area where the papers belong to in this TJ	

		#submit latex document
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
			thisPaperInfoWithReview = copy.deepcopy(tempThisPaperInfoWithReview)
			paperSubUtils.database_operation_update_paper(tempThisPaperInfoWithReview,tjyear,paperId,False)
			flash('The information of this paper is updated!')
			return render_template('blank.html')
		else:
			flash('The information of this paper is not updated!')
			return render_template('blank.html')
	return render_template('reviewPaperInfo.html', error=error,tjyear=tjyear,paperId=paperId,\
	thisPaperInfo=thisPaperInfoWithReview,managerReviewInfo=managerReviewInfo, \
	expertReviewInfo=expertReviewInfo, displayStrings = displayStrings)	   

