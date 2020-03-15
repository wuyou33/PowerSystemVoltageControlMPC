from numpy import array
     
class Tr2W():
    #Note: All parameters are in system base.

    def __init__(self):
        self.properties = {
            'init': False,
            'fcall': False, 
            'fxcall': False,
            'fycall': False,
            'fucall': False,
            'gcall': False,
            'gxcall': False,
            'gycall': False,
            'gucall': False,
            'type': 'line' 
            }
        #General parameters
        self.n = 0
        self.deviceIdx = {}

        #Parameters
        self.name = []
        self.bus0 = []  # bus "from" where the line is connected
        self.bus1 = []  # bus "to" where the line is connected
        self.x = []     # reactance p.u
        self.r = []     # resistance p.u
        self.b = []     # shunt susceptances p.u
        self.g = []     # shunt conductance p.u
        self.ratio1 = [] #Voltage ratio1
        self.ratio2 = [] #Voltage ratio2
        self.shift = [] #Angle shift
        self.status = []
        self.parameters = ['name', 'x', 'r', 'b',  'bus0', 'bus1', 'status', 'ratio1', 'ratio2', 'shift']
        
        #States
        self.states = []

        #Algebraics
        self.algebraics = []

        self.inputs = []
        
        #Algebraics equations
        self.algEquations = []
        #Bus variables and equations
        self.busVariables = ['bus0Idx', 'bus1Idx']
        self.bus0Idx = [] #Bus Idx
        self.bus1Idx = [] #Bus Idx         
        
    def addDevice(self,DAE, Bus, deviceData):
    
        #Add device parameters.
        for pari in self.parameters:
            self.__dict__[pari].append(deviceData[pari])

        #Bus variables and equations
        self.bus0Idx.append(Bus.deviceIdx[self.bus0[-1]])
        self.bus1Idx.append(Bus.deviceIdx[self.bus1[-1]])


        #Internal index
        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1




    def setUp(self):
        
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari])