PRAGMA foreign_keys = ON;
drop table if exists users;
create table users(
	id integer primary key autoincrement,
	username string not null,
	password string not null
);

drop table if exists tjvolume;
create table tjvolume(
	id integer primary key autoincrement,
	tjyear integer
);

drop table if exists tjarchive;
create table tjinfo(
	id integer primary key autoincrement,
	tjyear integer,
	typeinfo string not null,
	URL string not null,
	FOREIGN KEY (tjyear) REFERENCES tjvolume(tjyear)
);

drop table if exists noOfTotalSubmittedPaper;
create table noOfTotalSubmittedPaper(
	id integer primary key autoincrement,
	tjyear integer,
	maxPaperId integer,
	FOREIGN KEY (tjyear) REFERENCES tjvolume(tjyear)
);

drop table if exists submissionList;
create table submissionList (
  id integer primary key autoincrement,
  paperTitle string not null,
  department string not null,
  pdfURL string not null,
  zipURL string not null,
  tjSection integer,
  approvedStatus boolean,
  submissionSequence integer,
  publishSequence integer,
  tjyear integer,
  FOREIGN KEY (tjyear) REFERENCES tjvolume(tjyear)
);

drop table if exists reviewContent;
create table reviewContent(
	id integer primary key autoincrement,
    reviewSubmitted boolean,
	Overall integer,
	commentedVersionURL string not null,
	excelURL string not null,
	isManagerReview boolean,
	submissionSequence integer,
    tjyear integer,
    FOREIGN KEY (tjyear,submissionSequence) REFERENCES submissionList(tjyear,submissionSequence)
);

drop table if exists reviewItem;
create table reviewItem(
	id integer primary key autoincrement,
	tjyear integer,
	submissionSequence integer,
	isManagerReview boolean,
	reviewItemName string not null,
	reviewItemGrade integer,
	FOREIGN KEY (tjyear,submissionSequence,isManagerReview) REFERENCES reviewContent(tjyear,submissionSequence,isManagerReview)
);

drop table if exists reviewComments;
create table reviewComments(
	id integer primary key autoincrement,
	tjyear integer,
	submissionSequence integer,
	isManagerReview boolean,
	question string not null,
	answer string not null,
	FOREIGN KEY (tjyear,submissionSequence,isManagerReview) REFERENCES reviewContent(tjyear,submissionSequence,isManagerReview)
);

drop table if exists personInfo;
create table personInfo(
	id integer primary key autoincrement,
	submissionSequence integer,
	authorOrder integer,
	role string not null,
	name string not null,
	email string not null,
	tjyear integer,
    FOREIGN KEY (tjyear,submissionSequence) REFERENCES submissionList(tjyear,submissionSequence)
);	

drop table if exists noOfAuthors;
create table noOfAuthors(
	id integer primary key autoincrement,
	tjyear integer,
	submissionSequence integer,
	numberOfAuthors integer,
    FOREIGN KEY (tjyear,submissionSequence) REFERENCES submissionList(tjyear,submissionSequence)
);
