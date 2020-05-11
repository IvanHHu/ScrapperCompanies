from enum import Enum
class Tests:
    def main(self):
        #string = '//-- ..Genral asde SA (), dsdssd . dsdsd € \n  dkksjd'
        #string = 'Jmontero@Ns- Group.Com; Web Www.Nutri'
        #string = self.cleanStringData(string, StringType.Email)
        self.getType([])

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