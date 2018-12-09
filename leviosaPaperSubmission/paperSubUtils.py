from leviosaPaperSubmission import app,paperSubUtilsFile
from flask import request, g, url_for, render_template, flash
import re, os, operator,copy

def database_operation_update_paper(thisPaperInfoWithReview,tjyear,thisPaperId,newPaper):
	thisPaperInfo = thisPaperInfoWithReview['paperInfo']
	if newPaper == False:
		g.db.execute('delete from submissionList where (tjyear,submissionSequence) = (?,?)',[tjyear,thisPaperId])
		g.db.execute('delete from personInfo where (tjyear,submissionSequence) = (?,?)',[tjyear,thisPaperId])
		database_operation_update_paper_review_info(thisPaperInfoWithReview['managerReviewInfo'],\
			thisPaperId,tjyear,True)
		database_operation_update_paper_review_info(thisPaperInfoWithReview['expertReviewInfo'],\
			thisPaperId,tjyear,False)
	else:
		#initialize review information in the database
		reviewInfoManager = init_review_comments(thisPaperInfoWithReview, tjyear,True)
		reviewInfoExpert = init_review_comments(thisPaperInfoWithReview,tjyear, False)
		database_operation_update_paper_review_info(reviewInfoManager,thisPaperId,tjyear,True, True)
		database_operation_update_paper_review_info(reviewInfoExpert,thisPaperId,tjyear,False, True)
		#initialize review information in the database

		#Update maximum paper Id
		g.db.execute('delete from noOfTotalSubmittedPaper where tjyear =(?)', [tjyear])
		g.db.execute('insert into noOfTotalSubmittedPaper (tjyear,maxPaperId) values (?,?)', [tjyear,thisPaperId])
		#Update maximum paper Id

	#Add paper information into submission list
	g.db.execute('insert into submissionList (paperTitle,department,\
		zipURL,pdfURL,\
		tjSection, approvedStatus,\
		submissionSequence,publishSequence,tjyear) \
		values (?,?,?,?,?,?,?,?,?)',[thisPaperInfo['paperTitle'],thisPaperInfo['department'],\
		thisPaperInfo['zipURL'],	thisPaperInfo['pdfURL'], \
		thisPaperInfo['tjSection'],thisPaperInfo['approvedStatus'],\
		thisPaperId,thisPaperInfo['publishSequence'],tjyear])
	#Add paper information into submission list
	
	#Update Author Info
	for authorInfo in thisPaperInfoWithReview['authorList']:
		g.db.execute('insert into personInfo (submissionSequence, authorOrder, \
			role, name, email, tjyear) values (?,?,?,?,?,?)',\
			[thisPaperId, authorInfo['authorOrder'],'Author',\
			authorInfo['name'],authorInfo['email'],tjyear])
	#Update Author Info	

	#Update Manager Info
	g.db.execute('insert into personInfo (submissionSequence, authorOrder,\
		role, name, email, tjyear) values (?,?,?,?,?,?)',\
		[thisPaperId, 0, 'Manager',\
		thisPaperInfoWithReview['managerInfo']['name'],thisPaperInfoWithReview['managerInfo']['email'],tjyear])
	#Update Manager Info	

	#Update Expert Info
	g.db.execute('insert into personInfo (submissionSequence, authorOrder, \
		role, name, email, tjyear) values (?,?,?,?,?,?)',\
		[thisPaperId, 0, 'Expert',\
		thisPaperInfoWithReview['expertInfo']['name'],thisPaperInfoWithReview['expertInfo']['email'],tjyear])
	#Update Expert Info	

	g.db.execute('insert into noOfAuthors (submissionSequence, numberOfAuthors, tjyear) values (?,?,?)',\
		[thisPaperId, thisPaperInfoWithReview['noOfAuthors'],tjyear])
	

	g.db.commit()
	return

