import sys
import WbUtils
import requests
import OutputData
from lxml import html
from urllib.parse import urlencode
from urllib.parse import quote
from requests.exceptions import RequestException
from difflib import SequenceMatcher
import csv
from enum import Enum
from googlesearch import search

class WebScrappingCompany:

    def __init__(self):
        self.Labels = {
            'Nombre':{'INFOCIF':'Nombre','GUIAEMPRESAS':'Nombre','AXESOR':'Nombre','INFOEMPRESA':'Nombre','EMPRESITE':'Nombre','GOOGLE':'Nombre'},
            'Brand':{'INFOCIF':'Marca','GUIAEMPRESAS':'Marca','AXESOR':'Marca','INFOEMPRESA':'Marca','EMPRESITE':'Marca','GOOGLE':'Marca'},
            'Website':{'INFOCIF':'Web','GUIAEMPRESAS':'Web','AXESOR':'Web','INFOEMPRESA':'Web','EMPRESITE':'Web','GOOGLE':'Web'},
            'NIF':{'INFOCIF':'NIF','GUIAEMPRESAS':'NIF','AXESOR':'NIF','INFOEMPRESA':'NIF','EMPRESITE':'NIF','Google':'NIF'},
            'Phone_Number':{'INFOCIF':'Teléfono','GUIAEMPRESAS':'Teléfono','AXESOR':'Teléfono','INFOEMPRESA':'Teléfono','EMPRESITE':'Teléfono','GOOGLE':'Teléfono'},              
            'Email':{'INFOCIF':'Email','GUIAEMPRESAS':'Email','AXESOR':'Email','INFOEMPRESA':'Email','EMPRESITE':'Email','GOOGLE':'Email'},
            'Industry':{'INFOCIF':'Sector','GUIAEMPRESAS':'Sector','AXESOR':'Sector','INFOEMPRESA':'Sector','EMPRESITE':'Sector','Google':'Sector'},
            'Contacts':{'INFOCIF':'Contactos','GUIAEMPRESAS':'Contactos','AXESOR':'Contactos','INFOEMPRESA':'Contactos','EMPRESITE':'Contactos','GOOGLE':'Contactos'},              
            'Contact_Title':{'INFOCIF':'Nombre Contacto','GUIAEMPRESAS':'Nombre Contacto','AXESOR':'Nombre Contacto','INFOEMPRESA':'Nombre Contacto','EMPRESITE':'Nombre Contacto','Google':'Nombre Contacto'},
            'Linkedin':{'INFOCIF':'Linkedin','GUIAEMPRESAS':'Linkedin','AXESOR':'Linkedin','INFOEMPRESA':'Linkedin','EMPRESITE':'Linkedin','GOOGLE':'Linkedin'},              
            'Facebook':{'INFOCIF':'Facebook','GUIAEMPRESAS':'Facebook','AXESOR':'Facebook','INFOEMPRESA':'Facebook','EMPRESITE':'Facebook','GOOGLE':'Facebook'},
            'Twitter':{'INFOCIF':'Twitter','GUIAEMPRESAS':'Twitter','AXESOR':'Twitter','INFOEMPRESA':'Twitter','EMPRESITE':'Twitter','Google':'Twitter'},
            'Instagram':{'INFOCIF':'Instagram','GUIAEMPRESAS':'Instagram','AXESOR':'Instagram','INFOEMPRESA':'Instagram','EMPRESITE':'Instagram','GOOGLE':'Instagram'},              
            'City':{'INFOCIF':'Ciudad','GUIAEMPRESAS':'Ciudad','AXESOR':'Ciudad','INFOEMPRESA':'Ciudad','EMPRESITE':'Ciudad','GOOGLE':'Ciudad'},
            'Facturacion':{'INFOCIF':'Facturacion','GUIAEMPRESAS':'Facturacion','AXESOR':'Facturacion','INFOEMPRESA':'Facturacion','EMPRESITE':'Facturacion','Google':'Facturacion'},
            'Empleados':{'INFOCIF':'Empleados','GUIAEMPRESAS':'Empleados','AXESOR':'Empleados','INFOEMPRESA':'Empleados','EMPRESITE':'Empleados','GOOGLE':'Empleados'}}              
        
        self.sourceList = []
        self.csvF = WbUtils.WbUtils()
        self.URLINFOCIF="http://www.infocif.es"
        self.URLAXESOR="https://www.axesor.es"
        self.URLGUIAEMPRESAS = "https://guiaempresas.universia.es"
        self.URLINFOEMPRESAS="https://www.infoempresa.com/es-es/es/"
        self.URLEMPRESITE="https://empresite.eleconomista.es/"
        self.URLGOOGLE="https://www.google.com/"
        self.URLINFOCIFSRCH="/general/empresas-informacion-listado-empresas.asp"
        self.URLAXESORSRCH="/buscar/empresas"
        self.URLGUIAEMPRESASSRCH = "/busqueda_empresas/"
        self.URLINFOEMPRESASSRCH="buscar"
        self.URLEMPRESITESRCH="Actividad/"
        self.URLGOOGLESRCH="search"
        self.SRCHNOTFOUND="Empresa no encontrada"
        self.SRCHNOTFOUND2="No se han encontrado resultados"
        self.FoundData = False
    def main(self):
        sourceList = []
        csvF = WbUtils.WbUtils()
        companyList = []
        if sys.argv[1:] != []:
            print(sys.argv[1:])
            csvF.setPathFile(sys.argv[1:][0])
        
            sourceList = csvF.readFile(False)
            if sourceList != []:
                sourceList.pop(0)
                listOfHeadersInput = sourceList[0]
                #print(listOfHeadersInput[0])
                sourceList.pop(0)
                #print(listOfHeadersInput)
                for sourceItems in sourceList:
                    if sourceItems != []:
                        company = self.newCompany(dict(zip(listOfHeadersInput, sourceItems)))
                        company[listOfHeadersInput[0]]['valor'] = sourceItems[0]
                        company[listOfHeadersInput[1]]['valor']= sourceItems[1]
                        company[listOfHeadersInput[2]]['valor'] = sourceItems[2]
                        company[listOfHeadersInput[3]]['valor'] = sourceItems[3]
                        #print(company[listOfHeadersInput[1]])
                        sourceItems = [sourceItems[1], sourceItems[3],sourceItems[0],sourceItems[2]]
                        #print(sourceItems)
                        for webSite in WebSite:
                            print('Buscando en la web de ' + str(webSite.name))
                            print('Los valores a ingresar en ' + str(webSite.name) + ' son:')
                            if self.FoundData == True:
                                self.FoundData = False
                                continue
                            else:
                                self.SearchData(sourceItems, self.buildUrl(webSite.value), company,listOfHeadersInput)
                        companyList.append(company)
                        print(companyList)

    def newCompany(self, objCompany={}):
        keys = objCompany.keys()
        for key in keys:
            objCompany[key] = {'valor' : '', 'fuente': ''}
        return objCompany

    #Método que construye la URL dependiendo del sitio
    #forma una lista con la URL, el tipo de URL, la fuente (sitio web enum) y los criterios de busqueda
    def buildUrl(self,v):
        url = ""
        fullUrl ={}
        if v == WebSite.GOOGLE.value:
            url = self.URLGOOGLE + self.URLEMPRESITESRCH
            print(url)
            fullUrl['url'] = url
            fullUrl['type'] = 'd'
            fullUrl['src'] = v
            fullUrl['params'] = {'q': '' }
        return fullUrl
    
    #Método que obtiene la lista de links arrojados por una busqueda, dependiendo de la página
    def getListLinks(self, txtHtml,srcWeb = 0):
        rL = []
        return rL
    
    #Método que obtiene los contenedores del detalle de la información de las empresas dependiendo de la pagina
    def getOutputsContainer(self, webSrc, txtHtml):
        r = None
        return r

    #Método que obtiene el matchratio de las cadenas encontradas en la lista de resultados dependiendo del parametro de cada pagina
    def getMatchRatioFromStr(self, srcWeb, params, link):
        matchRatioStr = 0.0
        return matchRatioStr

    def getOutputDataFromHtml(self, typeO, field, webSrc):
        oData = []
        if typeO == "Label" :
            print("Label")
        else:
            print("Field")
        print(oData)
        return oData

    def SearchData(self, sourceItems, fullUrl={}, company={}, headersCsv={}):
        #outputList = []
        outputList = {}
        for index, item in enumerate(sourceItems):
            print('Buscando: ' + item)
            if item != "":
                url= fullUrl['url']
                print('URL de busqueda: ' + url)
                params = None
                if fullUrl['type'] == 'd':
                    '''if fullUrl['src'] == WebSite.INFOCIF.value:
                        params = fullUrl['params']
                        params['Buscar'] = item
                    '''
                    if fullUrl['src'] == WebSite.GOOGLE.value:
                        params = fullUrl['params']
                        params['q'] = item
                    '''if fullUrl['src'] == WebSite.INFOEMPRESA.value:
                        params = fullUrl['params']
                        params['q'] = item'''
                    print(params)
                else:
                    params = fullUrl['params']
                    params['pathSearch'] = str(item).replace(u' ',u'-')

                resultLinks = ""
                try:
                    page = None
                    if fullUrl['type'] == 'd':
                        page = requests.get(url, params=params, timeout=5)
                    else:
                        page = requests.get(url+params['pathSearch'], timeout=5)
                    page.encoding = 'ISO-8859-1'
                    if page.status_code == 200 :
                        txtHtml = html.fromstring(page.content)
                        #print(txtHtml.xpath('//div[@id="generic-msg-status"]/text()'))
                        #print(txtHtml.xpath('//div[contains(@id, "generic-msg-status")]/text()'))
                        if (txtHtml.xpath('//div[contains(@id, "generic-msg-status")]/text()') != []) or (txtHtml.xpath('//div[@id="generic-msg-status"]/text()') != []):
                            print('NOT FOUND RESULTS')
                            continue
                        else:
                            print('FOUND RESULTS')
                            pageCompany = ""
                            resultLinks = []
                            resultLinks = self.getListLinks(txtHtml, fullUrl['src'])
                            print(resultLinks)
                            if resultLinks != []:
                                print('Resultados encontrados')
                                ratioMatch=0.0
                                strMatchVal = 0.0
                                indexList = 0
                                indexiter = 0
                                for link in resultLinks:
                                    print(link.attrib['href'], link.text_content())
                                    #if ratioMatch <= SequenceMatcher(None, params['Buscar'], link.text_content()).real_quick_ratio():
                                        #ratioMatch = SequenceMatcher(None, params['Buscar'], link.text_content()).real_quick_ratio()
                                    strMatchVal = self.getMatchRatioFromStr(fullUrl['src'],params,link)
                                    if ratioMatch <= strMatchVal:
                                        ratioMatch = strMatchVal
                                        indexList = indexiter
                                        print('# 270 Indice de lista de resultados: ', indexList)
                                        indexiter += indexiter
                                        pageCompany = self.cleanUrl(resultLinks[indexList].attrib['href'])
                                print('# 273 ',pageCompany)
                                pageDetail = requests.get(pageCompany)
                                pageDetail.encoding = 'utf-8'
                                if pageDetail.status_code == 200 :
                                    txtHtml = html.fromstring(pageDetail.text)
                                    #fields = txtHtml.xpath('//div[contains(@id, "fe-informacion-izq")]')
                                    fields = self.getOutputsContainer(fullUrl['src'],txtHtml)
                                    for field in fields:
                                        #outputs = field.xpath('//strong[contains(@class, "fwb")]/text()')
                                        outputs = self.getOutputDataFromHtml("Label",field,fullUrl['src'])
                                        h = 0
                                        for outputHdr in outputs:
                                            outputs[h] = str(str(str(str(outputHdr.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')).replace('\n','')
                                        print('#283 labels: ',outputs)
                                        #datos = field.xpath('//*[contains(@class, "editable")]/text()')
                                        datos = self.getOutputDataFromHtml("Data",field,fullUrl['src'])
                                        i = 0
                                        for dato in datos:
                                            datos[i] = str(str(str(dato.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')
                                            #print(type(dato))
                                            i = i +1
                                        print('#287 datos: ',datos)
                                        for i, e in enumerate(outputs):
                                            #oD = OutputData.OutputData()
                                            if self.Labels['Nombre'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[0]]['valor'] == '' :
                                                company[headersCsv[0]]['valor'] = datos[i]
                                                company[headersCsv[0]]['fuente'] = pageCompany
                                            if self.Labels['Brand'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[1]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[1]]['valor'] = datos[i]
                                                company[headersCsv[1]]['fuente'] = pageCompany
                                            if self.Labels['Website'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[2]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[2]]['valor'] = datos[i]
                                                company[headersCsv[2]]['fuente'] = pageCompany
                                            if self.Labels['NIF'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[3]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[3]]['valor'] = datos[i]
                                                company[headersCsv[3]]['fuente'] = pageCompany
                                            if self.Labels['Phone_Number'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[4]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[4]]['valor'] = datos[i]
                                                company[headersCsv[4]]['fuente'] = pageCompany
                                            if self.Labels['Email'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[5]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[5]]['valor'] = datos[i]
                                                company[headersCsv[5]]['fuente'] = pageCompany
                                            if self.Labels['Industry'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[6]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[6]]['valor'] = datos[i]
                                                company[headersCsv[6]]['fuente'] = pageCompany
                                            if self.Labels['Contacts'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[7]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[7]]['valor'] = datos[i]
                                                company[headersCsv[7]]['fuente'] = pageCompany
                                            if self.Labels['Contact_Title'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[8]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[8]]['valor'] = datos[i]
                                                company[headersCsv[8]]['fuente'] = pageCompany
                                            if  company[headersCsv[9]]['valor'] == '':
                                                self.FoundData == True
                                                for j in search("Linkedin " + str(item), tld='es', lang='en', num=1, start=0, stop=None, pause=1.0): 
                                                    company[headersCsv[9]]['valor'] = j
                                                company[headersCsv[9]]['fuente'] = ("https://google.com/search?q=Linkedin%20" + str(item).replace(" ","%20"))
                                                print(j)
                                            if  company[headersCsv[10]]['valor'] == '':
                                                self.FoundData == True
                                                for j in search("Facebook " + str(item), tld='es', lang='en', num=1, start=0, stop=None, pause=1.0): 
                                                    company[headersCsv[9]]['valor'] = j
                                                company[headersCsv[9]]['fuente'] = ("https://google.com/search?q=Facebook%20" + str(item).replace(" ","%20"))
                                                print(j)
                                            if company[headersCsv[11]]['valor'] == '':
                                                self.FoundData == True
                                                for j in search("Twitter " + str(item), tld='es', lang='en', num=1, start=0, stop=None, pause=1.0): 
                                                    company[headersCsv[9]]['valor'] = j
                                                company[headersCsv[9]]['fuente'] = ("https://google.com/search?q=Twitter%20" + str(item).replace(" ","%20"))
                                                print(j)
                                            if company[headersCsv[12]]['valor'] == '':
                                                self.FoundData == True
                                                for j in search("Instagram " + str(item), tld='es', lang='en', num=1, start=0, stop=None, pause=1.0): 
                                                    company[headersCsv[9]]['valor'] = j
                                                company[headersCsv[9]]['fuente'] = ("https://google.com/search?q=Instagram%20" + str(item).replace(" ","%20"))
                                                print(j)
                                            if self.Labels['City'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[13]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[13]]['valor'] = datos[i]
                                                company[headersCsv[13]]['fuente'] = pageCompany
                                            if self.Labels['Facturacion'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[14]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[14]]['valor'] = datos[i]
                                                company[headersCsv[14]]['fuente'] = pageCompany
                                                #outputList['Facturacion'] = [oD]
                                            if self.Labels['Empleados'][WebSite.getWebsiteName(fullUrl['src'])] in e and company[headersCsv[15]]['valor'] == '':
                                                self.FoundData == True
                                                company[headersCsv[15]]['valor'] = datos[i]
                                                company[headersCsv[15]]['fuente'] = pageCompany
                                        break
                                pageDetail.close()
                                return outputList
                            else:
                                print('Nada que mostrar')
                                continue
                            #break
                    page.close()
                except RequestException as e:
                    print('Exception: ', e)
                    #break
                    #continue
            else:
                print("item: " + str(index) + " vacio" )
                #continue
    
    def cleanUrl(self, url):
        if str(url).startswith('http://'):
            url = 'http://' + str(url).strip('http://')
        if str(url).startswith('https://'):
            url = 'http://' + str(url).strip('https://')
        if str(url).startswith('//'):
            url = 'http://' + str(url).strip('//')
        return url

    def find(self, key, dictionary):
        #print(key)
        for k, v in dictionary.iteritems():
            if k == key:
                #print(v)
                yield v
            elif isinstance(v, dict):
                for result in self.find(key, v):
                    #print(result)
                    yield result
            elif isinstance(v, list):
                for d in v:
                    #print(d)
                    if isinstance(d, dict):
                        for result in self.find(key, d):
                            #print(result)
                            yield result
    
    def createCompanyObj(self,srcLst):
        for i in range(len(srcLst)):
            print(i)

class WebSite(Enum):
    #INFOCIF = 1
    #AXESOR = 2
    #GUIAEMPRESAS = 3
    #INFOEMPRESA = 4
    #EMPRESITE = 5
    GOOGLE = 6

    def getWebsiteName(value):
        for wb in WebSite:
            if wb.value == value:
                return wb.name

if __name__ == "__main__":
    Wsc = WebScrappingCompany()
    Wsc.main()
    