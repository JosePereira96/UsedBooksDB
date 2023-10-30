'''#Table Creation
myCursor.execute("""
    CREATE TABLE books (
        BookID int NOT NULL AUTO_INCREMENT,
        Title varchar(255) NOT NULL,
        Author varchar(255) NOT NULL,
        Price FLOAT(6,2) NOT NULL,
        Genre varchar(50) NOT NULL,
        Language ENUM("PT","EN") NOT NULL,
        CreatedBy varchar(50) NOT NULL,
        PageURL varchar(255) NOT NULL,
        ImageURL varchar(512) NOT NULL,
        DateAdded datetime NOT NULL,
        PRIMARY KEY (BookID)
    ); 
    """)


myCursor.execute("""
    CREATE TABLE recently_added (
        BookID int NOT NULL AUTO_INCREMENT,
        Title varchar(255) NOT NULL,
        Author varchar(255) NOT NULL,
        Price FLOAT(6,2) NOT NULL,
        Genre varchar(50) NOT NULL,
        Language ENUM("PT","EN") NOT NULL,
        CreatedBy varchar(50) NOT NULL,
        PageURL varchar(255) NOT NULL,
        ImageURL varchar(512) NOT NULL,
        DateAdded datetime NOT NULL,
        PRIMARY KEY (BookID)
    ); 
    """) '''


from bs4 import BeautifulSoup
import requests

import time

from PIL import Image
from datetime import datetime

import concurrent.futures

import mysql.connector

mainURL = 'https://tradestories.pt'   

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database = "usedbooksdb"
    )

myCursor = db.cursor()

def buildURL(genreCode,languageCode,pageNumber):
    global mainURL
    
    resultURL = mainURL+"/comprar?combine=&genero"+genreCode+"&idioma="+languageCode+"&sort_by=created"+"&page="+str(pageNumber)
    return resultURL 

#checks books that have been sold, meaning the url is broken 
def checkBrokenURL(bookID,url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text,'html')
    pageContent = soup.find_all(class_ = "view-content")
    
    if pageContent:
        return 0
    else:
        return bookID

class Table:
    global myCursor
    global db
    
    def __init__(self,name,main):
        self.name = name
        self.main = main

    #applies checkBrokenURL in parallel and deletes them linearly
    def checkAllURLs(self):
        myCursor.execute("SELECT BookID,PageURL FROM {};".format(self.name))
        queryResult = myCursor.fetchall()
        
        # Execute checkBrokenURL in multiple threads each having a different book URL
        with concurrent.futures.ThreadPoolExecutor(max_workers=10000) as executor:
            results = [executor.submit(checkBrokenURL,result[0],result[1]) for result in queryResult]
        
        #removes all the OK URL and leaves only the broken
        #results = [x.result() for x in results if x.result() != 0]
        #print("Removing",len(results),"books")
        for i in results:
            if i.result():
                self.deleteBook(i.result())
                
        db.commit()
        
    def deleteBook(self,bookID):        
        myCursor.execute("DELETE FROM {} WHERE BookID = {};".format(self.name,bookID))
    
    def mergeWithTable(self,table1):
        myCursor.execute("""
            INSERT INTO {}(Title,Author,Price,Genre,Language,CreatedBy,PageURL,ImageURL,DateAdded)
            SELECT Title,Author,Price,Genre,Language,CreatedBy,PageURL,ImageURL,DateAdded FROM {}
        """.format(table1.name,self.name))

        db.commit()

    def clear(self):
        myCursor.execute("DELETE FROM {}".format(self.name))
        db.commit()    
        
    def printContents(self):
        myCursor.execute("SELECT Title,Author,Genre FROM {}".format(self.name))
        results = myCursor.fetchall()
        
        for i in results:
            print(i)

mainTable = Table("books",True)
secondaryTable = Table("recently_added",False)