def database_operation_update_paper_review_info(reviewInfo,paperId,tjyear,isManagerReview, isInit = False):
	if isInit == False:
		g.db.execute('delete from reviewContent where (tjyear,submissionSequence,isManagerReview) = (?,?,?)',\
			[tjyear,paperId,isManagerReview])
		g.db.execute('delete from reviewComments where (tjyear,submissionSequence,isManagerReview) = (?,?,?)',\
			[tjyear,paperId,isManagerReview])
		g.db.execute('delete from reviewItem where (tjyear,submissionSequence,isManagerReview) = (?,?,?)',\
			[tjyear,paperId,isManagerReview])
	g.db.execute('insert into reviewContent (reviewSubmitted,Overall,commentedVersionURL, excelURL,\
		isManagerReview, submissionSequence,tjyear) values (?,?,?,?,?,?,?)',\
		[reviewInfo['reviewSubmitted'],\
		reviewInfo['Overall'],\
		reviewInfo['commentedVersionURL'],reviewInfo['excelURL'],isManagerReview,paperId,tjyear])
		

	for eachReviewQuestion in reviewInfo['questionList']:
		g.db.execute('insert into reviewComments (tjyear,submissionSequence,isManagerReview,question,answer) values\
			(?,?,?,?,?)', [tjyear,paperId,isManagerReview,eachReviewQuestion['question'],eachReviewQuestion['answer']])
	for eachReviewItem in reviewInfo['itemList']:
		g.db.execute('insert into reviewItem (tjyear, submissionSequence, isManagerReview, reviewItemName, \
			reviewItemGrade) values\
			(?,?,?,?,?)', [tjyear,paperId, isManagerReview,eachReviewItem['reviewItemName'],eachReviewItem['reviewItemGrade']])
	g.db.commit()
	return

def database_operation_delete_paper(tjyear,paperId):
		g.db.execute('delete from reviewContent where (tjyear,submissionSequence) = (?,?)',\
		[tjyear,paperId])
		g.db.execute('delete from submissionList where (tjyear,submissionSequence) = (?,?)',[tjyear,paperId])
		g.db.execute('delete from personInfo where (tjyear,submissionSequence) = (?,?)',[tjyear,paperId])
		g.db.execute('delete from reviewComments where (tjyear,submissionSequence) = (?,?)',[tjyear,paperId])
		g.db.execute('delete from reviewItem where (tjyear,submissionSequence) = (?,?)',[tjyear,paperId])
		g.db.commit()
		return

def database_operation_update_tjinfo(tjyear, infotype):
		g.db.execute('delete from tjinfo where (tjyear,typeinfo) = (?,?)',[tjyear,infotype])
		if infotype == 'archive':
			filename = str(tjyear)+'.zip'
		elif infotype == 'spreadsheet':
			filename = str(tjyear)+'.xlsx'
		file = os.path.join(app.config['UPLOAD_FOLDER'],filename)
		URL = app.config['UPLOAD_URL_PREFIX']+filename
		if(os.path.isfile(file)):
			g.db.execute('insert into tjinfo (tjyear,typeinfo, URL) values (?,?,?)',[tjyear,infotype,URL])
		else:
			g.db.execute('insert into tjinfo (tjyear,typeinfo, URL) values (?,?,?)',[tjyear,infotype,'n/a'])
		g.db.commit()
		return

def init_review_comments(paperInfoWithReview, tjyear, isManagerReview):
	reviewInfo = {}
	questionList = []
	itemList = []

	reviewInfo['reviewSubmitted'] = False

	reviewInfo['Overall'] = 0
	reviewInfo['commentedVersionURL'] = "n/a"

	for question in app.config['REVIEW_COMMENTS_QUESTIONS']:
		eachReviewQuestion = {}
		eachReviewQuestion['question'] = question
		eachReviewQuestion['answer'] = "n/a"

		questionList.append(eachReviewQuestion)


	questionList.sort(key=operator.itemgetter('question'))
	reviewInfo['questionList'] = questionList

	for item in app.config['REVIEW_ITEM']:
		eachReviewItem = {}
		eachReviewItem['reviewItemName'] = item
		eachReviewItem['reviewItemGrade'] = 0

		itemList.append(eachReviewItem)

	itemList.sort(key=operator.itemgetter('reviewItemName'))
	reviewInfo['itemList'] = itemList	
	
	filenameStr = paperSubUtilsFile.form_file_name(tjyear,paperInfoWithReview['paperInfo']['submissionSequence'],paperInfoWithReview['paperInfo'])
	if isManagerReview == True:
		filenameStr = filenameStr+'manager_Review'
	else:
		filenameStr = filenameStr+'expert_Review'
	filename = filenameStr+'.xlsx'

	reviewInfo['excelURL'] = app.config['UPLOAD_URL_PREFIX']+filename


		
	return reviewInfo	

