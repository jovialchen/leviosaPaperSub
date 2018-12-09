from leviosaPaperSubmission import app,paperSubUtils,paperSubUtilsFile
import sqlite3, copy, datetime, os, zipfile,shutil,re
from datetime import timedelta
from flask import request, session, g, redirect, url_for,\
	abort, render_template, flash, send_from_directory
import sys
import operator
from shutil import copyfile
import tempfile


app.config['TEX_FILE_NAME'] = 'script.tex'
app.config['BIB_FILE_NAME'] = 'ref.bib'	


app.config['TEX_INCLUDE_BIB_CMD'] = 'addbibresource'
app.config['TEX_DOCUMENTCLASS_CMD'] = 'documentclass'
app.config['TEX_CLASS_NAME'] = 'InnoTJ'
app.config['TEX_BEGINDOCUMENT_LINE'] = '\\begin{document}'
app.config['TEX_GRAPHICPATH_CMD'] = 'graphicspath'
app.config['TEX_ENDDOCUMENT_LINE'] = '\\end{document}'
app.config['TEX_BIB_REPLACE_SIGN'] = '$bibdocs'
app.config['TEX_CONTENT_REPLACE_SIGN'] = '$CONTENT'
app.config['TEX_COVER_REPLACE_SIGN'] = '$cover'
app.config['TEX_BACK_REPLACE_SIGN'] = '$back'
app.config['TEX_INPUT_SCRIPT_CMD'] = 'input'
app.config['TEX_PART_CMD'] = 'part'
def generate_this_year_journal(allPaperInfoWithReview, tjyear):
	allPaperInfoWithReview.sort(key=operator.itemgetter('publishSequence'))
	allPaperInfoWithReview.sort(key=operator.itemgetter('tjSection'))
	folderNames = []
	tjSection = 0
	bibString = ""
	contentString = '\n'+"\\"+app.config['TEX_PART_CMD'] +'{'+app.config['RESEARCHING_AREAS'][tjSection]+"}"+'\n'
	for paperInfoWithReview in allPaperInfoWithReview:
		folderNames = paperSubUtilsFile.form_file_name(tjyear,paperInfoWithReview['submissionSequence'],paperInfoWithReview['paperInfo'])
		bibString += '\n'+   '\\' + app.config['TEX_INCLUDE_BIB_CMD']  +'{'+folderNames+'/'+app.config['BIB_FILE_NAME']+'}' +'\n'
		if paperInfoWithReview['tjSection'] != tjSection:
			tjSection = paperInfoWithReview['tjSection'] 
			contentString += '\n'+"\\"+app.config['TEX_PART_CMD'] +'{'+app.config['RESEARCHING_AREAS'][tjSection]+"}"+'\n'
		contentString += '\n' +'\\'+app.config['TEX_INPUT_SCRIPT_CMD']+'{'+folderNames+'/'+app.config['TEX_FILE_NAME']+'}'  +'\n'
		texFile = os.path.join(app.config['UPLOAD_FOLDER']+folderNames,app.config['TEX_FILE_NAME'])
		with open(texFile, 'r') as filetemp :
			filedata = filetemp.read()

		graphicPathString = '\\'+ app.config['TEX_GRAPHICPATH_CMD']+'{{'+folderNames+'/}}'+'\n'
		filedata = filedata.replace('\\'+app.config['TEX_INCLUDE_BIB_CMD'], '%')
		filedata = filedata.replace('\\'+app.config['TEX_DOCUMENTCLASS_CMD'], '%')
		filedata = filedata.replace(app.config['TEX_BEGINDOCUMENT_LINE'], '%')
		filedata = filedata.replace(app.config['TEX_ENDDOCUMENT_LINE'], '%')
		filedata = filedata.replace('\\'+app.config['TEX_GRAPHICPATH_CMD'], '%')
		filedata = graphicPathString + filedata
		with open(texFile, 'w') as filetemp:
			filetemp.write(filedata)



	filename = str(tjyear)+'.tex'
	classFilename = str(tjyear)+'.cls'
	file = os.path.join(app.config['UPLOAD_FOLDER'],filename)
	classFile = os.path.join(app.config['UPLOAD_FOLDER'],classFilename)
	copyfile(os.path.join(app.config['UPLOAD_FOLDER'],'editorialDraft.tex'), file)
	copyfile(os.path.join(app.config['UPLOAD_FOLDER'],'InnoTJ.cls'), classFile)
	
	journalName = ' ' + str(tjyear)+' ' + app.config['EDITORIAL_COMMITEE_INFO']['journal']
	#update class file
	with open(classFile, 'r') as filetemp :
	  filedata = filetemp.read()
	filedata = filedata.replace(app.config['LATEX_CLASS_FOOTER'], journalName)
	with open(classFile, 'w') as filetemp:
	  filetemp.write(filedata)
	
	coverString = str(tjyear)+'_'+'cover.png'
	backString = str(tjyear)+'_'+'back.png'
	#update script
	with open(file, 'r') as filetemp :
	  filedata = filetemp.read()
	filedata = filedata.replace(app.config['TEX_BIB_REPLACE_SIGN'], bibString)
	filedata = filedata.replace(app.config['TEX_CONTENT_REPLACE_SIGN'], contentString)
	filedata = filedata.replace(app.config['TEX_COVER_REPLACE_SIGN'], coverString)
	filedata = filedata.replace(app.config['TEX_BACK_REPLACE_SIGN'], backString)
	filedata = filedata.replace('InnoTJ',str(tjyear))
	# Write the file out again
	with open(file, 'w') as filetemp:
	  filetemp.write(filedata)
	  
	return 