class Book:
    global myCursor
    global db
    
    def __init__(self,title,author,price,pageURL,imageURL,genre,languageCode,userName):
        self.title = title
        self.author = author
        self.price = price
        self.pageURL = pageURL
        self.imageURL = imageURL
        self.genre = genre
        self.languageCode = languageCodeToString(languageCode)
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
                       self.languageCode,
                       self.userName,
                       self.pageURL,
                       self.imageURL,
                       datetime.now()
                      )
                )
        db.commit() 
        
        
    def checkTable(self,table):
        myCursor.execute("SELECT BookID FROM {} WHERE PageURL = \"{}\"".format(table.name, self.pageURL))
        queryResult = myCursor.fetchall()
        
        if queryResult: 
            if table.main:
                self.mainID = queryResult[0][0]
            else:
                self.secID = queryResult[0][0]
                
        return (len(queryResult) > 0)
    
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

def genreCodeToString(genreCode):
    global fantasyCode 
    global scienceFictionCode 
    global nonFictionCode 
    global romanceCode 
    
    outputString = ""
      
    if genreCode == fantasyCode or genreCode == "Fantasia":
        outputString = "fantasy"
    elif genreCode == scienceFictionCode or genreCode == "Ficção científica":
        outputString = "scifi"
    elif genreCode == nonFictionCode or genreCode == "Não ficção":
        outputString = "nonfiction"
    elif genreCode == romanceCode or genreCode == "Romance":    
        outputString = "romance"
    else:
        pass
    
    return outputString

def languageCodeToString(languageCode):
    global englishLanguageCode
    global portugueseLanguageCode 
    
    outputString = ""
      
    if languageCode == englishLanguageCode:
        outputString = "EN"
    elif languageCode == portugueseLanguageCode:
        outputString = "PT"
    else:
        pass
    
    return outputString

fantasyCode = "%5B7%5D=7"
scienceFictionCode = "%5B3%5D=3"
nonFictionCode = "%5B9%5D=9"
romanceCode = "%5B11%5D=11"

englishLanguageCode = "18"
portugueseLanguageCode = "16"

batchSize = 5
   
books = []

def ScrapPage(genreCode,languageCode,pageNumber):
    global mainTable
    global secondaryTable
    global books
    
    genreString = genreCodeToString(genreCode)
    validPageFlag = True
    
    url = buildURL(genreCode,languageCode,pageNumber)
    page = requests.get(url)
    
    if page.ok:
        soup = BeautifulSoup(page.text,'html')
        pageContent = soup.find_all(class_ = "view-content")
        
        if pageContent:
            bookElement = pageContent[0].find_all(class_="views-row")
        
            for element in bookElement:            
                userName = (element.a['href']).split("/")[1]
                pageURL = mainURL + element.a['href']
                title = element.find(class_="views-field views-field-title").a.string.strip()
                title = title.replace("\"", "")
                author = element.find(class_="views-field views-field-field-livro-autor").find(class_="field-content").text[3:].strip()
                author = author.replace("\"", "")
                price = element.find(class_="preco").text
                price = float(price[:-1])
                imageURL = element.find(class_="image-style-medium")['src']
                
                newBook = Book(title,author,price,pageURL,imageURL,genreString,languageCode,userName)

                books.append(newBook)
        else:
            validPageFlag = False
    
    else:
        print("Connection issue!")
    
    return validPageFlag
    

def multiScrapPage(genreCode,languageCode,startPage,endPage,workers=batchSize):
    start = time.time()
    validPageFlag = True
        
    # Execute ScrapPage in multiple threads each having a different page number
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = [executor.submit(ScrapPage,genreCode,languageCode,pageNumber=i) for i in range(startPage,endPage)]
    
    for i in results:
        validPageFlag = i.result() and validPageFlag
    
    end = time.time()    
    print(f'Checking Pages {startPage}-{endPage-1} | Time elapsed: {end-start}')
    return validPageFlag