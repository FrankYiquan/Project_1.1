CREATE TABLE MotionPicture (
    id INT PRIMARY KEY,        
    NAME VARCHAR(255) NOT NULL, 
    rating DECIMAL(3,1) CHECK (rating BETWEEN 0 AND 10), 
    production VARCHAR(255),  
    budget BIGINT CHECK (budget > 0)
);


CREATE TABLE Users (
    email VARCHAR(255) PRIMARY KEY,        
    NAME VARCHAR(255), 
    age INT CHECK (age > 0)
);

CREATE TABLE Likes (
    mpid INT,   
    uemail VARCHAR(255),
    PRIMARY KEY (uemail, mpid),     
    FOREIGN KEY (uemail) REFERENCES Users(email),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);

CREATE TABLE Movie (
    mpid INT PRIMARY KEY,   
    boxoffice_collection INT CHECK (boxoffice_collection >= 0),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);

CREATE TABLE Series (
    mpid INT PRIMARY KEY,   
    season_count INT CHECK (season_count >= 0),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);

CREATE TABLE People (
    id INT PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    nationality VARCHAR(255),
    dob DATE, 
    gender VARCHAR(100)
);

CREATE TABLE Role (
    mpid INT,   
    pid INT,
    role_name VARCHAR(100),
    PRIMARY KEY(mpid, pid, role_name),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    FOREIGN KEY (pid) REFERENCES People(id)
);

CREATE TABLE Award (
    mpid INT,
    pid INT,
    award_name VARCHAR(255),
    award_year INT,
    PRIMARY KEY(mpid, pid, award_name, award_year),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    FOREIGN KEY (pid) REFERENCES People(id)
);

CREATE TABLE Genre (
    mpid INT,
    genre_name VARCHAR(255),
    PRIMARY KEY (mpid, genre_name),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);

CREATE TABLE Location (
    mpid INT,
    zip INT,
    city VARCHAR(255),
    country VARCHAR(255),
    PRIMARY KEY(mpid, zip),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);


