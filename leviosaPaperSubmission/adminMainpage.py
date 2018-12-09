from leviosaPaperSubmission import app
from leviosaPaperSubmission import paperSubUtils,paperSubUtilsFile,adminReviewVolume
import sqlite3
from flask import request, session, g, redirect, url_for,\
	abort, render_template, flash
 


@app.route('/admin_mainpage')
def admin_mainpage():
	error = None
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	cur = g.db.execute('select tjyear from tjvolume order by id desc')
	tjvolume = [dict(tjyear=row[0]) for row in cur.fetchall()]
	paperSubUtilsFile.change_permissions_recursive(app.config['UPLOAD_FOLDER'], 0755)

	return render_template('adminMainpage.html', tjvolume=tjvolume, error=error) 
	

@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		with g.db:
			cur = g.db.execute("SELECT username, password FROM users")
			users = cur.fetchall()
			for user in users:
				dbUser = user[0]
				dbPswd = user[1]
				if dbUser == request.form['username']:
					if dbPswd == request.form['password']:
						session['logged_in'] = True
						flash('You were logged in')				
						return redirect(url_for('admin_mainpage'))
			flash('Wrong username or password')
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')


@app.route('/verify_email/<int:tjyear>/<int:paperId>/<string:role>', methods=['GET','POST'])
def verify_email(tjyear,paperId,role):
	error = None
	flash('Please enter your email address')

	flash('verify_email'+str(tjyear)+str(paperId))
	paperInfo = paperSubUtils.get_paper_info_with_review(tjyear,paperId)
	
	if request.method == 'POST':
		roleMatch = match_email_info(paperInfo, request.form['email'])
		if role == 'Author' and role == roleMatch:
				session['verified'] = True
				return redirect(url_for('review_paper_info',tjyear=tjyear, paperId=paperId))	
		elif role == 'Expert' and role == roleMatch:
				session['verified'] = True
				return redirect(url_for('submit_review_comments', tjyear=tjyear, paperId=paperId, isManagerReview=False) )
		elif role == 'Manager' and role == roleMatch:
				session['verified'] = True
				return redirect(url_for('submit_review_comments',tjyear=tjyear, paperId=paperId, isManagerReview=True))

	return render_template('verifyEmail.html',tjyear=tjyear, paperId=paperId, role=role, error=error)

def match_email_info(paperInfo, email):
	for authorInfo in paperInfo['authorList']:
		if(email == authorInfo['email']):
			return 'Author'
	if paperInfo['expertInfo']['email'] == email:
		return 'Expert'
	if paperInfo['managertInfo']['email'] == email:
		return 'Manager'		

@app.route('/add_tjvolume', methods=['GET','POST'])
def add_tjvolume():
	error = None
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	cur = g.db.execute("SELECT tjyear FROM tjvolume")
	tjvolumes = cur.fetchall()
	year = int(request.form['tjyear'])
	for tjvolume in tjvolumes:
		existyear=tjvolume[0]
		if year == existyear:
			flash('This TJ volume exists')
			return redirect(url_for('admin_mainpage'))
	g.db.execute('insert into tjvolume (tjyear) values (?)',[year])
	g.db.execute('insert into noOfTotalSubmittedPaper (tjyear,maxPaperId) values (?,?)', [year,0])
	g.db.execute('insert into tjinfo (tjyear,typeinfo, URL) values (?,?,?)',[year,'archive','n/a'])
	g.db.execute('insert into tjinfo (tjyear,typeinfo, URL) values (?,?,?)',[year,'spreadsheet','n/a'])
	g.db.commit()
	flash('New tj was successfully posted')
	return redirect(url_for('admin_mainpage'))


