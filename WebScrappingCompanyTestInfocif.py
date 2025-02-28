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
import html5lib
from bs4 import BeautifulSoup 
from enum import Enum
from itertools import cycle

class WebScrappingCompany:

    def __init__(self):
        self.Labels = {
            'Nombre':{'INFOCIF':'Nombre','GUIAEMPRESAS':'Nombre','AXESOR':'Nombre','INFOEMPRESA':'Nombre','EMPRESITE':'Razón Social','GOOGLE':'Nombre'},
            'Brand':{'INFOCIF':'Marca','GUIAEMPRESAS':'Marca','AXESOR':'Marca','INFOEMPRESA':'Marca','EMPRESITE':'Marca','GOOGLE':'Marca'},
            'Website':{'INFOCIF':'Web','GUIAEMPRESAS':'Web','AXESOR':'Sitio Web','INFOEMPRESA':'Web','EMPRESITE':'Web','GOOGLE':'Web'},
            'NIF':{'INFOCIF':'CIF','GUIAEMPRESAS':'NIF','AXESOR':'CIF','INFOEMPRESA':'NIF/CIF','EMPRESITE':'CIF','Google':'NIF'},
            'Phone_Number':{'INFOCIF':'Teléfono','GUIAEMPRESAS':'Teléfono','AXESOR':'Teléfono','INFOEMPRESA':'Teléfono','EMPRESITE':'Teléfono','GOOGLE':'Teléfono'},              
            'Email':{'INFOCIF':'Email','GUIAEMPRESAS':'Email','AXESOR':'Email','INFOEMPRESA':'Email','EMPRESITE':'Email','GOOGLE':'Email'},
            'Industry':{'INFOCIF':'Sector','GUIAEMPRESAS':'Sector','AXESOR':'Sector','INFOEMPRESA':'Sector','EMPRESITE':'Actividad','Google':'Sector'},
            'Contacts':{'INFOCIF':'Contacto','GUIAEMPRESAS':'Contactos','AXESOR':'Contactos','INFOEMPRESA':'Contactos','EMPRESITE':'Contactos','GOOGLE':'Contactos'},              
            'Contact_Title':{'INFOCIF':'Cargos_directivos','GUIAEMPRESAS':'Nombre Contacto','AXESOR':'Nombre Contacto','INFOEMPRESA':'Nombre Contacto','EMPRESITE':'Nombre Contacto','Google':'Nombre Contacto'},
            'Linkedin':{'INFOCIF':'Linkedin','GUIAEMPRESAS':'Linkedin','AXESOR':'Linkedin','INFOEMPRESA':'Linkedin','EMPRESITE':'Linkedin','GOOGLE':'Linkedin'},              
            'Facebook':{'INFOCIF':'Facebook','GUIAEMPRESAS':'Facebook','AXESOR':'Facebook','INFOEMPRESA':'Facebook','EMPRESITE':'Facebook','GOOGLE':'Facebook'},
            'Twitter':{'INFOCIF':'Twitter','GUIAEMPRESAS':'Twitter','AXESOR':'Twitter','INFOEMPRESA':'Twitter','EMPRESITE':'Twitter','Google':'Twitter'},
            'Instagram':{'INFOCIF':'Instagram','GUIAEMPRESAS':'Instagram','AXESOR':'Instagram','INFOEMPRESA':'Instagram','EMPRESITE':'Instagram','GOOGLE':'Instagram'},              
            'City':{'INFOCIF':'Domicilio','GUIAEMPRESAS':'Localidad','AXESOR':'Dirección','INFOEMPRESA':'Dirección','EMPRESITE':'Domicilio Social','GOOGLE':'Ciudad'},
            'Facturacion':{'INFOCIF':'Facturacion','GUIAEMPRESAS':'Ventas','AXESOR':'Facturacion','INFOEMPRESA':'Facturacion','EMPRESITE':'Rango de Ventas','Google':'Facturacion'},
            'Empleados':{'INFOCIF':'Nº de empleados','GUIAEMPRESAS':'Empleados','AXESOR':'Empleados','INFOEMPRESA':'Empleados','EMPRESITE':'Rango de Empleados','GOOGLE':'Empleados'}}              
        
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
        self.URLEMPRESITESRCH="search?q="
        self.URLGOOGLESRCH="search"
        self.SRCHNOTFOUND="Empresa no encontrada"
        self.SRCHNOTFOUND2="No se han encontrado resultados"
        self.FoundData = False
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

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
                sourceList.pop(0)
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
                            print('Buscando en ......  ' + str(webSite.name))
                            if self.FoundData == True:
                                self.FoundData = False
                                continue
                            else:
                                self.SearchData(sourceItems, self.buildUrl(webSite.value), company,listOfHeadersInput)
                        companyList.append(company)
                print(companyList)
                csvF.setPathFile("Scrapped.csv")
                #csvF.writeFile(companyList,self.fixHeaders(listOfHeadersInput),True)
                csvF.writeFile(self.fixDataCompany(companyList,listOfHeadersInput),self.fixHeaders(listOfHeadersInput),False)
                
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
        if v == WebSite.INFOCIF.value:
            url = self.URLINFOCIF + self.URLINFOCIFSRCH
            fullUrl['url'] = url
            fullUrl['type'] = 'd'
            fullUrl['src'] = v
            fullUrl['params'] = {'Buscar': '' }
        '''elif v == WebSite.AXESOR.value:
            url = self.URLAXESOR + self.URLAXESORSRCH
            fullUrl['url'] = url
            fullUrl['type'] = 'd'
            fullUrl['src'] = v
            fullUrl['params'] = {'tabActivo':'empresas', 'q':'' }
        elif v == WebSite.GUIAEMPRESAS.value:
            url = self.URLGUIAEMPRESAS + self.URLGUIAEMPRESASSRCH
            fullUrl['url'] = url
            fullUrl['type'] = 's'
            fullUrl['src'] = v
            fullUrl['params'] = {'pathSearch': '' }
        
        elif v == WebSite.INFOEMPRESA.value:
            url = self.URLINFOEMPRESAS + self.URLINFOEMPRESASSRCH
            fullUrl['url'] = url
            fullUrl['type'] = 'd'
            fullUrl['src'] = v
            fullUrl['params'] = {'gateway_id':'ESP_0000', 'q':'' }
    
        elif v == WebSite.EMPRESITE.value:
            url = self.URLEMPRESITE + self.URLEMPRESITESRCH
            fullUrl['url'] = url
            fullUrl['type'] = 's'
            fullUrl['src'] = v
            fullUrl['params'] = {'pathSearch': '' }
        elif v == WebSite.GOOGLE.value:
            url = self.URLGOOGLE + self.URLEMPRESITESRCH
            fullUrl['url'] = url
            fullUrl['type'] = 'd'
            fullUrl['src'] = v
            fullUrl['params'] = {'q': '' }
            '''
        return fullUrl
    
    #Método que obtiene la lista de links arrojados por una busqueda, dependiendo de la página
    def getListLinks(self, txtHtml,srcWeb = 0):
        rL = []
        if srcWeb == WebSite.INFOCIF.value:
            rL = txtHtml.xpath('//ul[contains(@class, "ulcargos")]/li/a')
        '''elif srcWeb == WebSite.GUIAEMPRESAS.value:
            rL = txtHtml.xpath('//table[contains(@class, "ranking_einf")]/tbody/tr/td/a')
        elif srcWeb == WebSite.AXESOR.value:
            rL = txtHtml.xpath('//table[contains(@id, "tablaEmpresas")]/tbody/tr/td/a')
        elif srcWeb == WebSite.INFOEMPRESA.value:
            rL = txtHtml.xpath('//ul[contains(@class, "search-list")]/li/a')
        elif srcWeb == WebSite.EMPRESITE.value:  
            rL = txtHtml.xpath('//ol/li[contains(@class, "resultado_pagina")]/article/div/div/div/a')
        elif srcWeb == WebSite.GOOGLE.value:
            rL = txtHtml.xpath('//div[contains(@class, "rc")]/div/a')'''
        return rL
    
    #Método que obtiene los contenedores del detalle de la información de las empresas dependiendo de la pagina
    def getOutputsContainer(self, webSrc, txtHtml):
        r = None
        if webSrc == WebSite.INFOCIF.value:
            r = txtHtml.xpath('//div[contains(@id, "fe-informacion-izq")]')
        '''elif webSrc == WebSite.GUIAEMPRESAS.value:
            r = txtHtml.xpath('//div[contains(@id,"ficha_iden")]')
        elif webSrc == WebSite.AXESOR.value:
            r = txtHtml.xpath('//table[contains(@id, "tablaInformacionGeneral")]')
        elif webSrc == WebSite.INFOEMPRESA.value:
            r = txtHtml.xpath('//div[contains(@id, "company-data")]')
        elif webSrc == WebSite.EMPRESITE.value:
            r = txtHtml.xpath('//section[contains(@id, "datos-externos1")]')'''
        return r

    #Método que obtiene el matchratio de las cadenas encontradas en la lista de resultados dependiendo del parametro de cada pagina
    def getMatchRatioFromStr(self, srcWeb, params, link):
        matchRatioStr = 0.0
        if srcWeb == WebSite.INFOCIF.value:
            matchRatioStr = SequenceMatcher(None, params['Buscar'], link.text_content()).real_quick_ratio()
        '''elif srcWeb == WebSite.GUIAEMPRESAS.value:
            matchRatioStr = SequenceMatcher(None, params['pathSearch'], link.text_content()).real_quick_ratio()
        elif srcWeb == WebSite.AXESOR.value:
            matchRatioStr = SequenceMatcher(None, params['q'], link.text_content()).real_quick_ratio()
        elif srcWeb == WebSite.INFOEMPRESA.value:
            matchRatioStr = SequenceMatcher(None, params['q'], link.text_content()).real_quick_ratio()
        elif srcWeb == WebSite.EMPRESITE.value:
            matchRatioStr = SequenceMatcher(None, params['pathSearch'], link.text_content()).real_quick_ratio()
        elif srcWeb == WebSite.GOOGLE.value:
            matchRatioStr = SequenceMatcher(None, params['q'], link.text_content()).real_quick_ratio()'''
        return matchRatioStr

    def getOutputDataFromHtml_Google(self, field, Selector, url, item):
        dato = ''
        if Selector == "Link":
            print("Aqui va el link")
            print ("Este el item " + item)
            params = {'q': str(field) + ' ' + item}
            page = requests.get(url, params=params, stream=True)
            page.encoding = 'utf-8'
            url_2 = page.url
            if page.status_code == 200:
                print(url_2)
                soup = BeautifulSoup(page.content, "lxml")
                links = soup.findAll("a")
                for link in links :
                    link_href = link.get('href')
                    if item == "Linkedin" or item == 'Facebook' or item == 'Instagram' or item =='Twitter':
                        if str(item.lower()) + '.com' in link_href:
                            if "url?q=" in link_href and not "webcache" in link_href:
                                dato = link.get('href').split("?q=")[1].split("&sa=U")[0]
                                print(dato)
                                break
                    else:
                        if "url?q=" in link_href and not "webcache" in link_href:
                            dato = link.get('href').split("?q=")[1].split("&sa=U")[0]
                            print(dato)
                            break
        else:
            print("Aqui va la info")
            params = {'q': str(field) + ' ' + item}
            page = requests.get(url, params=params, stream=True)
            page.encoding = 'utf-8'
            url_2 = page.url
            if page.status_code == 200:
                print(url_2)
                soup = BeautifulSoup(page.content,"lxml")
                html_text = str(soup.text).lower()[30:]
                if str(field.lower()) == "localidad" or str(field.lower()) == "cif/nif" or str(field.lower()) == "telefono":
                    limite = 15
                else:
                    limite = 40
                len_dato = 100
                while len_dato > limite:
                    first_point = html_text.find(str(field.lower()))
                    if first_point == -1:
                        break
                    first_data = html_text[int(first_point):]
                    last_point = first_data.find(",")
                    dato = str(first_data[0:int(last_point)])
                    dato = str(dato.split("\n")[0])[int(str(dato.split("\n")[0]).find(":")):int(limite) + int(str(dato.split("\n")[0]).find(":"))]
                    print("El dato es ... " + dato)
                    dato = str(str(dato.replace(':',"")).strip()).title()
                    html_text = first_data[1:]
                    len_dato = len(dato)
        return dato, url_2

    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = html.fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        return proxies

    def getOutputDataFromHtml(self, typeO, field, webSrc):
        oData = []
        if typeO == "Label" :
            if webSrc == WebSite.INFOCIF.value:
                #oData = field.xpath('//strong[contains(@class, "fwb")]/text()')
                count = field.xpath('count(//strong[contains(@class, "fwb")])')
                print("250 count Labels", count)
                for elem in field.xpath('//strong[contains(@class, "fwb")]/text()'):
                    if elem != []:
                        print(elem)
                        if 'Anterior Denominación' not in str(elem):
                            if '-' in str(elem): 
                                strCargos = str(elem)                         
                                end = strCargos.find('-')
                                oData.append(str(str(strCargos[0:end]).strip()).replace(' ','_')) 
                                oData.append('Contacto')
                            else:   
                                oData.append(str(elem).strip('\n'))
            '''elif webSrc == WebSite.GUIAEMPRESAS.value:
                count = field.xpath('count(//th[contains(@class, "td_ficha_univ")])')
                print('Count Labels', count)
                for i in range(1,int(count)):
                    xpath = '//tr[%d]/th[@class="td_ficha_univ"]/p/text()' % i
                    xpaths = '//tr[%d]/th[@class="td_ficha_univ"]/p/strong/text()' % i
                    if field.xpath(xpath) != []:
                        tditem = field.xpath(xpath)
                    else:
                        tditem = field.xpath(xpaths)
                    oData.append(tditem[0])
            elif webSrc == WebSite.AXESOR.value:
                count = field.xpath('count(//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr)')
                xpathEmpVta = '//div[@id="resumen_general"]/p[2]/text()'
                print('Count Labels', count)
                for i in range(1,int(count)):
                    xpath = '//table[contains(@id,"tablaInformacionGeneral")]/tbody//tr[%d]/td[1]/text()' % i
                    if field.xpath(xpath) != []:
                        tditem = field.xpath(xpath)
                    print(str(tditem[0]).strip('\n'))
                    oData.append(str(tditem[0]).strip('\n'))
                if field.xpath(xpathEmpVta) != []:
                    if "empleados" in field.xpath(xpathEmpVta)[0]:
                        oData.append('Empleados')
                    if "ventas" in field.xpath(xpathEmpVta)[0]:
                        oData.append('Facturación')
            elif webSrc == WebSite.INFOEMPRESA.value:     
                count = field.xpath('count(//ul[contains(@class, "list-company-data")]/li)')
                xpathEmpVta = '//div[@id="tab-more-info"]/div/div[1]/p[3]/text()'
                print('Count Labels', count)
                for i in range(1,int(count)):
                    tditem = []
                    xpath = '//li[%d]/span[1]/text()' % i
                    xpathNif = '//li[%d]/span[2]/text()' % i
                    xpathPs = '//li[%d]/p/span/text()' % i
                    if i == 1:
                        if field.xpath(xpathNif) != []:
                            strTitle = str(field.xpath(xpathNif)[0]).split(':')
                            tditem.append(strTitle[0])
                    elif i == 2:
                        if field.xpath(xpath) != []:
                            strTitle = field.xpath(xpath)
                            tditem.append(str(strTitle[1]).replace(':',''))
                    elif i == 4:
                        tditem.append('Direccion')
                    else:
                        if field.xpath(xpath) != []:    
                            strTitle = str(field.xpath(xpath)[0]).split(':') if len(str(field.xpath(xpath)[0]).split(':')) > 1 else field.xpath(xpath)
                            tditem.append(str(strTitle[0]).replace('\n',''))
                        elif field.xpath(xpathPs) != []:
                            strTitle = str(field.xpath(xpathPs)[0]).split(':')
                            tditem.append(strTitle[0])
                    print(tditem)
                    oData.append(tditem[0])
                if field.xpath(xpathEmpVta) != []:
                    strEmpVta = field.xpath(xpathEmpVta)[0]
                    if "empleados" in strEmpVta:
                        oData.append('Empleados')
                    if "facturación" in strEmpVta:
                        oData.append('Facturación')
            elif webSrc == WebSite.EMPRESITE.value:
                count = field.xpath('count(//section[contains(@id, "datos-einforma")]/ul/li)')
                if int(count) == 0:
                    count = field.xpath('count(//section[contains(@id, "datos-externos1")]/ul/li)')
                print('Count Labels', count)
                for i in range(1, int(count)+1):
                    tditem = []
                    xpath = '//li[%d]/strong/text()' % i
                    xpath2 = '//li[%d]/div/strong/text()' % i
                    if field.xpath(xpath) != []:
                        if len(field.xpath(xpath)) > 1:
                            tditem.append(field.xpath(xpath)[0])  
                        else: 
                            tditem = field.xpath(xpath)
                    elif field.xpath(xpath2) != []:
                        tditem = field.xpath(xpath2)
                    print(tditem)
                    oData.append(tditem[0])'''
        else:
            if webSrc == WebSite.INFOCIF.value:
                count = field.xpath('count(//div[@id="fe-informacion-izq"]/p)')
                print("348 Count Data", count)
                xpathCIF = '//h2[contains(@class, "editable")]/text()'
                if field.xpath(xpathCIF) != []:
                    oData.append(field.xpath(xpathCIF)[0])
                for i in range(1,int(count)+1):
                    xpath = '//div[@id="fe-informacion-izq"]/p[%d]/text()' % i
                    xpathLnk = '//div[@id="fe-informacion-izq"]/p[%d]/a/text()' % i
                    if i <= 5:
                        if field.xpath(xpath) != [] and i < 4:
                            valor = self.cleanStringData(field.xpath(xpath)[0],StringType.AlfaNumerico)
                            print('358 ',self.cleanStringData(field.xpath(xpath)[0],StringType.AlfaNumerico))
                            tditem = valor
                            print(xpath)
                            if i == 5:
                                print(field.xpath(xpath))
                            else:
                                print(tditem)
                        elif field.xpath(xpathLnk) != []:
                            tditem = field.xpath(xpathLnk)[0]
                            print(xpathLnk)
                            print(tditem)
                    else:
                        xpathAux = '//div[@id="fe-informacion-izq"]/p[%d]/text()' % (i-5)
                        if field.xpath(xpathAux) != []:
                            valorXpthAux = self.cleanStringData(field.xpath(xpathAux)[1],StringType.AlfaNumerico)
                            #print('367 Nombre Contacto',self.cleanStringData(field.xpath(xpathAux)[1],StringType.AlfaNumerico))
                            if 'p[3]' in xpathAux:
                                valorLabel = field.xpath('//*[@id="fe-informacion-izq"]/strong[3]/text()')[1]
                                print('370 Etiqueta', valorLabel)
                                if '-' in valorLabel:                          
                                    start = valorLabel.find('-')+2
                                    print('373 Cargo:',valorLabel[start:len(valorLabel)])
                                    oData.append(valorLabel[start:len(valorLabel)])
                                    tditem = valorXpthAux
                            else:
                                tditem = valorXpthAux
                            print('378 ',xpathAux)
                            print('379 ',tditem)
                    oData.append(tditem)
            '''elif webSrc == WebSite.GUIAEMPRESAS.value:
                count = field.xpath('count(//td[contains(@class, "td_ficha_univ")])')
                print('Count Data', count)
                for i in range(1,int(count)):
                    xpath = '//tr[%d]/td[@class="td_ficha_univ"]/text()' % i
                    xpaths = '//tr[%d]/td[@class="td_ficha_univ"]/span/text()' % i
                    xpathb = '//tr[%d]/td[@class="td_ficha_univ"]/button/text()' % i
                    xpathEmp = '//p[@id="bloque-empleados"]/text()'
                    xpathVta = '//p[@id="bloque-ventas"]/text()'
                    if field.xpath(xpath) != []:
                        tditem = field.xpath(xpath)
                    elif field.xpath(xpaths) != []:
                        tditem = field.xpath(xpaths)
                    elif field.xpath(xpathb) != []:
                        if 'empleados' in str(field.xpath(xpathb)[0]) and field.xpath(xpathEmp) != []:
                            tditem = field.xpath(xpathEmp)
                        elif 'ventas' in str(field.xpath(xpathb)[0]) and field.xpath(xpathVta) != []:
                            tditem = field.xpath(xpathVta)
                        else:
                            tditem = field.xpath(xpathb)
                    oData.append(tditem[len(tditem)-1] if len(tditem)>1 else tditem[0])
            elif webSrc == WebSite.AXESOR.value:
                count = field.xpath('count(//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr)')
                xpathEmpVta = '//div[@id="resumen_general"]/p[2]/text()'
                print('Count Data', count)
                for i in range(1,int(count)):
                    xpath = '//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr[%d]/td[2]/text()' % i
                    xpathH3 = '//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr[%d]/td[2]/h3/text()' % i
                    xpaths = '//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr[%d]/td[2]/span/text()' % i
                    xpaths2 = '//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr[%d]/td[2]/span/span' % i
                    cntSpans = field.xpath('count(//table[contains(@id,"tablaInformacionGeneral")]/tbody/tr[%d]/td[2]/span/span)' % i)

                    if (int(cntSpans) > 0):
                        if field.xpath(xpaths2) != []:
                            strSpan = ''
                            for span in field.xpath(xpaths2):                                
                                strSpan += span.xpath('text()')[0]                                
                            tditem[0] = str(strSpan).replace(',', ', ')
                    else:
                        if field.xpath(xpath) != []:
                            tditem = field.xpath(xpath)
                        elif field.xpath(xpathH3) != []:
                            tditem = field.xpath(xpathH3)
                        elif field.xpath(xpaths) != []:                        
                            if len(field.xpath(xpaths)) > 1:
                                tditem[0]= ''.join([str(elem).strip() for elem in field.xpath(xpaths)])
                            else:
                                tditem = field.xpath(xpaths)
                    oData.append(str(str(tditem[0]).strip('\xa0')).strip())
                if field.xpath(xpathEmpVta) != []:
                    strEmp = field.xpath(xpathEmpVta)[0]
                    if "empleados" in strEmp:
                        start = strEmp.find('empleados') + 13
                        end = strEmp.find('importe') -6
                        print("333 ", strEmp[start:end])
                        oData.append(strEmp[start:end]) 
                    if "ventas de entre" in strEmp:
                        start = strEmp.find('ventas') + 10
                        end = strEmp.find('€.') + 1
                        print("342 ", strEmp[start:end])
                        oData.append(strEmp[start:end]) 
                    elif "ventas de más de" in strEmp:
                        start = strEmp.find('ventas') + 10
                        end = strEmp.find('€.') + 1 
                        print("347 ", strEmp[start:end])
                        oData.append(strEmp[start:end])   
            elif webSrc == WebSite.INFOEMPRESA.value:
                count = field.xpath('count(//ul[contains(@class, "list-company-data")]/li)')
                xpathEmpVta = '//div[@id="tab-more-info"]/div/div[1]/p[3]/text()'
                print('Count Data', count)
                for i in range(1,int(count)):
                    tditem = []
                    xpath = '//li[%d]/span[2]/text()' % i
                    xpath2 = '//li[%d]/span[1]/text()' % i
                    xpathNif = '//li[%d]/span[2]/text()' % i
                    xpathPs = '//li[%d]/p/span/text()' % i
                    if i == 1:
                        if field.xpath(xpathNif) != []:
                            strTitle = str(field.xpath(xpathNif)[0]).split(':')
                            tditem.append(str(strTitle[1]).strip())
                    elif i == 2:
                        if field.xpath(xpath) != []:
                            strTitle = field.xpath(xpath)
                            tditem.append(strTitle[0])
                    elif i == 4:
                        strTitle = field.xpath(xpathPs)
                        tditem.append(str(strTitle[0]).replace('\n',''))
                    else:
                        print('272 ' , field.xpath(xpath2))
                        if field.xpath(xpath2) != []:                               
                            strTitle = str(field.xpath(xpath2)[0]).split(':') if len(str(field.xpath(xpath2)[0]).split(':')) > 1 else field.xpath(xpath2)
                            tditem.append(strTitle[1])
                        elif field.xpath(xpathPs) != []:
                            strTitle = str(field.xpath(xpathPs)[0]).split(':')
                            tditem.append(strTitle[0])
                    print(tditem)
                    oData.append(tditem[0])
                if field.xpath(xpathEmpVta) != []:
                    strEmp = field.xpath(xpathEmpVta)[0]
                    if "empleados" in strEmp:
                        if "cuenta con entre" in strEmp:
                            start = strEmp.find('cuenta con') + 10
                            end = strEmp.find('empleados')
                            print("393 ", strEmp[start:end])
                            oData.append(strEmp[start:end])   
                        elif "cuenta con más" in strEmp:
                            start = strEmp.find('cuenta con') + 10
                            end = strEmp.find('empleados')
                            print("398 ", strEmp[start:end])
                            oData.append(strEmp[start:end])
                    if "facturación anual de entre" in strEmp:
                        start = strEmp.find('facturación anual de entre') + 21
                        end = strEmp.find('euros.')
                        print("403 ", strEmp[start:end])
                        oData.append(strEmp[start:end] + "€")
                    elif "facturación anual de más" in strEmp:
                        start = strEmp.find('facturación anual de más') + 20
                        end = strEmp.find('euros.')
                        print("403 ", strEmp[start:end])
                        oData.append(strEmp[start:end] + "€")
            elif webSrc == WebSite.EMPRESITE.value:
                count = field.xpath('count(//section[contains(@id, "datos-einforma")]/ul/li)')
                if int(count) == 0:
                    count = field.xpath('count(//section[contains(@id, "datos-externos1")]/ul/li)')
                print('Count Data', count)
                for i in range(1, int(count)+1):
                    tditem = []
                    
                    xpath = '//li[%d]/div/span/text()' % i
                    xpath2 = '//li[%d]/div/text()' % i
                    xpath3 = '//li[%d]/span/text()' % i
                    xpathDivs = '//li[%d]/span/div' % i
                    xpathMail = '//li[%d]/a/span/text()' % i
                    xpathWeb = '//li[%d]/span/a/text()' % i
                    xpathForma = '//li[%d]/text()' % i
                    cntDivs = field.xpath('count(//li[%d]/span/div)' % i)
                    if (int(cntDivs) > 0):
                        if field.xpath(xpathDivs) != []:
                            strDivs = ''
                            for div in field.xpath(xpathDivs):
                                strDivs += div.xpath('text()')[0] 
                            tditem.append(str(strDivs).replace(',', ', '))
                    else:
                        if field.xpath(xpath) != []:
                            tditem = field.xpath(xpath)
                        elif field.xpath(xpath2) != []:
                            tditem = field.xpath(xpath2)
                        elif field.xpath(xpath3) != []:
                            tditem = field.xpath(xpath3)
                        elif field.xpath(xpathMail) != []:
                            tditem = field.xpath(xpathMail)
                        elif field.xpath(xpathWeb) != []:
                            tditem = field.xpath(xpathWeb)
                        elif field.xpath(xpathForma) != []:
                            tditem = field.xpath(xpathForma)
                    print(tditem)
                    oData.append(str(tditem[0]).strip(': '))'''
        return oData

    def cleanStringData(self,texto, typeString):
        import re
        stringLimpio = ''
        if typeString == StringType.AlfaNumerico:
            listaStrings = re.compile(r'\W+ ', re.UNICODE).split(texto)
            for string in listaStrings:
                if string != '':
                    stringLimpio += string + ' '
        elif typeString == StringType.AlfaNumericoExt:
            listaStrings = re.compile(r'\W,.-€', re.UNICODE).split(texto)
            for string in listaStrings:
                if string != '':
                    stringLimpio += string + ' '
        elif typeString == StringType.Email:
            listaStrings = re.compile(r'\b[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,6}\b', re.UNICODE).split(texto)
            for string in listaStrings:
                if string != '':
                    stringLimpio += string + ' '
        elif typeString == StringType.Telefono:
            listaStrings = re.compile(r'\b[\d\.]+\b', re.UNICODE).split(texto)
            for string in listaStrings:
                if string != '':
                    stringLimpio += string + ' '
        elif typeString == StringType.Web:
            listaStrings = re.compile(r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$', re.UNICODE).split(texto)
            for string in listaStrings:
                if string != '':
                    stringLimpio += string + ' '
        return stringLimpio

    def fixHeaders(self, headers = []):
        headersFixed = []
        if headers != []:
            for header in headers:
                headersFixed.append(header)
                headersFixed.append('Fuente')
        #print(headersFixed)
        return headersFixed

    def fixDataCompany(self, companies = [], headers = []):
        dataFixed = []
        if companies != []:
            for company in companies:
                companyFix = []
                for header in headers:
                    #print('585 ',company[header]['valor'])print('585 ',company[header]['valor'])
                    companyFix.append(company[header]['valor'])
                    companyFix.append(company[header]['fuente'])
                #dataFixed[headers[0]] = companyFix
                dataFixed.append(companyFix)
        print(dataFixed)
        return dataFixed

    def SearchData(self, sourceItems, fullUrl={}, company={}, headersCsv={}):
        #outputList = []
        outputList = {}
        for index, item in enumerate(sourceItems):
            item_2 = item.replace('SL','Sociedad Limitada').replace('Sl','Sociedad Limitada').replace('sl','Sociedad Limitada').replace('sL','Sociedad Limitada')
            item_2 = item_2.replace('SA','Sociedad Anonima').replace('Sa','Sociedad Anonima').replace('sa','Sociedad Anonima').replace('sA','Sociedad Anonima')
            #if item != '':
            if item != '' and item != 'N/A':
                if item != 'N/A':
                    print('Tomando el dato [' + item_2 + '] para la busqueda.') 
                    url= fullUrl['url']
                    #print('URL de busqueda: ' + url)
                    params = None
                    IsGOOGLE = False
                    NoEntrar = True
                    if fullUrl['type'] == 'd':
                        if fullUrl['src'] == WebSite.INFOCIF.value:
                            params = fullUrl['params']
                            params['Buscar'] = item
                        '''elif fullUrl['src'] == WebSite.AXESOR.value:
                            params = fullUrl['params']
                            params['q'] = item
                        elif fullUrl['src'] == WebSite.INFOEMPRESA.value:
                            params = fullUrl['params']
                            params['q'] = item
                        elif fullUrl['src'] == WebSite.GOOGLE.value:
                            params = fullUrl['params']
                            params['q'] = item
                            IsGOOGLE = True
                            NoEntrar = False'''
                    else:
                        params = fullUrl['params']
                        params['pathSearch'] = str(item).replace(u' ',u'-') + '/'
                    resultLinks = ""
                    try:
                        if IsGOOGLE == False and NoEntrar == True:
                            page = None
                            proxies = {'https': 'https://user-59460:user-59460@31.220.33.13:1212'}
                            proxy_pool = cycle(proxies)
                            proxy = next(proxy_pool)
                            if fullUrl['type'] == 'd':
                                page = requests.get(url, params=params, proxies=proxies, timeout=5)
                                #page = requests.get(url, params=params, timeout=5)
                            else:
                                print(url+params['pathSearch'])
                                page = requests.get(url+params['pathSearch'], proxies=proxies, timeout=5)
                                #page = requests.get(url+params['pathSearch'], timeout=5)
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
                                            strMatchVal = self.getMatchRatioFromStr(fullUrl['src'],params,link)
                                            if ratioMatch <= strMatchVal:
                                                ratioMatch = strMatchVal
                                                indexList = indexiter
                                                print('# 470 Indice de lista de resultados: ', indexList)
                                                pageCompany = self.cleanUrl(resultLinks[indexList].attrib['href'],fullUrl['src'])
                                            indexiter = indexiter+1
                                        print('# 474 ',pageCompany)
                                        return self.getRequestPageDetailInfo(pageCompany, fullUrl, company, headersCsv,item)
                                        '''pageDetail = requests.get(pageCompany)
                                        pageDetail.encoding = 'utf-8'
                                        if pageDetail.status_code == 200 :
                                            txtHtml = html.fromstring(pageDetail.text)
                                            fields = self.getOutputsContainer(fullUrl['src'],txtHtml)
                                            for field in fields:
                                                outputs = self.getOutputDataFromHtml("Label",field,fullUrl['src'])
                                                h = 0
                                                for outputHdr in outputs:
                                                    outputs[h] = str(str(str(str(outputHdr.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')).replace('\n','')
                                                    h = h + 1
                                                print('#489 labels: ',outputs)
                                                datos = self.getOutputDataFromHtml("Data",field,fullUrl['src'])
                                                x = 0
                                                for dato in datos:
                                                    datos[x] = str(str(str(dato.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')
                                                    x = x +1
                                                print('#497 datos: ',datos)
                                                for i, e in enumerate(outputs):
                                                    print(i, e)
                                                    if self.Labels['Nombre'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[0]]['valor'] == '' or company[headersCsv[0]]['fuente'] == ''):
                                                        company[headersCsv[0]]['valor'] = datos[i] if company[headersCsv[0]]['valor'] == '' else company[headersCsv[0]]['valor']
                                                        company[headersCsv[0]]['fuente'] = pageCompany
                                                    if self.Labels['Brand'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[1]]['valor'] == '' or company[headersCsv[1]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[1]]['valor'] = datos[i] if company[headersCsv[1]]['valor'] == '' else company[headersCsv[1]]['valor']
                                                        company[headersCsv[1]]['fuente'] = pageCompany
                                                    if self.Labels['Website'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[2]]['valor'] == '' or company[headersCsv[2]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[2]]['valor'] = datos[i] if company[headersCsv[2]]['valor'] == '' else company[headersCsv[2]]['valor']
                                                        company[headersCsv[2]]['fuente'] = pageCompany
                                                    if self.Labels['NIF'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[3]]['valor'] == '' or company[headersCsv[3]]['fuente'] == ''):
                                                        if datos[i] == "-" or  "   " in datos[i]:
                                                            first_letter = ''
                                                            if " Anonima" in item:
                                                                first_letter = "A"
                                                            else:
                                                                first_letter = "B"
                                                            if str(datos[i])[0] == first_letter:
                                                                self.FoundData == True
                                                                company[headersCsv[3]]['valor'] = datos[i] if company[headersCsv[3]]['valor'] == '' else company[headersCsv[3]]['valor']
                                                                company[headersCsv[3]]['fuente'] = pageCompany
                                                    if self.Labels['Phone_Number'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[4]]['valor'] == '' or company[headersCsv[4]]['fuente'] == ''):
                                                       if str(datos[i])[0:3] != 902 or str(datos[i])[0:3] != 901:
                                                        self.FoundData == True
                                                        company[headersCsv[4]]['valor'] = datos[i] if company[headersCsv[4]]['valor'] == '' else company[headersCsv[4]]['valor']
                                                        company[headersCsv[4]]['fuente'] = pageCompany
                                                    if self.Labels['Email'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[5]]['valor'] == '' or company[headersCsv[5]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[5]]['valor'] = datos[i] if company[headersCsv[5]]['valor'] == '' else company[headersCsv[5]]['valor']
                                                        company[headersCsv[5]]['fuente'] = pageCompany
                                                    if self.Labels['Industry'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[6]]['valor'] == '' or company[headersCsv[6]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[6]]['valor'] = datos[i] if company[headersCsv[6]]['valor'] == '' else company[headersCsv[6]]['valor']
                                                        company[headersCsv[6]]['fuente'] = pageCompany
                                                    if self.Labels['Contacts'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[7]]['valor'] == '' or company[headersCsv[7]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[7]]['valor'] = datos[i] if company[headersCsv[7]]['valor'] == '' else company[headersCsv[7]]['valor']
                                                        company[headersCsv[7]]['fuente'] = pageCompany
                                                    if self.Labels['Contact_Title'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[8]]['valor'] == '' or company[headersCsv[8]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[8]]['valor'] = datos[i] if company[headersCsv[8]]['valor'] == '' else company[headersCsv[8]]['valor']
                                                        company[headersCsv[8]]['fuente'] = pageCompany
                                                    if self.Labels['City'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[13]]['valor'] == '' or company[headersCsv[13]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[13]]['valor'] = datos[i] if company[headersCsv[13]]['valor'] == '' else company[headersCsv[13]]['valor']
                                                        company[headersCsv[13]]['fuente'] = pageCompany
                                                    if self.Labels['Facturacion'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[14]]['valor'] == '' or company[headersCsv[14]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[14]]['valor'] = datos[i] if company[headersCsv[14]]['valor'] == '' else company[headersCsv[14]]['valor']
                                                        company[headersCsv[14]]['fuente'] = pageCompany
                                                    if self.Labels['Empleados'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[15]]['valor'] == '' and company[headersCsv[15]]['fuente'] == ''):
                                                        self.FoundData == True
                                                        company[headersCsv[15]]['valor'] = datos[i] if company[headersCsv[15]]['valor'] == '' else company[headersCsv[15]]['valor']
                                                        company[headersCsv[15]]['fuente'] = pageCompany
                                                break
                                        pageDetail.close()
                                        return company'''
                                    else:
                                        xpthPageInfocif = '//*[@id="fe-informacion"]/div[1]/h2/span[2]/text()'
                                        xpthPageAxesor = '//*[@id="informacion_general"]/header/h2/text()'
                                        xpthPageInfoEmpresa = '//*[@id="company-data"]/div/div/div/h2/text()'
                                        xpthPageGuiaEmpresa = '//*[@id="einf"]/div[4]/div/a/span/text()'
                                        xpthPageEmpresite = '//*[@id="datos-externos"]'
                                        if (txtHtml.xpath(xpthPageInfocif) != []) or (txtHtml.xpath(xpthPageAxesor)) or (txtHtml.xpath(xpthPageInfoEmpresa)!=[]) or (txtHtml.xpath(xpthPageGuiaEmpresa)!= []) or (txtHtml.xpath(xpthPageEmpresite)!= []):
                                            print('745 ', page.url)
                                            return self.getRequestPageDetailInfo(page.url,fullUrl, company, headersCsv,item)
                                        else:
                                            print('Nada que mostrar')
                                            continue
                                    #break
                            else:
                                print(page.status_code)
                            page.close()
                        '''elif IsGOOGLE == True and NoEntrar == False:
                            if company[headersCsv[2]]['valor'] == '' or company[headersCsv[2]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Website","Link", url, item)
                                company[headersCsv[2]]['valor'] = outputs if company[headersCsv[2]]['valor'] == '' else outputs
                                company[headersCsv[2]]['fuente'] = url_2
                            if company[headersCsv[0]]['valor'] == '' or company[headersCsv[0]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Empresa:","Info", url, item)
                                company[headersCsv[0]]['valor'] = outputs if company[headersCsv[0]]['valor'] == '' else outputs
                                company[headersCsv[0]]['fuente'] = url_2
                            if company[headersCsv[1]]['valor'] == '' or company[headersCsv[1]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Denominacion","Info", url, item)
                                company[headersCsv[1]]['valor'] = outputs if company[headersCsv[1]]['valor'] == '' else outputs
                                company[headersCsv[1]]['fuente'] = url_2
                            if company[headersCsv[3]]['valor'] == '' or company[headersCsv[3]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("CIF/NIF:","Info", url, item)
                                company[headersCsv[3]]['valor'] = outputs if company[headersCsv[3]]['valor'] == '' else outputs
                                company[headersCsv[3]]['fuente'] = url_2
                            if company[headersCsv[4]]['valor'] == '' or company[headersCsv[4]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Telefono","Info", url, item)
                                company[headersCsv[4]]['valor'] = outputs if company[headersCsv[4]]['valor'] == '' else outputs
                                company[headersCsv[4]]['fuente'] = url_2
                            if company[headersCsv[5]]['valor'] == '' or company[headersCsv[5]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Email","Info", url, item)
                                company[headersCsv[5]]['valor'] = outputs if company[headersCsv[5]]['valor'] == '' else outputs
                                company[headersCsv[5]]['fuente'] = url_2
                            if company[headersCsv[6]]['valor'] == '' or company[headersCsv[6]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("CNAE 2009:","Info", url, item)
                                company[headersCsv[6]]['valor'] = outputs if company[headersCsv[6]]['valor'] == '' else outputs
                                company[headersCsv[6]]['fuente'] = url_2
                            if company[headersCsv[7]]['valor'] == '' or company[headersCsv[7]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Contacts","Info", url, item)
                                company[headersCsv[7]]['valor'] = outputs if company[headersCsv[7]]['valor'] == '' else outputs
                                company[headersCsv[7]]['fuente'] = url_2
                            if company[headersCsv[8]]['valor'] == '' or company[headersCsv[8]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Contacts Title","Info", url, item)
                                company[headersCsv[8]]['valor'] = outputs if company[headersCsv[8]]['valor'] == '' else outputs
                                company[headersCsv[8]]['fuente'] = url_2
                            if company[headersCsv[9]]['valor'] == '' or company[headersCsv[9]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Linkedin","Link", url, item)
                                company[headersCsv[9]]['valor'] = outputs if company[headersCsv[9]]['valor'] == '' else outputs
                                company[headersCsv[9]]['fuente'] = url_2
                            if company[headersCsv[10]]['valor'] == '' or company[headersCsv[10]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Facebook","Link", url, item)
                                company[headersCsv[10]]['valor'] = outputs if company[headersCsv[10]]['valor'] == '' else outputs
                                company[headersCsv[10]]['fuente'] = url_2
                            if company[headersCsv[11]]['valor'] == '' and company[headersCsv[11]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Twitter","Link", url, item)
                                company[headersCsv[11]]['valor'] = outputs if company[headersCsv[11]]['valor'] == '' else outputs
                                company[headersCsv[11]]['fuente'] = url_2
                            if company[headersCsv[12]]['valor'] == '' or company[headersCsv[12]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Instagram","Link", url, item)
                                company[headersCsv[12]]['valor'] = outputs if company[headersCsv[12]]['valor'] == '' else outputs
                                company[headersCsv[12]]['fuente'] = url_2
                            if company[headersCsv[13]]['valor'] == '' or company[headersCsv[13]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Localidad:","Info", url, item)
                                company[headersCsv[13]]['valor'] = outputs if company[headersCsv[13]]['valor'] == '' else outputs
                                company[headersCsv[13]]['fuente'] = url_2
                            if company[headersCsv[14]]['valor'] == '' or company[headersCsv[14]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Facturacion:","Info", url, item)
                                company[headersCsv[14]]['valor'] = outputs if company[headersCsv[14]]['valor'] == '' else outputs
                                company[headersCsv[14]]['fuente'] = url_2
                            if company[headersCsv[15]]['valor'] == '' and company[headersCsv[15]]['fuente'] == '':
                                self.FoundData == True
                                outputs, url_2 = self.getOutputDataFromHtml_Google("Empleados:","Info", url, item)
                                company[headersCsv[15]]['valor'] = outputs if company[headersCsv[15]]['valor'] == '' else outputs
                                company[headersCsv[15]]['fuente'] = url_2'''
                    except RequestException as e:
                        print('Exception: ', e)
    
    def getRequestPageDetailInfo(self, pageCompany, fullUrl, company, headersCsv,item):
        proxies = proxies = {'https': 'https://user-59460:user-59460@31.220.33.13:1212'}
        proxy_pool = cycle(proxies)
        proxy = next(proxy_pool)
        requests.encoding = 'ISO-8859-1'
        pageDetail = requests.get(pageCompany,proxies=proxies)
        #pageDetail = requests.get(pageCompany)
        pageDetail.encoding = 'ISO-8859-1'
        if pageDetail.status_code == 200 :
            txtHtml = html.fromstring(pageDetail.text)
            fields = self.getOutputsContainer(fullUrl['src'],txtHtml)
            for field in fields:
                outputs = self.getOutputDataFromHtml("Label",field,fullUrl['src'])
                h = 0
                for outputHdr in outputs:
                    outputs[h] = str(str(str(str(outputHdr.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')).replace('\n','')
                    h = h + 1
                print('#489 labels: ',outputs)
                datos = self.getOutputDataFromHtml("Data",field,fullUrl['src'])
                x = 0
                for dato in datos:
                    datos[x] = str(str(str(dato.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')
                    x = x +1
                print('#497 datos: ',datos)
                for i, e in enumerate(outputs):
                    print(i, e)
                    if self.Labels['Nombre'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[0]]['valor'] == '' or company[headersCsv[0]]['fuente'] == ''):
                        company[headersCsv[0]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumerico) if company[headersCsv[0]]['valor'] == '' else self.cleanStringData(company[headersCsv[0]]['valor'],StringType.AlfaNumerico)
                        company[headersCsv[0]]['fuente'] = pageCompany
                        print('Nombre: ', company[headersCsv[0]]['valor'])
                        print("company[headersCsv[0]]['valor']")
                    if self.Labels['Brand'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[1]]['valor'] == '' or company[headersCsv[1]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[1]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumerico) if company[headersCsv[1]]['valor'] == '' else self.cleanStringData(company[headersCsv[1]]['valor'],StringType.AlfaNumerico)
                        company[headersCsv[1]]['fuente'] = pageCompany
                        print('Brand: ', company[headersCsv[1]]['valor'])
                        print("company[headersCsv[1]]['valor']")
                    if self.Labels['Website'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[2]]['valor'] == '' or company[headersCsv[2]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[2]]['valor'] = datos[i] if company[headersCsv[2]]['valor'] == '' else company[headersCsv[2]]['valor']
                        company[headersCsv[2]]['fuente'] = pageCompany
                        print('WebSite: ', company[headersCsv[2]]['valor'])
                        print("company[headersCsv[2]]['valor']")
                    if self.Labels['NIF'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[3]]['valor'] == '' or company[headersCsv[3]]['fuente'] == ''):
                        #if datos[i] == "-" or  "   " in datos[i]:
                        first_letter = ''
                        if " Anonima" in item:
                            first_letter = "A"
                        else:
                            first_letter = "B"
                        #if str(datos[i])[0] == first_letter:
                        if str(self.cleanStringData(datos[i],StringType.AlfaNumerico))[0] == first_letter:
                            self.FoundData == True
                            company[headersCsv[3]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumerico) if company[headersCsv[3]]['valor'] == '' else self.cleanStringData(company[headersCsv[3]]['valor'],StringType.AlfaNumerico)
                            company[headersCsv[3]]['fuente'] = pageCompany
                            print('NIF: ', company[headersCsv[3]]['valor'])
                            print("company[headersCsv[3]]['valor']")
                    if self.Labels['Phone_Number'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[4]]['valor'] == '' or company[headersCsv[4]]['fuente'] == ''):
                        if str(datos[i])[0:3] != 902 or str(datos[i])[0:3] != 901:
                            self.FoundData == True
                            company[headersCsv[4]]['valor'] = self.cleanStringData(datos[i],StringType.Telefono) if company[headersCsv[4]]['valor'] == '' else self.cleanStringData(company[headersCsv[4]]['valor'],StringType.Telefono)
                            company[headersCsv[4]]['fuente'] = pageCompany
                            print('Telefono: ', company[headersCsv[4]]['valor'])
                            print("company[headersCsv[4]]['valor']")
                    if self.Labels['Email'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[5]]['valor'] == '' or company[headersCsv[5]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[5]]['valor'] = self.cleanStringData(datos[i],StringType.Email) if company[headersCsv[5]]['valor'] == '' else self.cleanStringData(company[headersCsv[5]]['valor'],StringType.Email)
                        company[headersCsv[5]]['fuente'] = pageCompany
                        print('Email: ', company[headersCsv[5]]['valor'])
                        print("company[headersCsv[5]]['valor']")
                    if self.Labels['Industry'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[6]]['valor'] == '' or company[headersCsv[6]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[6]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumericoExt) if company[headersCsv[6]]['valor'] == '' else self.cleanStringData(company[headersCsv[6]]['valor'],StringType.AlfaNumericoExt)
                        company[headersCsv[6]]['fuente'] = pageCompany
                        print('Industry: ', company[headersCsv[6]]['valor'])
                        print("company[headersCsv[6]]['valor']")
                    if self.Labels['Contacts'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[7]]['valor'] == '' or company[headersCsv[7]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[7]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumerico) if company[headersCsv[7]]['valor'] == '' else self.cleanStringData(company[headersCsv[7]]['valor'],StringType.AlfaNumerico)
                        company[headersCsv[7]]['fuente'] = pageCompany
                        print('Contacto: ', company[headersCsv[7]]['valor'])
                        print("company[headersCsv[7]]['valor']")
                    if self.Labels['Contact_Title'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[8]]['valor'] == '' or company[headersCsv[8]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[8]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumericoExt) if company[headersCsv[8]]['valor'] == '' else self.cleanStringData(company[headersCsv[8]]['valor'],StringType.AlfaNumericoExt)
                        company[headersCsv[8]]['fuente'] = pageCompany
                        print('Cargo: ', company[headersCsv[8]]['valor'])
                        print("company[headersCsv[8]]['valor']")
                    if self.Labels['City'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[13]]['valor'] == '' or company[headersCsv[13]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[13]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumericoExt) if company[headersCsv[13]]['valor'] == '' else self.cleanStringData(company[headersCsv[13]]['valor'],StringType.AlfaNumericoExt)
                        company[headersCsv[13]]['fuente'] = pageCompany
                        print('City: ', company[headersCsv[13]]['valor'])
                        print("company[headersCsv[13]]['valor']")
                    if self.Labels['Facturacion'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[14]]['valor'] == '' or company[headersCsv[14]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[14]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumericoExt) if company[headersCsv[14]]['valor'] == '' else self.cleanStringData(company[headersCsv[14]]['valor'],StringType.AlfaNumericoExt)
                        company[headersCsv[14]]['fuente'] = pageCompany
                        print('Facturacion: ', company[headersCsv[14]]['valor'])
                        print("company[headersCsv[14]]['valor']")
                    if self.Labels['Empleados'][WebSite.getWebsiteName(fullUrl['src'])] in e and (company[headersCsv[15]]['valor'] == '' and company[headersCsv[15]]['fuente'] == ''):
                        self.FoundData == True
                        company[headersCsv[15]]['valor'] = self.cleanStringData(datos[i],StringType.AlfaNumericoExt) if company[headersCsv[15]]['valor'] == '' else self.cleanStringData(company[headersCsv[15]]['valor'],StringType.AlfaNumericoExt)
                        company[headersCsv[15]]['fuente'] = pageCompany
                        print('Empleados: ', company[headersCsv[15]]['valor'], headersCsv[15])
                        print("company[headersCsv[15]]['valor']")
                break
        else:
            print(pageDetail.status_code)
        pageDetail.close()
        return company

    def cleanUrl(self, url, srcWeb):
        if srcWeb == WebSite.INFOEMPRESA.value:
            url = 'http://' + str(url).strip('http://')
        '''elif srcWeb == WebSite.AXESOR.value:
            url = 'http://' + str(url).strip('//')
        elif srcWeb == WebSite.GUIAEMPRESAS.value:
            url = self.URLGUIAEMPRESAS + url
        elif srcWeb == WebSite.INFOEMPRESA.value:
            url = self.URLINFOEMPRESAS + str(url).replace('/es-es/es/','')
        elif srcWeb == WebSite.EMPRESITE.value:
            url = url'''
        
        return url

    def find(self, key, dictionary):
        print(key)
        for k, v in dictionary.iteritems():
            if k == key:
                print(v)
                yield v
            elif isinstance(v, dict):
                for result in self.find(key, v):
                    print(result)
                    yield result
            elif isinstance(v, list):
                for d in v:
                    print(d)
                    if isinstance(d, dict):
                        for result in self.find(key, d):
                            print(result)
                            yield result
    
    def createCompanyObj(self,srcLst):
        for i in range(len(srcLst)):
            print(i)

class WebSite(Enum):
    #GUIAEMPRESAS = 1
    INFOCIF = 2
    '''INFOEMPRESA = 3
    AXESOR = 4
    EMPRESITE = 5
    GOOGLE = 6'''

    def getWebsiteName(value):
        for wb in WebSite:
            if wb.value == value:
                return wb.name

class StringType(Enum):
    AlfaNumerico = 1
    AlfaNumericoExt = 2
    Web = 3
    Email = 4
    Telefono = 5

if __name__ == "__main__":
    Wsc = WebScrappingCompany()
    Wsc.main()
    