from numpy import array
from numpy import ones
from scipy.sparse import csc_matrix

class GovTypeII():
    def __init__(self):
        self.properties = {
            'init': True,
            'fcall': True, 
            'fxcall': True,
            'fycall': False,
            'fucall': False,
            'gcall': True,
            'gxcall': True,
            'gycall': False,
            'gucall': False ,
            'type': 'gov' 
            }
        

        # General parameters
        self.n = 0
        self.deviceIdx = {}

        # Parameters
        self.parameters = ['gen0', 'name', 'R', 'T1', 'T2', 'pmax', 'pmin']
        self.gen0 = []
        self.name = []
        self.R = []
        self.T1 = []
        self.T2 = []
        self.pmax = []
        self.pmin = []
    
        
        # States
        self.states = ['xg']
        self.xg = []

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

        genIdx = Gen.deviceIdx[self.gen0[-1]]
        self.gen0Gov.append(Gen.gGov[genIdx])
        self.gen0pm.append(Gen.pm[genIdx])
        self.genOmega.append(Gen.omega[genIdx])

        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1

    #----------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari]) 

    def initialize(self, dae):
        self.pm0 = dae.y[self.gen0pm]
        dae.x[self.xg] = 0


    #----------------------------------------------------------------------
    def fcall(self, dae):
        omega = dae.x[self.genOmega]
        xg = dae.x[self.xg]

        dae.f[self.xg] = ((1/self.R)*(1 - (self.T1/self.T2))*(1 - omega) - xg)/self.T2

    def fxcall(self, dae):
        #Matrix shape
        nx_nx = (dae.nx, dae.nx)

        dae.fx += csc_matrix(( -1 / self.T2, (self.xg, self.xg)), shape=nx_nx)
        dae.fx += csc_matrix(( -1 * (1/self.R)*(1 - (self.T1/self.T2)) / self.T2, (self.xg, self.genOmega)), shape=nx_nx)

    def fycall(self, dae): pass

    def fucall(self, dae): pass

    def gcall(self, dae): 
        omega = dae.x[self.genOmega]
        xg = dae.x[self.xg]

        #Mechanical torque
        pm = xg + (1/self.R)*(self.T1/self.T2) * (1 - omega) + self.pm0
        dae.g[self.gen0Gov] += -1 * pm

    def gxcall(self, dae):
        #matrix size
        ng_nx = (dae.ng, dae.nx)
        dae.gx += -1*csc_matrix(( ones(self.n), (self.gen0Gov, self.xg)), shape=ng_nx)
        dae.gx += csc_matrix(( (1/self.R)*(self.T1/self.T2), (self.gen0Gov, self.genOmega)), shape=ng_nx)


    def gycall(self,dae): pass

    def gucall(self, dae): pass









    






        
