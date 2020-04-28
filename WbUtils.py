import csv

class WbUtils:

    pathFile = "/example"

    #Constructor 1
    def __init__ (self): 
         self.pathFile = ""

    #Constructor Inicializando el pathfile
    def setPathFile(self, f = "" ):
        self.pathFile = f

    def readFile (self, useDictReader = False): #Metodo para leer el archivo
        results = []
        if useDictReader == False:
            with open (self.pathFile,  newline='', encoding= "ISO-8859-1") as File:
                reader = csv.reader(File, delimiter=',',quotechar=',',quoting=csv.QUOTE_NONE)
                for row in reader:
                    #print(row)
                    r = results + [row]
                    results = r
                #print(results)
            return results
        else:
            
            with open(self.pathFile) as File:
                reader = csv.DictReader(File)
                for row in reader:
                    #results.append(row)
                    #print(row)
                    r = results + [row]
                    #results = r
                print(results)
            return results

    def writeFile(self, data = [] , headers = [], useDictReader=False): # Método para escribir un archivo CSV
        print(self.pathFile)
        if useDictReader == False:
            #f = open(self.pathFile,'w', newline='', encoding='cp1252')
            f = open(self.pathFile,'w', newline='', encoding='ISO-8859-1',errors='ignore')
            with f :
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            print("Writing %s without DictReader complete" % self.pathFile)
        else:
            #f = open(self.pathFile, encoding='cp1252')
            f = open(self.pathFile, encoding='ISO-8859-1',errors='ignore')
            with f:    
                myFields = headers
                writer = csv.DictWriter(f, fieldnames=myFields)    
                writer.writeheader()
                for company in data:
                    writer.writerow(company)
                print("Writing %s with DictReader complete" % self.pathFile)
                
       
        
