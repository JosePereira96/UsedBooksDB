import usedBooksDB
import datetime
import requests
from PIL import Image

db, myCursor = usedBooksDB.connect()

class Book:
    
    def __init__(self,title,author,price,pageURL,imageURL,genre,languageString,userName):
        self.title = title
        self.author = author
        self.price = price
        self.pageURL = pageURL
        self.imageURL = imageURL
        self.genre = genre
        self.languageString = languageString
        self.userName = userName
        self.mainID = 0
        self.secID = 0

    def insertToTable(self,table):
        myCursor.execute("""
                INSERT INTO {}(Title,Author,Price,Genre,Language,CreatedBy,PageURL,ImageURL,DateAdded)
                VALUES ("{}","{}",{},"{}","{}","{}","{}","{}","{}");
            """.format(table.name,
                       self.title,
                       self.author,
                       self.price,
                       self.genre,
                       self.languageString,
                       self.userName,
                       self.pageURL,
                       self.imageURL,
                       datetime.datetime.now()
                      )
                )
        db.commit() 
        
    #checks if a book is in a given table. returns boolean
    def checkTable(self,table):
        myCursor.execute("SELECT BookID FROM {} WHERE PageURL = \"{}\"".format(table.name, self.pageURL))
        queryResult = myCursor.fetchall()
        
        if queryResult: 
            if table.main:
                self.mainID = queryResult[0][0]
            else:
                self.secID = queryResult[0][0]
                
        return (bool(queryResult))
    
    #updates the genre of a given book, since some books may appear in more than 1 genreCode(e.g. scifi & fantasy). prevents duplicates in database. 
    #this function is only called when the book is in the recently_added table (before inserting to books table)
    def updateGenre(self,table):        
        myCursor.execute("SELECT Genre FROM {} WHERE BookID = {}".format(table.name,self.secID))
        
        aux = []
        aux.append(myCursor.fetchone()[0])
        
        if self.genre in aux:
            pass
        else:
            aux.append(self.genre)
            
        aux.sort()
        newGenre = ""

        for i in aux:
            newGenre += i
            newGenre += ','

        #removes last comma
        self.genre = newGenre[:-1]
            
        myCursor.execute("UPDATE {} SET Genre=\"{}\" WHERE BookID = {};".format(table.name,self.genre,self.secID))
        db.commit()
        
    
    def loadBookCover(self):
        data = requests.get(self.imageURL).content 
  
        # Opening a new file named img with extension .jpg 
        # This file would store the data of the image file 
        f = open('img.jpg','wb') 
  
        # Storing the image data inside the data variable to the file 
        f.write(data) 
        f.close() 
  
        # Opening the saved image and displaying it 
        img = Image.open('img.jpg') 
        img.show()
        
    def prettyPrint(self):
        print(self.title,",",self.author, "|",self.price,"€")