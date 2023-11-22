import datetime

class File:
    
    def __init__(self,name):
        self.name = name
        self.buffer= []
    
    def addToBuffer(self,string):
        self.buffer.append(string)

    def writeLog(self):
        f = open(self.name,'a')
        
        for s in self.buffer:
            f.write(s)

        self.buffer.clear()
        f.close()
        
    def eraseLog(self):
        # delete the data inside file
        # but not the file itself
  
        f = open(self.name, "r+")  
        f.seek(0)  
        f.truncate()  
        f.close()