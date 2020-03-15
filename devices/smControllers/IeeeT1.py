from numpy import exp
from numpy import array
from numpy import sign
from numpy import ones
from scipy.sparse import csc_matrix



class IeeeT1():
    # AVR standar IEEET1 or IEEE type DC1.
    # For further detail see: https://www.neplan.ch/wp-content/uploads/2015/08/Nep_EXCITERS1.pdf
    def __init__(self):
        self.properties = {
            'init': True,
            'fcall': True, 
            'fxcall': True,
            'fycall': True,
            'fucall': True,
            'gcall': True,
            'gxcall': True,
            'gycall': False,
            'gucall': False ,
            'type': 'gov' 
            }
        #General parameters
        self.n = 0
        self.deviceIdx = {}
        #Parameters
        self.parameters = ['gen0', 'name', 'Ae', 'Be', 'Ka', 'Ke', 'Kf', 'Ta', 'Tf', 'Te', 'Tr', 'vrmax', 'vrmin']
        self.gen0 = []
        self.name = []
        self.Ae = []
        self.Be = []
        self.Ka = []
        self.Ke = []
        self.Kf = []
        self.Ta = []
        self.Tf = []
        self.Te = []
        self.Tr = []
        self.vrmax = []
        self.vrmin = []


        # States
        self.states = ['vmea', 'vr1', 'vr2', 'vf']
        self.vmea = []
        self.vr1 = []
        self.vr2 = []
        self.vf = []

        #Algebraics
        self.algebraics = []
        # Inputs
        self.inputs = ['vref']
        self.vref = []

        # Generator variables
        self.gen0AVR = [] #Generator AVR equation
        self.bus0Vm = [] #Generator terminal voltage
        self.gen0Vf = [] #Generator voltage field 


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
        #Terminal voltage
        vm = DAE.y[self.bus0Vm]
        #States
        vf = DAE.x[self.vf] = DAE.y[self.gen0Vf] #Voltage field
        vmea = DAE.x[self.vmea] = vm #Voltage measured
        vr1 = DAE.x[self.vr1] = vf * (self.Ke + self.Ae * exp(self.Be * abs(vf)))
        vr2 = DAE.x[self.vr2] = -1 * (self.Kf / self.Tf) * vf

        #Inputs
        vref = DAE.u[self.vref] = vr1/self.Ka + vmea + vr2 + (self.Kf / self.Tf) * vf
    
    #----------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari])        
    #----------------------------------------------------------------------
    def fcall(self, DAE):
        # States
        vmea = DAE.x[self.vmea]
        vr1 = DAE.x[self.vr1]
        vr2 = DAE.x[self.vr2]
        vf = DAE.x[self.vf]
        #Algebraic 
        vm = DAE.y[self.bus0Vm]
        #Inputs
        vref = DAE.u[self.vref]
        
        # f1
        DAE.f[self.vmea] = (vm - vmea)/self.Tr
        # f2
        DAE.f[self.vr1] = (self.Ka * (vref - vmea - vr2 - (self.Kf / self.Tf) * vf) - vr1)/self.Ta
        # f3
        DAE.f[self.vr2] = -((self.Kf / self.Tf) * vf + vr2 ) / self.Tf
        # f4
        DAE.f[self.vf] = -(vf * (self.Ke + self.Ae * exp(self.Be * abs(vf))) - vr1) / self.Te

    #----------------------------------------------------------------------
    def fxcall(self, DAE):
        #Matrix shape
        nx_nx = (DAE.nx, DAE.nx) 
        # States
        vmea = DAE.x[self.vmea]
        vr1 = DAE.x[self.vr1]
        vr2 = DAE.x[self.vr2]
        vf = DAE.x[self.vf]
        #Algebraic 
        vm = DAE.y[self.bus0Vm]
        #Inputs
        vref = DAE.u[self.vref]

        # f1 w.r.t vmea
        DAE.fx += csc_matrix((-1/self.Tr, (self.vmea, self.vmea)), shape=nx_nx)
        # f2 w.r.t vmea
        DAE.fx += csc_matrix((-1 * self.Ka/self.Ta, (self.vr1, self.vmea)), shape=nx_nx)
        # f2 w.r.t vr1
        DAE.fx += csc_matrix((-1/self.Ta, (self.vr1, self.vr1)), shape=nx_nx)
        # f2 w.r.t vr2
        DAE.fx += csc_matrix((-1 * self.Ka/self.Ta, (self.vr1, self.vr2)), shape=nx_nx)
        # f2 w.r.t vf
        DAE.fx += csc_matrix((-1 * self.Ka*(self.Kf/self.Tf)/self.Ta, (self.vr1, self.vf)), shape=nx_nx)
        # f3 w.r.t vr2
        DAE.fx += csc_matrix((-1 / self.Tf, (self.vr2, self.vr2)), shape=nx_nx)
        # f3 w.r.t vf
        DAE.fx += csc_matrix((-1 * (self.Kf / self.Tf) / self.Tf, (self.vr2, self.vf)), shape=nx_nx)
        # f4 w.r.t vr1
        DAE.fx += csc_matrix((1/self.Te, (self.vf, self.vr1)), shape=nx_nx)
        # f4 w.r.t vf
        DAE.fx += csc_matrix((-(self.Ke + self.Ae*exp(self.Be*abs(vf)) + self.Ae*self.Be*vf*exp(self.Be*abs(vf))*sign(vf))/self.Te, (self.vf, self.vf)), shape=nx_nx)
        


    #----------------------------------------------------------------------
    def fycall(self, DAE):
        #Matrix shape
        nx_ny = (DAE.nx, DAE.ny) 
        # States
        vmea = DAE.x[self.vmea]
        vr1 = DAE.x[self.vr1]
        vr2 = DAE.x[self.vr2]
        vf = DAE.x[self.vf]
        #Algebraic 
        vm = DAE.y[self.bus0Vm]
        #Inputs
        vref = DAE.u[self.vref]    
        
        # f1 w.r.t vm
        DAE.fy += csc_matrix((1/self.Tr, (self.vmea, self.bus0Vm)), shape=nx_ny) 
    #----------------------------------------------------------------------
    def fucall(self, DAE): 
        #Matrix shape
        nx_nu = (DAE.nx, DAE.nu)         
        #Matrix shape
        nx_ny = (DAE.nx, DAE.ny) 
        # States
        vmea = DAE.x[self.vmea]
        vr1 = DAE.x[self.vr1]
        vr2 = DAE.x[self.vr2]
        vf = DAE.x[self.vf]
        #Algebraic 
        vm = DAE.y[self.bus0Vm]
        #Inputs
        vref = DAE.u[self.vref]    

        # f2 w.r.t vmea
        DAE.fu += csc_matrix((self.Ka/self.Ta, (self.vr1, self.vref)), shape=nx_nu)

    #----------------------------------------------------------------------
    def gcall(self, DAE):
        # States
        vmea = DAE.x[self.vmea]
        vr1 = DAE.x[self.vr1]
        vr2 = DAE.x[self.vr2]
        vf = DAE.x[self.vf]
        #Algebraic 
        vm = DAE.y[self.bus0Vm]
        #Inputs
        vref = DAE.u[self.vref]    
        
        DAE.g[self.gen0AVR] += -1 * vf
    
    def gxcall(self, DAE):
        #Matrix shape
        ng_nx = (DAE.ng, DAE.nx)
        DAE.gx += csc_matrix((-1 * ones(self.n), (self.gen0AVR, self.vf)), shape=ng_nx)

        
