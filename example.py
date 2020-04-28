import requests
from lxml import html
from urllib.parse import urlencode
from urllib.parse import quote
from requests.exceptions import RequestException
from difflib import SequenceMatcher
'''import WbUtils

wb = WbUtils.WbUtils()

wb.setPathFile('Book1.csv')
wb.readFile(True)'''

'''s = requests.Session()

s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')

r = s.get('http://httpbin.org/cookies')
r.encoding
print(r.encoding)
r.status_code
print(r.status_code)
r.elapsed
print(r.elapsed)
r.url
print(r.url)

r.history
print(r.history)'''
empresa = {'Buscar':'General Asde'}
print(empresa['Buscar'])
#data = {'txtEmpresaBuscada:': 'General Asde', "opcbusqueda" : "RazonSocial"}
#url = 'http://www.infocif.es/general/empresas-informacion-listado-empresas.asp?Buscar=General%20Asde'
url = 'http://www.infocif.es/general/empresas-informacion-listado-empresas.asp'
resultLinks = ""
#print(url)
try:
    page = requests.get(url, params=empresa, timeout=5)
    page.encoding = 'ISO-8859-1'
    if page.status_code == 200 :
        txtHtml = html.fromstring(page.content)
        print(txtHtml)
        pageCompany = ""
        #searchResult = txtHtml.xpath('//ul[contains(@class, "ulcargos")]/li/a/text()')
        resultLinks = txtHtml.xpath('//ul[contains(@class, "ulcargos")]/li/a')
        ratioMatch=0.0
        indexList = 0
        indexiter = 0
        for link in resultLinks:
            print(link.attrib['href'], link.text_content())
            print(ratioMatch)
            if ratioMatch <= SequenceMatcher(None, empresa['Buscar'], link.text_content()).real_quick_ratio():
                ratioMatch = SequenceMatcher(None, empresa['Buscar'], link.text_content()).real_quick_ratio()
                print('Entre Al IF ', ratioMatch)
                indexList = indexiter
            else:
                print('No Entre Al IF %f', ratioMatch)
            indexiter = indexiter + 1
            print('Indice de lista ', indexList)
            pageCompany = resultLinks[indexList].attrib['href']
        print(pageCompany)
        pageDetail = requests.get(pageCompany)
        pageDetail.encoding = 'ISO-8859-1'
        if pageDetail.status_code == 200 :
            txtHtml = html.fromstring(pageDetail.text)
            print(txtHtml)
            fields = txtHtml.xpath('//div[contains(@id, "fe-informacion-izq")]')
            print(fields)
            for field in fields:
                inputs = field.xpath('//strong[contains(@class, "fwb")]/text()')
                print(inputs)
                datos = field.xpath('//*[contains(@class, "editable")]/text()')
                i =0
                for dato in datos:
                    datos[i] = dato.strip()
                    i = i +1
                print(datos)
                
        #return page.text
        pageDetail.close()
    #return None
    page.close()
except RequestException as e:
    print(e)





'''page = requests.get(url,}
print(page.content)
txthtml = html.fromstring(page.content)
print(txthtml)'''
#This will create a list of buyers:
#buyers = txthtml.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
#prices = txthtml.xpath('//span[@class="item-price"]/text()')

#print('Buyers: ', buyers)
#print('Prices: ', prices)