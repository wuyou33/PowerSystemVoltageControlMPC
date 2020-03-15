from numpy import pi
from numpy import array
from numpy import exp
from numpy import conj

from scipy.sparse import csc_matrix
from pypower.api import dSbus_dV

class Bus():
    #Bus type:
        #PQ = 1
        #PV = 2
        #REF = 3
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
            'gucall': False,
            'type': 'bus'
            }
        
        #Internal Parameters
        self.n = 0
        self.deviceIdx = {}
        #Parameters
        self.parameters = ['name', 'va0', 'vm0', 'busType', 'vb']
        self.name = []
        self.va0 = []
        self.vm0 = []
        self.busType = []
        self.vb = [] 
        #states
        self.states = []
        #inputs
        self.inputs = []
        #Algebraic variables
        self.algebraics = ['va', 'vm']
        self.va = []
        self.vm = []
        #Algebraic equations
        self.algEqs = ['ph', 'qh']
        self.ph = [] #Active  power 
        self.qh = [] #reactive power      
        
        

    def addDevice(self, DAE, deviceData):       
        #Add device parameters.
        for pari in self.parameters:
            self.__dict__[pari].append(deviceData[pari])            
                
        #Assing index for algebraic variables.
        for algi in self.algebraics:
            self.__dict__[algi].append(DAE.ny)
            DAE.ny += 1
        #Assing index for algebraic equations.
        for algi in self.algEqs:
            self.__dict__[algi].append(DAE.ng)
            DAE.ng += 1        
        #Internal index
        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1

#-----------------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari])
#-----------------------------------------------------------------------------
    def initialize(self, DAE):
        DAE.y[self.va] = self.va0*pi/180
        DAE.y[self.vm] = self.vm0


    def gcall(self, DAE, Ybus):
        #Get voltage value
        vm = DAE.y[self.vm]
        va = DAE.y[self.va]
        #Compute complex voltage
        V = vm*exp(1j*va)
        #Compute power injections
        S = V * (conj(Ybus * V))
        #Active and Reactive power
        DAE.g[self.ph] += -1*S.real
        DAE.g[self.qh] += -1*S.imag



#-----------------------------------------------------------------------------

    def gycall(self, DAE, Ybus):
        #Get voltage value
        vm = DAE.y[self.vm]
        va = DAE.y[self.va]
        #Compute complex voltage
        v = vm*exp(1j*va)
        #Compute jacobian    
        dS_dVm, dS_dVa = dSbus_dV(Ybus, v)        
        #Jacobian matrix shape
        ng_ny = (DAE.ng, DAE.ny)
        #jacobians w.r.t voltage magnitude
        # Ph w.r.t Vm
        idx = dS_dVm.nonzero()
        row = array(self.ph)[idx[0]]
        col = array(self.vm)[idx[1]]
        data = dS_dVm.data.real        
        DAE.gy += -1*csc_matrix((data, (row, col)), shape = ng_ny)
        # Qh w.r.t Vm
        idx = dS_dVm.nonzero()
        row = array(self.qh)[idx[0]]
        col = array(self.vm)[idx[1]]
        data = dS_dVm.data.imag        
        DAE.gy += -1*csc_matrix((data, (row, col)), shape = ng_ny)

        #jacobians w.r.t voltage angle
        # Ph w.r.t Va
        idx = dS_dVa.nonzero()
        row = array(self.ph)[idx[0]]
        col = array(self.va)[idx[1]]
        data = dS_dVa.data.real        
        DAE.gy += -1*csc_matrix((data, (row, col)), shape = ng_ny)
        # Qh w.r.t Va
        idx = dS_dVa.nonzero()
        row = array(self.qh)[idx[0]]
        col = array(self.va)[idx[1]]
        data = dS_dVa.data.imag        
        DAE.gy += -1*csc_matrix((data, (row, col)), shape = ng_ny)

