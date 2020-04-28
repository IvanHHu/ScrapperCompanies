
class OutputData:
    #fieldName = ""
    #fieldSource = ""
    field = {}

    def __init__(self, fN = "", fS = ""):
        #self.fieldName = fN
        #self.fieldSource = fS
        self.field['name'] = fN
        self.field['source'] = fS

    def setFieldName(self, fieldName = ""):
        #self.fieldName = fieldName
        self.field['name'] = fieldName
    
    def getFieldName(self):
        #return self.fieldName
        return self.field['name']

    def setFieldSource(self, fieldSource = ""):
        #self.fieldSource = fieldSource
        self.field['source'] = fieldSource
    
    def getFieldSource(self):
        #return self.fieldSource
        return self.field['source']
    
    def toString(self):
        return "OutputData { fieldName = " + self.field['name'] +", fieldSource = " + self.field['source'] + "}"