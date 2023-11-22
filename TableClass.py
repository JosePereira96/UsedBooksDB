import usedBooksDB

db, myCursor = usedBooksDB.connect()

class Table:
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
        results = [x.result() for x in results if x.result() != 0]
        print("Removing",len(results),"books")
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

