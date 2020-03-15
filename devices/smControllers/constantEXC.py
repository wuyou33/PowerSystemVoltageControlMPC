from numpy import exp
from numpy import array
from numpy import sign
from numpy import ones
from scipy.sparse import csc_matrix



class constantEXC():
    # AVR standar IEEET1 or IEEE type DC1.
    # For further detail see: https://www.neplan.ch/wp-content/uploads/2015/08/Nep_EXCITERS1.pdf
    def __init__(self):
        self.properties = {
            'init': True,
            'fcall': False, 
            'fxcall': False,
            'fycall': False,
            'fucall': False,
            'gcall': True,
            'gxcall': False,
            'gycall': False,
            'gucall': False ,
            'type': 'gov' 
            }
        #General parameters
        self.n = 0
        self.deviceIdx = {}
        #Parameters
        self.parameters = ['gen0', 'name']
        self.gen0 = []
        self.name = []
        # States
        self.states = []
        #Algebraics
        self.algebraics = []
        # Inputs
        self.inputs = []
        # Generator variables
        self.gen0AVR = [] #Generator AVR equation
        self.bus0Vm = [] #Generator terminal voltage
        self.gen0Vf = [] #Generator voltage field 

        #Constants
        self.vf0 = []       


    #----------------------------------------------------------------------
    def addDevice(self,DAE, Gen ,deviceData):
        #Assing index for state variables.
        for statei in self.states:
            self.__dict__[statei].append(DAE.nx)
            DAE.nx += 1

        #Add device parameters.
        for pari in self.parameters:
            self.__dict__[pari].append(deviceData[pari])

        #Assing index for algebraic variables.
        for algi in self.algebraics:
            self.__dict__[algi].append(DAE.ny)
            DAE.ny += 1
        
        #Assing index for input variables.
        for algi in self.inputs:
            self.__dict__[algi].append(DAE.nu)
            DAE.nu += 1

        #Generator variables
        genIdx = Gen.deviceIdx[self.gen0[-1]]
        self.gen0AVR.append(Gen.gAVR[genIdx])
        self.bus0Vm.append(Gen.bus0Vm[genIdx])
        self.gen0Vf.append(Gen.vf[genIdx])

        #Internal index
        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1
            
    def initialize(self, DAE):       
        #Constants
        self.vf0 = 1 * DAE.y[self.gen0Vf] #Voltage field

    #----------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari])        
    #----------------------------------------------------------------------
    def fcall(self, DAE):
        pass
    #----------------------------------------------------------------------
    def fxcall(self, DAE):
        pass
    #----------------------------------------------------------------------
    def fycall(self, DAE):
        pass
     #----------------------------------------------------------------------
    def fucall(self, DAE): 
        pass
    #----------------------------------------------------------------------
    def gcall(self, DAE):        
        DAE.g[self.gen0AVR] += -1 * self.vf0
    
    def gxcall(self, DAE):
        pass