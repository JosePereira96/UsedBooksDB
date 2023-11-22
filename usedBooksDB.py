import mysql.connector
from configparser import ConfigParser

config = ConfigParser()
config.read("myconfig.ini")
loginData = config['database']

def connect():
    db = mysql.connector.connect(
        host=loginData['host'],
        user=loginData['user'],
        password=loginData['password'],
        database = loginData['dbName']
    )

    myCursor = db.cursor()


    #Table Creation
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            BookID int NOT NULL AUTO_INCREMENT,
            Title varchar(255) NOT NULL,
            Author varchar(255) NOT NULL,
            Price FLOAT(6,2) NOT NULL,
            Genre varchar(50) NOT NULL,
            Language varchar(50) NOT NULL,
            CreatedBy varchar(50) NOT NULL,
            PageURL varchar(255) NOT NULL,
            ImageURL varchar(512) NOT NULL,
            DateAdded datetime NOT NULL,
            PRIMARY KEY (BookID)
        ); 
    """)


    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS recently_added (
            BookID int NOT NULL AUTO_INCREMENT,
            Title varchar(255) NOT NULL,
            Author varchar(255) NOT NULL,
            Price FLOAT(6,2) NOT NULL,
            Genre varchar(50) NOT NULL,
            Language varchar(50) NOT NULL,
            CreatedBy varchar(50) NOT NULL,
            PageURL varchar(255) NOT NULL,
            ImageURL varchar(512) NOT NULL,
            DateAdded datetime NOT NULL,
            PRIMARY KEY (BookID)
        ); 
    """)

    return (db,myCursor)

def disconnect():
    db.close()