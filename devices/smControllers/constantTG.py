from numpy import array
from numpy import ones
from scipy.sparse import csc_matrix

class constantTG():
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
        

        # General parameters
        self.n = 0
        self.deviceIdx = {}

        # Parameters
        self.parameters = ['gen0', 'name']
        self.name = []   
        self.gen0 = []         
        # States
        self.states = []
        # Algebraics
        self.algebraics = []
        # Inputs
        self.inputs = []
        # Generator variables
        self.gen0Gov = []
        self.gen0pm = []
        self.genOmega = []
        #Constants
        self.pm0 = []

    #----------------------------------------------------------------------
    def addDevice(self,dae, Gen ,deviceData):
        #Assing index for state variables.
        for statei in self.states:
            self.__dict__[statei].append(dae.nx)
            dae.nx += 1

        #Add device parameters.
        for pari in self.parameters:
            self.__dict__[pari].append(deviceData[pari])

        #Assing index for algebraic variables.
        for algi in self.algebraics:
            self.__dict__[algi].append(dae.ny)
            dae.ny += 1
        
        #Assing index for input variables.
        for algi in self.inputs:
            self.__dict__[algi].append(dae.nu)
            dae.nu += 1

        #Indexes of generator variables
        genIdx = Gen.deviceIdx[self.gen0[-1]]
        self.gen0Gov.append(Gen.gGov[genIdx])
        self.gen0pm.append(Gen.pm[genIdx])
        self.genOmega.append(Gen.omega[genIdx])
        
        #Device counter
        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1

    #----------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari]) 

    def initialize(self, dae):
        self.pm0 = 1 * dae.y[self.gen0pm]

    #----------------------------------------------------------------------
    def fcall(self, dae):
        pass
    #----------------------------------------------------------------------
    def fxcall(self, dae):
        pass
    #----------------------------------------------------------------------
    def fycall(self, dae): pass
    #----------------------------------------------------------------------
    def fucall(self, dae): pass
    #----------------------------------------------------------------------
    def gcall(self, dae):         
        dae.g[self.gen0Gov] += -1 * self.pm0
    #----------------------------------------------------------------------
    def gxcall(self, dae):
        pass
    #----------------------------------------------------------------------
    def gycall(self,dae): pass
    #----------------------------------------------------------------------
    def gucall(self, dae): pass









    






        
