import OutputData

class Company:
    inputList =[]
    outputList = []

    def __init__(self):
        self.inputList = []
        self.outputList = []

    def setInputList(self, iL = []):
        self.inputList = iL

    def getInputList(self):
        return self.inputList
    
    def setOutputList(self, oL = []):
        self.outputList = oL
    
    def getOutputList(self):
        return self.outputList
    
    def toString(self):
        return "Company { inputList = " + self.inputList +", outputList = " + self.outputList + "}"