def get_review_info(isManagerReview,paperId,tjyear):
	cur = g.db.execute('select * from reviewContent where tjyear =(?) \
		and submissionSequence = (?) and isManagerReview  = (?)', \
		[tjyear,paperId,isManagerReview])
  
	reviewInfo = [dict(reviewSubmitted=row[1], \
		Overall=row[2],commentedVersionURL=row[3],excelURL=row[4])\
		for row in cur.fetchall()]

	cur2 = g.db.execute('select question,answer from reviewComments where tjyear=(?) \
		and submissionSequence=(?) and isManagerReview  = (?)', \
		[tjyear,paperId, isManagerReview])

	questionList = [dict(question=row[0],answer=row[1]) for row in cur2.fetchall()]
	questionList.sort(key=operator.itemgetter('question'))
	reviewInfo[0]['questionList'] = questionList

	cur3 = g.db.execute('select reviewItemName,reviewItemGrade from reviewItem where tjyear=(?) \
		and submissionSequence=(?) and isManagerReview  = (?)', \
		[tjyear,paperId, isManagerReview])
	itemList = [dict(reviewItemName=row[0],reviewItemGrade=row[1]) for row in cur3.fetchall()]
	itemList.sort(key=operator.itemgetter('reviewItemName'))
	reviewInfo[0]['itemList'] = itemList
	return reviewInfo[0]	 

def get_this_paper_id_for_submission(tjyear):
	#Assign the paper ID, the paper ID is incremented automatically for paper submitted for this year
	cur = g.db.execute('select maxPaperId from noOfTotalSubmittedPaper where tjyear = (?)', [tjyear])
	paperIds = cur.fetchall()
	if(not paperIds):
		   beforeThisPaperId = 0
	else:
		for paperIdInc in paperIds:
			beforeThisPaperId=paperIdInc[0]
			break;

	thisPaperId = beforeThisPaperId+1
	#Assign the paper ID, the paper ID is incremented automatically for paper submitted for this year

	return thisPaperId

def get_no_of_authors(tjyear,paperId):
	cur = g.db.execute('select numberOfAuthors from noOfAuthors where tjyear = (?) and submissionSequence = (?)', [tjyear,paperId])
	allNoOfAuthors = cur.fetchall()
	if(not allNoOfAuthors):
		   allNoOfAuthors = 0
	else:
		for noOfAuthors in allNoOfAuthors:
			return noOfAuthors[0]




def get_paper_info(tjyear,paperId):
	cur = g.db.execute('select * from submissionList where tjyear =(?) \
		and submissionSequence = (?)', [tjyear,paperId])
  
	paperInfo = [dict(paperTitle=row[1], department=row[2],\
	pdfURL=row[3],\
	zipURL=row[4],\
	tjSection=row[5],approvedStatus=row[6], submissionSequence =row[7], publishSequence=row[8],\
	tjyear=row[9])\
	for row in cur.fetchall()]

	return paperInfo[0]

def get_all_paper_info(tjyear):
	cur = g.db.execute('select * from submissionList where tjyear = (?)',\
		[tjyear])
  
	paperInfo = [dict(paperTitle=row[1], department=row[2],\
	pdfURL=row[3],\
	zipURL=row[4],\
	tjSection=row[5],approvedStatus=row[6], submissionSequence =row[7], publishSequence=row[8],\
	tjyear=row[9])\
	for row in cur.fetchall()]

	return paperInfo
def get_tj_info(tjyear):
	tjInfo = {}

	cur = g.db.execute('select URL from tjinfo where (tjyear, typeinfo) = (?,?)',\
		[tjyear,'archive'])
	allArchiveInfo = cur.fetchall()
	if(not allArchiveInfo):
		tjInfo['archiveURL'] = "n/a"
	else:
		for archiveURL in allArchiveInfo:
			tjInfo['archiveURL'] = archiveURL[0]
	
	cur = g.db.execute('select URL from tjinfo where (tjyear, typeinfo) = (?,?)',\
		[tjyear,'spreadsheet'])
	allSpreadSheetInfo = cur.fetchall()
	if(not allSpreadSheetInfo):
		tjInfo['spreadsheetURL'] = "n/a"
	else:
		for spreadsheetURL in allSpreadSheetInfo:
			tjInfo['spreadsheetURL'] = spreadsheetURL[0]
	return tjInfo

