import requests
from lxml import html
from urllib.parse import urlencode
from urllib.parse import quote
from requests.exceptions import RequestException
from difflib import SequenceMatcher
import csv
import pandas as pd

class SearchData:
        def __init__(self,*argv):
            self.Company_Name=argv[0]
            self.Brand=argv[1]
            self.Website=argv[2]
            self.CIF=argv[3]
            self.Phone_number=argv[4]	
            self.Company_email=argv[5]
            self.Industry=argv[6]
            self.Contacts=argv[7]
            self.Contact_Title=argv[8]
            self.Linkedin=argv[9]	
            self.Facebook=argv[10]
            self.Twitter=argv[11]
            self.Instagram=argv[12]
            self.City=argv[13]
            self.Facturacion_Empleados=argv[14]

            print(self.Brand)

        def FindIntoPage(self,*argv):
            
            empresa = {'Buscar':'General Asde'}
            url = 'http://www.infocif.es/general/empresas-informacion-listado-empresas.asp'
            resultLinks = ""
            try:
                page = requests.get(url, params=empresa, timeout=5)
                page.encoding = 'ISO-8859-1'
                if page.status_code == 200 :
                    txtHtml = html.fromstring(page.content)
                    print(txtHtml)
                    pageCompany = ""
                    resultLinks = txtHtml.xpath('//ul[contains(@class, "ulcargos")]/li/a')
                    ratioMatch=0.0
                    indexList = 0
                    indexiter = 0
                    for link in resultLinks:
                        print(link.attrib['href'], link.text_content())
                        if ratioMatch <= SequenceMatcher(None, empresa['Buscar'], link.text_content()).real_quick_ratio():
                            ratioMatch = SequenceMatcher(None, empresa['Buscar'], link.text_content()).real_quick_ratio()
                            indexList = indexiter
                            print('Indice de lista ', indexList)
                            indexiter += indexiter
                            pageCompany = resultLinks[indexList].attrib['href']
                    print(pageCompany)
                    pageDetail = requests.get(pageCompany)
                    pageDetail.encoding = 'utf-8'
                    if pageDetail.status_code == 200 :
                        txtHtml = html.fromstring(pageDetail.text)
                        fields = txtHtml.xpath('//div[contains(@id, "fe-informacion-izq")]')
                        for field in fields:
                            inputs = field.xpath('//strong[contains(@class, "fwb")]/text()')
                            print(inputs)
                            datos = field.xpath('//*[contains(@class, "editable")]/text()')
                            i =0
                            for dato in datos:
                                datos[i] = str(str(str(dato.strip()).replace(u'\xa0', u'')).replace('  ','')).replace('\r\n','')
                                i = i +1
                            print(datos)
                    pageDetail.close()
                page.close()
                print(self.Brand)
            except RequestException as e:
                print(e)

if __name__ == '__main__':
    ruta =input("\n\nPor favor, pon la ruta donde se encuentra el csv junto con su nombre :")
    with open(ruta, encoding='utf-8') as csvfile:
        columns_times = pd.read_csv(csvfile)
        for index, row in columns_times.iterrows():
                WebScrapingURL = SearchData(str(row['Company Name']),str(row['Brand']),str(row['Website']),str(row['CIF (Fiscal Number in Spain)']), \
                str(row['Phone number']),str(row['Company email']),str(row['Industry']),str(row['Contacts']),str(row["Contact's Title"]),str(row['Linkedin']),str(row['Facebook']), \
                str(row['Twitter']),str(row['Instagram']),str(row['City']),str(row['Facturacion']),str(row['Empleados']))
        WebScrapingURL.FindIntoPage()