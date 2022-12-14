CREATE TABLE IF NOT EXISTS Customer(
	fName		VARCHAR(15) NOT NULL,
	Lname		VARCHAR(15) NOT NULL,
	email		VARCHAR(50) UNIQUE NOT NULL,
	uid			INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Publisher(
	pName		VARCHAR(50) UNIQUE NOT NULL PRIMARY KEY,
	banking		VARCHAR(50) UNIQUE NOT NULL,
	email		VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Phone(
	pName		VARCHAR(50) NOT NULL PRIMARY KEY,
	phoneNumber	VARCHAR(10) UNIQUE NOT NULL,
	FOREIGN KEY (pName)
		REFERENCES Publisher (pName)
);


CREATE TABLE IF NOT EXISTS Book(
	bid			INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	price 		INT NOT NULL,
	percentage	float NOT NULL,
	pages 		INT,
	pName		VARCHAR(50) NOT NULL,
	name		VARCHAR(50) NOT NULL,
	CHECK (percentage>=0 AND percentage <=1),
	FOREIGN KEY (pName)
		REFERENCES Publisher (pName)
);


CREATE TABLE IF NOT EXISTS BK_Order(
	oNum		INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY ,
	shipping	VARCHAR(15) NOT NULL,
	billing		VARCHAR(50) NOT NULL,
	uid			INT NOT NULL,
	bid			INT NOT NULL,
	quantity	INT,
	FOREIGN KEY (uid)
		REFERENCES Customer (uid),
	FOREIGN KEY (bid)
		REFERENCES Book (bid)
);


CREATE TABLE IF NOT EXISTS Author(
	bid			INT NOT NULL,
	author		VARCHAR(50) NOT NULL,
	PRIMARY KEY (bid, author),
	FOREIGN KEY (bid)
		REFERENCES Book (bid)
);

CREATE TABLE IF NOT EXISTS Genre(
	bid			INT NOT NULL,
	genre		VARCHAR(50) NOT NULL,
	PRIMARY KEY (bid, genre),
	FOREIGN KEY (bid)
		REFERENCES Book (bid)
);


CREATE TABLE IF NOT EXISTS Store(
	sNum		INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	salesVsExp	INT
);

CREATE TABLE IF NOT EXISTS Sale(
	sid		INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	bid		INT NOT NULL,
	quantity	INT NOT NULL,
	sNum		INT NOT NULL,
	FOREIGN KEY (sNum)
		REFERENCES Store (sNum)
);

CREATE TABLE IF NOT EXISTS Store_Book(
	bid			INT NOT NULL,
	quantity	INT NOT NULL,
	restock		INT NOT NULL,
	sNum		INT NOT NULL,
	PRIMARY KEY (bid, sNum),
	FOREIGN KEY (sNum)
		REFERENCES Store (sNum),
	FOREIGN KEY (bid)
		REFERENCES Book (bid)
	
);


CREATE TABLE IF NOT EXISTS SalesPerGenre(
	sNum		INT NOT NULL,
	genre		VARCHAR(50) UNIQUE NOT NULL,
	sales		INT,
	PRIMARY KEY (sNum, genre),
	FOREIGN KEY (sNum)
		REFERENCES Store (sNum)
);


CREATE TABLE IF NOT EXISTS SalesPerAuthor(
	sNum		INT NOT NULL,
	author		VARCHAR(50) NOT NULL,
	sales		INT,
	PRIMARY KEY (sNum, author),
	FOREIGN KEY (sNum)
		REFERENCES Store (sNum)
);













































