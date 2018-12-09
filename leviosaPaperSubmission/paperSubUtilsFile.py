from leviosaPaperSubmission import app, paperSubUtilsOnlineInfo
from flask import request, g, url_for, render_template, flash
import re, os, operator,copy
import zipfile

def unzip_uploaded_file_and_parse_info(tjyear, thisPaperInfoWithReview, isFirstSub):
	thisPaperInfo =  thisPaperInfoWithReview['paperInfo']
	pathToZipFile = app.config['UPLOAD_FOLDER']+form_file_name(tjyear,thisPaperInfo['submissionSequence'], thisPaperInfo)+'.zip'
	zip_ref = zipfile.ZipFile(pathToZipFile, 'r')
	dirToExtractTo = app.config['UPLOAD_FOLDER']+form_file_name(tjyear,thisPaperInfo['submissionSequence'], thisPaperInfo)+'/'
	if isFirstSub == False and os.isdir(dirToExtractTo):
		shutil.rmtree(dirToExtractTo)
	zip_ref.extractall(dirToExtractTo)
	zip_ref.close()
	form_tex_and_bib_file_name(tjyear,thisPaperInfo)
	thisPaperInfoWithReview = parse_tex_file(tjyear, thisPaperInfoWithReview, isFirstSub)
	return thisPaperInfoWithReview

def form_tex_and_bib_file_name(tjyear, thisPaperInfo):
	pathToDir = app.config['UPLOAD_FOLDER']+form_file_name(tjyear,thisPaperInfo['submissionSequence'], thisPaperInfo)+'/'
	for file in os.listdir(pathToDir):
		if allowed_file_tex(file) and file != app.config['TEX_FILE_NAME']:
			oldFile = os.path.join(pathToDir,file)
			newFile = os.path.join(pathToDir,app.config['TEX_FILE_NAME'])
			os.rename(oldFile, newFile)
		elif allowed_file_bib(file) and file != app.config['BIB_FILE_NAME']:
			oldFile = os.path.join(pathToDir,file)
			newFile = os.path.join(pathToDir,app.config['BIB_FILE_NAME'])
			os.rename(oldFile, newFile)
	return
def parse_tex_file(tjyear, thisPaperInfoWithReview,isFirstSub):
	thisPaperInfo = thisPaperInfoWithReview['paperInfo']
	pathToLatexFile = os.path.join(app.config['UPLOAD_FOLDER']+form_file_name(tjyear,thisPaperInfo['submissionSequence'], thisPaperInfo)+'/',\
			app.config['TEX_FILE_NAME'])	

	

	with open(pathToLatexFile) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('\\'+app.config['TEX_NUMBER_AUTHOR_CMD']):
			regexString = app.config['TEX_NUMBER_AUTHOR_CMD']+'\{(.*)\}'
			noOfAuthors = int(re.search(regexString,line).group(1))
		elif line.startswith('\\'+app.config['TEX_PAPER_TITLE_CMD']):
			regexString = app.config['TEX_PAPER_TITLE_CMD']+'\{(.*)\}'
			thisPaperInfo['paperTitle'] = re.search(regexString,line).group(1)
		elif line.startswith('\\'+app.config['TEX_PAPAER_DPMT_CMD']):
			lineDepartment = line
		elif line.startswith('\\'+app.config['TEX_PAPER_AUTHOR_CMD']):
			lineAuthor = line
		elif line.startswith('\\'+app.config['TEX_PAPER_EMAIL_CMD']):
			lineEmail = line
			
	authorList = []
	regexStringDepartment = app.config['TEX_PAPAER_DPMT_CMD']
	regexStringAuthor = app.config['TEX_PAPER_AUTHOR_CMD']
	regexStringEmail = app.config['TEX_PAPER_EMAIL_CMD']

	for groupNumber in range(app.config['TEX_DEFAULT_MAX_AUTHOR']):
		regexStringAuthor = regexStringAuthor+'\{(.*)\}'
		regexStringEmail = regexStringEmail+'\{(.*)\}'
		regexStringDepartment = regexStringDepartment+'\{(.*)\}'
	departmentString = re.search(regexStringDepartment,lineDepartment).group(1).replace('\\','')
	thisPaperInfo['department'] = departmentString

	for index in range(noOfAuthors):
		authorInfo = {}
		authorInfo['name'] = re.search(regexStringAuthor,lineAuthor).group(index+1)
		authorInfo['authorOrder'] = index + 1
		emailString = re.search(regexStringEmail,lineEmail).group(index+1).replace('\\','')
		authorInfo['email']  = emailString
		authorList.append(authorInfo)
	managerInfo = paperSubUtilsOnlineInfo.get_manager_info(authorList[0]['email'])
	expertInfo = {}

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

	return thisPaperInfoWithReview
		
