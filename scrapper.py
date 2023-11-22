from bs4 import BeautifulSoup
import requests
import time
from PIL import Image
import datetime
import concurrent.futures
import mysql.connector

import usedBooksDB
import TableClass
import FileClass
import BookClass
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

db,myCursor = usedBooksDB.connect()

mainURL = 'https://tradestories.pt' 

mainTable = TableClass.Table("books",True)
secondaryTable = TableClass.Table("recently_added",False)

log = FileClass.File('log.txt')

batchSize = int(config['variables']['batchsize'])
   
books = []

desiredBooks = []
relation = config['genre_language_relation']
for item in relation:
    genre, language = item.split('-')
    desiredBooks.append((config['genre_codes'][genre],config['language_codes'][language]))




#builds the URL based on the genre and language codes and page number
def buildURL(genreCode,languageCode,pageNumber):
    global mainURL

    resultURL = f'{mainURL}/comprar?combine=&genero[{genreCode}]={genreCode}&idioma={languageCode}&sort_by=created&page={str(pageNumber)}'

    return resultURL 

#checks books that have been sold, meaning the url is broken. used in Table.checkAllURLs() in parallel
def checkBrokenURL(bookID,url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text,"lxml")
    pageContent = soup.find_all(class_ = "view-content")
    
    if pageContent:
        return 0
    else:
        return bookID

def genreCodeToString(genreCode):
    global config
    
    outputString = ""

    for i in config['genre_codes']:
        if config['genre_codes'][i] == genreCode:
            outputString = i
            break
    
    return outputString

def languageCodeToString(languageCode):
    global config
    
    outputString = ""
      
    for i in config['language_codes']:
        if config['language_codes'][i] == languageCode:
            outputString = i
            break
    
    return outputString


#gets the information from a single page, creates the books and appends them to a global array to be added to the DB afterwards  
#each page contains 30 book elements
def ScrapPage(genreCode,languageCode,pageNumber):
    global mainTable
    global secondaryTable
    global books
    
    genreString = genreCodeToString(genreCode)
    languageString = languageCodeToString(languageCode)
    validPageFlag = True
    
    url = buildURL(genreCode,languageCode,pageNumber)
    page = requests.get(url)
    
    if page.ok:
        soup = BeautifulSoup(page.text,"lxml")
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
                
                newBook = BookClass.Book(title,author,price,pageURL,imageURL,genreString,languageString,userName)

                books.append(newBook)
        else:
            validPageFlag = False
    
    else:
        print("Connection issue!")
    
    return validPageFlag
    
#runs the ScrapPage function in parallel, improving performance. 
def multiScrapPage(genreCode,languageCode,startPage,endPage,workers=batchSize):
    start = time.time()
    validPageFlag = True
        
    # Execute ScrapPage in multiple threads each having a different page number
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = [executor.submit(ScrapPage,genreCode,languageCode,pageNumber=i) for i in range(startPage,endPage)]
    
    for i in results:
        validPageFlag = i.result() and validPageFlag
    
    end = time.time()    
    print(f'Checking Pages {startPage}-{endPage-1} | Time elapsed: {end-start:.3f}s')
    return validPageFlag




#runs multiScrapPage for each genre present in the desiredBooks array
if __name__ == "__main__":

    log.addToBuffer(str(datetime.datetime.now()))

    start = time.time()
    books.clear() 
    globalBookCounter = 0 

    for item in desiredBooks:
        genreCode, languageCode = item
    
        genreString = genreCodeToString(genreCode)
        validPageFlag = True
        newBooksFlag = True
        pageNumber = 0
        newBookCounter = 0
    
        print("Adding books in the",genreString,"genre")

        while validPageFlag and newBooksFlag:
            newFlag = multiScrapPage(genreCode,languageCode,pageNumber,pageNumber+batchSize)
            validPageFlag = validPageFlag and newFlag
        
            for book in books:
                if book.checkTable(secondaryTable):
                    book.updateGenre(secondaryTable)
                elif book.checkTable(mainTable):
                    newBooksFlag = False
                else:
                    book.insertToTable(secondaryTable)
                    newBookCounter += 1
            
        
            books.clear()    
            pageNumber += batchSize
            globalBookCounter += newBookCounter

        print(f"Added {newBookCounter} new books in the {genreString} genre\n")
        log.addToBuffer(f"\nAdded {newBookCounter} new books in the {genreString} genre")


    end = time.time()

    secondaryTable.mergeWithTable(mainTable)
    secondaryTable.clear()
        
    log.addToBuffer(f'\nAdded {globalBookCounter} books to DB.\n')
    log.addToBuffer(f'Total Elapsed Time: {end-start:.3f}s')
    log.addToBuffer("\n------------------------------------\n")
    log.writeLog()
