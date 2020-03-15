from numpy import array, ones
from scipy.sparse import csc_matrix 

class LoadExp(): #Empiza en mayuscula
    # Note: All parameters in system base
    def __init__(self):
        self.properties = {
            'init': True,
            'fcall': False, 
            'fxcall': False,
            'fycall': False,
            'fucall': False,
            'gcall': True,
            'gxcall': False,
            'gycall': True,
            'gucall': False ,
            'type': 'load' 
            }
        

        #General parameters
        self.n = 0
        self.deviceIdx = {}

        #Parameters
        self.parameters = ['bus0', 'name', 'p', 'q', 'alpha', 'beta', 'status']
        self.bus0 = [] #Bus the load is connected to.
        self.name = [] #Unique ID for each device.
        self.p = [] #Initial active load
        self.q = [] #Initial reactive load
        self.alpha = [] #Exponent
        self.beta = [] #Exponent
        self.status = [] #Load status
        
        #Constants
        self.vm0 = array([]) #Initial voltage magnitude.
        #States
        self.states = []

        #Algebraics
        self.algebraics = []
        self.inputs = []
        
        #Algebraics equations
        self.algEquations = []


        #Bus variables and equations
        self.busVariables = ['bus0Idx', 'bus0Vm', 'bus0Va', 'bus0ph', 'bus0qh']
        self.bus0Idx = [] #Bus Idx
        self.bus0Vm = [] #Bus voltage magnitude Index
        self.bus0Va = [] #Bus voltage angle Index        
        self.bus0ph = [] #Bus injected active power index
        self.bus0qh = [] #Bus injected reactive power index

        #Connectivity matrix
        self.Cp = csc_matrix([])
        self.Cq = csc_matrix([])        


    def addDevice(self, DAE, Bus, deviceData):       
        
        #Add device parameters.
        for pari in self.parameters:
            self.__dict__[pari].append(deviceData[pari])

        #Assing index for state variables.
        for statei in self.states:
            self.__dict__[statei].append(DAE.nx)
            DAE.nx += 1
        #Assing index for algebraic variables.
        for algi in self.algebraics:
            self.__dict__[algi].append(DAE.ny)
            DAE.ny += 1

        #Bus variables and equations
        busIdx = Bus.deviceIdx[self.bus0[-1]]
        self.bus0Idx.append(busIdx)
        self.bus0Vm.append(Bus.vm[busIdx])
        self.bus0Va.append(Bus.va[busIdx])
        self.bus0ph.append(Bus.ph[busIdx])
        self.bus0qh.append(Bus.qh[busIdx])

        #Internal index
        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1

    #----------------------------------------------------------------------   
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari])

        
    #----------------------------------------------------------------------
    def initialize(self, DAE):
        #Get initial voltage magnitude
        self.vm0 = DAE.y[self.bus0Vm]
        #Connectivity matrix
        self.Cp = csc_matrix((ones(self.n), (self.bus0ph, range(self.n))), shape = (DAE.ng, self.n))
        self.Cq = csc_matrix((ones(self.n), (self.bus0qh, range(self.n))), shape = (DAE.ng, self.n))
        
    #----------------------------------------------------------------------
    def gcall(self, DAE):
        #Bus variables
        vm = DAE.y[self.bus0Vm]
        va = DAE.y[self.bus0Va]
        #Note: Several loads can be connected to the same bus, if modified directly python will not apply several changes on one component, only the last one.
        # For this reason, interface equations are handled using conectivity matrices.

        # Interface equations   
        #Compute power for the current voltage
        pd = self.p*(vm/self.vm0)**self.alpha
        qd = self.q*(vm/self.vm0)**self.beta

        DAE.g += -1*self.Cp*(self.status*pd)     
        DAE.g += -1*self.Cq*(self.status*qd)


    #----------------------------------------------------------------------
    def gycall(self, DAE):
        #Bus variables
        vm = DAE.y[self.bus0Vm]
        va = DAE.y[self.bus0Va]

        #matrix size
        ng_ny = (DAE.ng, DAE.ny)

        #Power injections
        jac = (self.alpha/self.vm0)*(vm/self.vm0)**(self.alpha - 1)
        DAE.gy += csc_matrix((-1*self.p*jac, (self.bus0ph, self.bus0Vm)), shape = ng_ny)
        DAE.gy += csc_matrix((-1*self.q*jac, (self.bus0qh, self.bus0Vm)), shape = ng_ny)
        