def allowed_file_pdf(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_PDF']

def allowed_file_zip(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_ZIP']

def allowed_file_xlsx(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_XLSX']
		   
def allowed_file_tex(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_TEX']		   

def allowed_file_bib(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_BIB']


def change_permissions_recursive(path, mode):
	for root, dirs, files in os.walk(path, topdown=False):
		for dir in [os.path.join(root,d) for d in dirs]:
			os.chmod(dir, mode)
	for file in [os.path.join(root, f) for f in files]:
			os.chmod(file, mode)

def upload_file(fileType, isFirstSub, isReviewer, isManager, thisPaperInfo,file, tjyear,thisPaperId, reviewInfo=None):
	error = ""
	filesUrl = "n/a"
	filename = "n/a"
	needsToUpdate =	 False

	if not file:
		needsToUpdate = False 
		if isFirstSub:
			#Other documents are not required when submitting new paper
			if fileType=="ZIP":
				error = "For editorial work, .zip document only	 -	\n"
			else:
				filesUrl = "n/a"
				needsToUpdate = True
		else:
			if fileType == "ZIP":
				if isReviewer:
					filesUrl = "n/a"
				else: 
					filesUrl = thisPaperInfo['zipURL']
			elif fileType == "PDF":
				if isReviewer:
					filesUrl = reviewInfo['commentedVersionURL']
				else:
					filesUrl = thisPaperInfo['pdfURL']
			elif fileType == "XLSX":
				#can only be from the reviewer
				filesUrl = reviewInfo['excelURL']
	else:
		filenameStr = form_file_name(tjyear,thisPaperId, thisPaperInfo)
		if isReviewer:
			if isManager:
				filenameStr += "manager_Review"
			else:
				filenameStr += "expert_Review"
			

		if fileType == "PDF":
			if allowed_file_pdf(file.filename):
				filename = filenameStr +'.pdf'
				needsToUpdate = True
			else:
				error = "For review document, .pdf document only  -	 \n"

		elif fileType == "ZIP":
			if allowed_file_zip(file.filename):
				filename = filenameStr +'.zip'
				needsToUpdate = True
			else:
				error = "For compressed file, .zip document only  -	 \n"			
		elif fileType == "XLSX":
			if allowed_file_xlsx(file.filename):
				filename = filenameStr +'.xlsx'
				needsToUpdate = True
			else:
				error = "For review form file, .xlsx document only  -	 \n"					
		if filename != "n/a":
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			filesUrl = app.config['UPLOAD_URL_PREFIX']+filename
	return {'error':error, 'filesUrl':filesUrl,'needsToUpdate':needsToUpdate}

def form_file_name(tjyear,thisPaperId, thisPaperInfo):
	return str(tjyear)+'-'+'id'+str(thisPaperId)+'-'+'cat'+\
	str(thisPaperInfo['tjSection'])+'-'+'pid'+str(thisPaperInfo['publishSequence'])



def delete_file(tjyear, thisPaperId, paperInfo):
	filenameStr = form_file_name(tjyear,thisPaperId,paperInfo)
	for fileType in ['PDF','ZIP']:
		if fileType == 'PDF': 
			filename = filenameStr+'.pdf'
		elif fileType == 'ZIP': 
			filename = filenameStr+'.zip'
		else:
			continue
		fileToBeDeleted = os.path.join(app.config['UPLOAD_FOLDER'],filename)
		if(os.path.isfile(fileToBeDeleted)):
			os.remove(fileToBeDeleted)
	return
			
def update_file_name(tjyear, thisPaperId, oldPaperInfo, newPaperInfo):
	#needs to be updated to update all related files and directories.
	oldFileNameStr = form_file_name(tjyear,thisPaperId,oldPaperInfo)
	newFileNameStr = form_file_name(tjyear,thisPaperId,newPaperInfo)
	oldPath = os.path.join(app.config['UPLOAD_FOLDER'],oldFileNameStr)
	newPath = os.path.join(app.config['UPLOAD_FOLDER'],newFileNameStr)
	
	if (os.path.isdir(oldPath)):
		os.rename(oldPath, newPath)
	for fileType in ['TEX','PDF','ZIP','BIB']:
		if fileType == 'PDF': 
			oldFileName = oldFileNameStr+'.pdf'
			newFileName = newFileNameStr+'.pdf'
			url2BUpdated = 'pdfURL'
		elif fileType == 'ZIP': 
			oldFileName = oldFileNameStr+'.zip'
			newFileName = newFileNameStr+'.zip'
			url2BUpdated = 'zipURL'
		else:
			continue
		oldFile = os.path.join(app.config['UPLOAD_FOLDER'],oldFileName)
		newFile = os.path.join(app.config['UPLOAD_FOLDER'],newFileName)

		if(os.path.isfile(oldFile)):
			os.rename(oldFile,newFile)
			newPaperInfo[url2BUpdated] = app.config['UPLOAD_URL_PREFIX']+newFileName
		else:
			continue
	return newPaperInfo
	
def update_review_file_name(tjyear, thisPaperId, oldPaperInfo, newPaperInfo,newReviewInfo, isManager):
	if isManager == True:
		suffixString = 'manager_Review'
	else:
		suffixString = 'expert_Review'
		
	oldFileNameStr = form_file_name(tjyear,thisPaperId,oldPaperInfo)+suffixString
	newFileNameStr = form_file_name(tjyear,thisPaperId,newPaperInfo)+suffixString
	for fileType in ['PDF','XLSX']:
		if fileType == 'PDF': 
			oldFileName = oldFileNameStr+'.pdf'
			newFileName = newFileNameStr+'.pdf'
		elif fileType == 'XLSX': 
			oldFileName = oldFileNameStr+'.xlsx'
			newFileName = newFileNameStr+'.xlsx'
		else:
			continue
		oldFile = os.path.join(app.config['UPLOAD_FOLDER'],oldFileName)
		newFile = os.path.join(app.config['UPLOAD_FOLDER'],newFileName)

		if(os.path.isfile(oldFile)):
			os.rename(oldFile,newFile)
			newReviewInfo['commentedVersionURL'] = app.config['UPLOAD_URL_PREFIX']+newFileName
		else:
			continue
	return newReviewInfo