def update_compressed_file_for_authors(paperInfoWithReview, tjyear):
	folderNames = paperSubUtilsFile.form_file_name(tjyear,paperInfoWithReview['submissionSequence'],paperInfoWithReview['paperInfo'])
	#bibString += '\n'+   '\\' + app.config['TEX_INCLUDE_BIB_CMD']  +'{'+folderNames+'/'+app.config['BIB_FILE_NAME']+'}' +'\n'
	#if paperInfoWithReview['tjSection'] != tjSection:
		#tjSection = paperInfoWithReview['tjSection'] 
		#contentString += '\n'+"\\"+app.config['TEX_PART_CMD'] +'{'+app.config['RESEARCHING_AREAS'][tjSection]+"}"+'\n'
	#contentString += '\n' +'\\'+app.config['TEX_INPUT_SCRIPT_CMD']+'{'+folderNames+'/'+app.config['TEX_FILE_NAME']+'}'  +'\n'
	texFile = os.path.join(app.config['UPLOAD_FOLDER']+folderNames,app.config['TEX_FILE_NAME'])
	with open(texFile, 'r') as filetemp :
		filedata = filetemp.read()

	filedata = filedata.replace('\\'+app.config['TEX_INCLUDE_BIB_CMD'], '%')
	filedata = filedata.replace('\\'+app.config['TEX_DOCUMENTCLASS_CMD'], '%')
	filedata = filedata.replace(app.config['TEX_BEGINDOCUMENT_LINE'], '%')
	filedata = filedata.replace(app.config['TEX_ENDDOCUMENT_LINE'], '%')
	filedata = filedata.replace('\\'+app.config['TEX_GRAPHICPATH_CMD'], '%')
	headerString ='\\'+app.config['TEX_DOCUMENTCLASS_CMD']+'{'+ app.config['TEX_CLASS_NAME']+'}'+'\n'
	headerString += '\\'+app.config['TEX_INCLUDE_BIB_CMD']+'{'+ app.config['BIB_FILE_NAME'] +'}' +'\n'
	headerString += app.config['TEX_BEGINDOCUMENT_LINE']+'\n'
	footerString = app.config['TEX_ENDDOCUMENT_LINE']
	filedata = headerString + filedata + footerString
	with open(texFile, 'w') as filetemp:
		filetemp.write(filedata)
	
	downloadZipFile = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'],folderNames+'.zip'),'w')
	for file in os.listdir(app.config['UPLOAD_FOLDER']+folderNames+'/'):
		downloadZipFile.write(os.path.join(app.config['UPLOAD_FOLDER']+folderNames+'/',file),\
					file,\
					compress_type = zipfile.ZIP_DEFLATED)
	downloadZipFile.close()

	with open(texFile, 'r') as filetemp :
		filedata = filetemp.read()

	graphicPathString = '\\'+ app.config['TEX_GRAPHICPATH_CMD']+'{{'+folderNames+'/}}'+'\n'
	filedata = filedata.replace('\\'+app.config['TEX_INCLUDE_BIB_CMD'], '%')
	filedata = filedata.replace('\\'+app.config['TEX_DOCUMENTCLASS_CMD'], '%')
	filedata = filedata.replace(app.config['TEX_BEGINDOCUMENT_LINE'], '%')
	filedata = filedata.replace(app.config['TEX_ENDDOCUMENT_LINE'], '%')
	filedata = filedata.replace('\\'+app.config['TEX_GRAPHICPATH_CMD'], '%')
	filedata = graphicPathString + filedata
	with open(texFile, 'w') as filetemp:
		filetemp.write(filedata)
	return 