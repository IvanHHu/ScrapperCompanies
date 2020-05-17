from enum import Enum
from difflib import SequenceMatcher
import re
class Tests:
    def main(self):
        #string = '//-- ..Genral asde SA (), dsdssd . dsdsd € \n  dkksjd'
        #string = 'Jmontero@Ns- Group.Com; Web Www.Nutri'
        #string = self.cleanStringData(string, StringType.Email)
        #self.getType([])
        
        print(SequenceMatcher(None, '216-INNOVA-SL', 'https://empresite.eleconomista.es/216INNOVA24H.html').get_close_matches())
        print(SequenceMatcher(None, '216-INNOVA-SL', 'https://empresite.eleconomista.es/RAMOZA-216.html').get_close_matches())
        
        '''html_text = ' de una empresa>como saber cuánto factura una empresa argentina>datos de facturación de una empresa>como saber cuanto factura mi competencia>sociedad limitada: características>  siguiente >  iniciar sesiónpreferenciasprivacidadcondicione '
        print(html_text)
        print()'''
        #EMpleados
        '''start = html_text.find('cuenta con entre')
        html_text_tmp = html_text[start: len(html_text)]
        end = html_text_tmp.find('empleados') + 9
        dato = re.findall(r'entre [\s0-9]{1,8}\s[a-y]\s[\s0-9a-z]{1,100}.\s', html_text_tmp[0:end])
        dato = str(dato[0]).replace('cuenta con ','') if len(dato) > 0 else ''
        if dato == '':
            start = html_text.find('nº de empleados: ')
            html_text_tmp = html_text[start: len(html_text)]
            end = html_text_tmp.find('teléfono')
            dato = html_text_tmp[0:end]
            dato = str(dato).replace('nº de empleados: ','') if len(dato) > 0 else ''
        print(dato)'''

        #FACTURACION
        '''start = html_text.find('facturación anual')
        if start != -1:
            html_text_tmp = html_text[start: len(html_text)]
            end = html_text_tmp.find('euros')
            dato = re.compile(r'^[\W]+', re.UNICODE).split(html_text_tmp[0:end-1])
            dato = str(dato[0]).replace('facturación anual','') + " €" if len(dato) > 0 else ''
            print(dato)
        else:
            dato = ''
        '''
        #CNAE
        '''start = html_text.find('cnae 2009')
        end = 0
        html_text_tmp = html_text[start: len(html_text)]
        for idx, itm in enumerate(html_text_tmp) :
            if itm =='.' or itm == '|' or itm == '-':
                end = idx
                break
                #print(idx, itm)
        dato = re.compile(r'^[\W]+', re.UNICODE).split(html_text_tmp[0:end])
        if 'http' not in dato[0]:
            dato = str(dato[0])[0:100]
        else:
            dato = ''
        if dato == '':
            start = html_text.find('sector de la empresa:')
            end = 0
            html_text_tmp = html_text[start: len(html_text)]
            end = html_text_tmp.find('nº')
            dato = re.compile(r'^[\W]+', re.UNICODE).split(html_text_tmp[0:end])
            print(dato)'''



    def cleanStringData(self,texto, typeString):
        import re
        print('String Originalv',texto)
        stringLimpio = ''
        if typeString == StringType.AlfaNumerico:
            listaStrings = re.compile(r'\W+', re.UNICODE).split(texto)
            for string in listaStrings:
                print('13 ',string)
                if string != '':
                    stringLimpio += string + ' '
        elif typeString == StringType.AlfaNumericoExt:
            #listaStrings = re.compile(r'^[\W]+', re.UNICODE).split(texto)
            listaStrings = re.compile(r'^[\W]+', re.UNICODE).split(texto)
            for string in listaStrings:           
                print('20 ',string)
                if string != '':
                    stringLimpio += string + ' '
        elif typeString == StringType.Email:
            #listaStrings = re.compile(r'^(\d+)@(\d+)/(\d+)$', re.UNICODE).split(texto)
            texto = texto.replace(' ','')
            email = re.search(r'[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,6}',texto)
            stringLimpio = email.group(0)
            print(stringLimpio)
        elif typeString == StringType.Telefono:
            telefono = re.search(r'[\d\.]+',texto)
            stringLimpio = telefono.group(0)
        elif typeString == StringType.Web:
            pagina = None
            if 'http' in texto:
                pagina = re.search(r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$',texto)
            else:
                pagina = re.search(r'^(www?)\.([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$',texto)
            stringLimpio = pagina.group(0)
        print('Nuevo String ', stringLimpio)
        return stringLimpio

    def getType(self,obj):
        print(type(obj))
        print('list' in str(type(obj)))

class StringType(Enum):
    AlfaNumerico = 1
    AlfaNumericoExt = 2
    Web = 3
    Email = 4
    Telefono = 5

if __name__ == "__main__":
    T = Tests()
    T.main()