def get_paper_info_with_review(tjyear,paperId):
	thisPaperInfo = get_paper_info(tjyear, paperId)

	thisPaperInfoWithReview = {}
	paperId = thisPaperInfo['submissionSequence']

	thisPaperInfoWithReview['paperInfo'] = thisPaperInfo
	thisPaperInfoWithReview['managerReviewInfo'] = get_review_info(True,paperId,tjyear)
	thisPaperInfoWithReview['expertReviewInfo'] = get_review_info(False,paperId,tjyear)
	thisPaperPersonInfo = get_person_list(tjyear,paperId)
	thisPaperInfoWithReview['authorList']=thisPaperPersonInfo['authorList']
	thisPaperInfoWithReview['expertInfo']=thisPaperPersonInfo['expertInfo']
	thisPaperInfoWithReview['managerInfo']=thisPaperPersonInfo['managerInfo']
	thisPaperInfoWithReview['noOfAuthors']=get_no_of_authors(tjyear,paperId)

	return thisPaperInfoWithReview

def get_person_list(tjyear,paperId):
	authorList = []
	cur = g.db.execute('select * from personInfo where (tjyear,submissionSequence) = (?,?)',[tjyear,paperId])
	thisPaperPersonInfo = [dict(authorOrder=row[2],role=row[3],name=row[4],email=row[5]) \
		for row in cur.fetchall()]

	for personInfo in thisPaperPersonInfo:
		if personInfo['role'] == 'Expert':
			expertInfo = copy.deepcopy(personInfo)
		elif personInfo['role'] == 'Manager':
			managerInfo = copy.deepcopy(personInfo)
		else:
			authorList.append(personInfo)
	authorList.sort(key=operator.itemgetter('authorOrder'))

	return{'expertInfo':expertInfo, 'managerInfo':managerInfo, 'authorList':authorList}


def get_all_paper_info_with_review(tjyear):
	allPaperInfo = get_all_paper_info(tjyear)

	allPaperInfoWithReview = []
	for thisPaperInfo in allPaperInfo:
		thisPaperInfoWithReview = {}
		paperId = thisPaperInfo['submissionSequence']

		thisPaperInfoWithReview['paperInfo'] = thisPaperInfo
		thisPaperInfoWithReview['managerReviewInfo'] = get_review_info(True,paperId,tjyear)
		thisPaperInfoWithReview['expertReviewInfo'] = get_review_info(False,paperId,tjyear)
		thisPaperPersonInfo = get_person_list(tjyear,paperId)
		thisPaperInfoWithReview['authorList']=thisPaperPersonInfo['authorList']
		thisPaperInfoWithReview['expertInfo']=thisPaperPersonInfo['expertInfo']
		thisPaperInfoWithReview['managerInfo']=thisPaperPersonInfo['managerInfo']
		thisPaperInfoWithReview['submissionSequence'] = thisPaperInfo['submissionSequence']
		thisPaperInfoWithReview['publishSequence'] = thisPaperInfo['publishSequence']
		thisPaperInfoWithReview['tjSection'] = thisPaperInfo['tjSection']
		thisPaperInfoWithReview['noOfAuthors']=get_no_of_authors(tjyear,paperId)
		allPaperInfoWithReview.append(thisPaperInfoWithReview)
	allPaperInfoWithReview.sort(key=operator.itemgetter('submissionSequence'))
	return allPaperInfoWithReview

def display_strings():
	stringDict = {'REVIEW_RESULT':app.config['REVIEW_RESULT'],\
		'RESEARCHING_AREAS':app.config['RESEARCHING_AREAS'],\
		'EMAIL_RECIPIENT_ROLES':app.config['EMAIL_RECIPIENT_ROLES']\
	}
	return stringDict

def information_updated(oldInfo, newInfo):
	if (newInfo != oldInfo):
		return True
	return False
 
def validate_email(email_address):
	match = re.match('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$', email_address)
	if match == None:
		return False
	return True
	
def parse_email_name(email_address):
	name = re.search('^([a-zA-Z]+).*', email_address).group(1)
	
	return name
	
