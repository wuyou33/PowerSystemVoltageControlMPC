
from numpy import array
from numpy import where
from numpy import ones
from scipy.sparse import csc_matrix
class GovTypeI():
    # Implemented as in Milano, F. (2010). Power system modelling and scripting. Springer. See section 16.1.1
    def __init__(self):
        self.properties = {
            'init': True,
            'fcall': True, 
            'fxcall': True,
            'fycall': True,
            'fucall': False,
            'gcall': True,
            'gxcall': True,
            'gycall': True,
            'gucall': False ,
            'type': 'gov' 
            }
        #General parameters
        self.n = 0
        self.deviceIdx = {}
        #Parameters
        self.parameters = ['gen0', 'name', 'pmax', 'pmin', 'R', 'T3', 'T4', 'T5', 'Tc', 'Ts']
        self.gen0 = []
        self.name = []
        self.pmax = []
        self.pmin = []
        self.R = []
        self.T3 = []
        self.T4 = []
        self.T5 = []
        self.Tc = []
        self.Ts = []
        # Algebraic equations
        self.algEq = ['gPin', 'gTm']
        self.gPin = []
        self.gTm = []

        #states
        self.states = ['xg1', 'xg2', 'xg3']
        self.xg1 = []
        self.xg2 = []
        self.xg3 = []
        #Algebraic variables.
        self.algebraics = ['pin', 'tm']
        self.pin = []
        self.tm = []
        # Inputs
        self.inputs = []
        # Constants
        self.porder = []
        # Generator variables
        self.gen0Gov = []
        self.gen0pm = []
        self.genOmega = []


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
        
        #Assing index for algebraic variables.
        for algi in self.algEq:
            self.__dict__[algi].append(dae.ng)
            dae.ng += 1   
        
        #Assing index for input variables.
        for algi in self.inputs:
            self.__dict__[algi].append(dae.nu)
            dae.nu += 1

        #Generator variables
        genIdx = Gen.deviceIdx[self.gen0[-1]]
        self.gen0Gov.append(Gen.gGov[genIdx])
        self.gen0pm.append(Gen.pm[genIdx])
        self.genOmega.append(Gen.omega[genIdx])

        self.n += 1

    #----------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari]) 
    #----------------------------------------------------------------------
    def initialize(self, dae):
        gen0pm = 1 * dae.y[self.gen0pm]
        #Constanst power reference
        self.porder = 1 * gen0pm
        #init mechanical power input
        pin = dae.y[self.pin] = 1 * self.porder        
        #Init governor
        xg1  = dae.x[self.xg1] = 1 *  gen0pm
        #Init servo
        xg2 = dae.x[self.xg2] = (1 - self.T3/self.Tc) * xg1
        #Init reheat
        xg3 = dae.x[self.xg3] = (1 - self.T4/self.T5) * (xg2 + (self.T3/self.Tc) * xg1)
        #Init mechanical power output
        tm = dae.y[self.tm] = xg3 + (self.T4/self.T5) * (xg2 + (self.T3/self.Tc) * xg1)

    #----------------------------------------------------------------------
    def fcall(self, dae):
        #Check the limits for pin
        # idx = where(dae.y[self.pin] > self.pmax).tolist()
        # dae.y[self.pin[idx]] = self.pmax[idx]

        # idx = where(dae.y[self.pin] < self.pmin)
        # dae.y[self.pin[idx]] = self.pmin[idx]

        #Algebraic
        pin = 1 * dae.y[self.pin]         
      


            

        # States
        xg1 = 1 * dae.x[self.xg1]
        xg2 = 1 * dae.x[self.xg2]
        xg3 = 1 * dae.x[self.xg3]

        dae.f[self.xg1] = (pin - xg1)/self.Ts
        dae.f[self.xg2] = ((1 - self.T3/self.Tc) * xg1 - xg2)/self.Tc
        dae.f[self.xg3] = ((1 - self.T4/self.T5) * (xg2 + (self.T3/self.Tc) * xg1) - xg3)/self.T5
    def fxcall(self, dae):
        #Matrix shape
        nx_nx = (dae.nx, dae.nx)
        # f1 w.r.t xg1
        dae.fx += csc_matrix((-1 / self.Ts, (self.xg1, self.xg1)), shape = nx_nx)
        # f2 w.r.t xg1
        dae.fx += csc_matrix(((1 - self.T3/self.Tc)/self.Tc, (self.xg2, self.xg1)), shape = nx_nx)        
        # f2 w.r.t xg2
        dae.fx += csc_matrix((-1 / self.Tc, (self.xg2, self.xg2)), shape = nx_nx)
        # f3 w.r.t xg1
        dae.fx += csc_matrix(((1 - self.T4/self.T5) * (self.T3/self.Tc) / self.T5, (self.xg3, self.xg1)), shape = nx_nx)
        # f3 w.r.t xg2
        dae.fx += csc_matrix(((1 - self.T4/self.T5) / self.T5, (self.xg3, self.xg2)), shape = nx_nx)   
        # f3 w.r.t xg3
        dae.fx += csc_matrix((-1 / self.T5, (self.xg3, self.xg3)), shape = nx_nx)

    def fycall(self, dae): 
        #Matrix shape
        nx_ny = (dae.nx, dae.ny) 
        # f1 w.r.t pin
        dae.fy +=  csc_matrix((1 / self.Ts, (self.xg1, self.pin)), shape=nx_ny)      
    # csc_matrix((data, (row, col)), shape=(3, 3))
    def gcall(self, dae):
        # Generator variables
        omega = dae.x[self.genOmega]
        #Check the limits for pin
        # idx = where(dae.y[self.pin] > self.pmax)
        # dae.y[self.pin[idx]] = self.pmax[idx]

        # idx = where(dae.y[self.pin] < self.pmin)
        # dae.y[self.pin[idx]] = self.pmin[idx]

        #Algebraic
        pin = 1 * dae.y[self.pin]
        tm = 1 * dae.y[self.tm]
        # States
        xg1 = 1 * dae.x[self.xg1]
        xg2 = 1 * dae.x[self.xg2]
        xg3 = 1 * dae.x[self.xg3]

        #Measurements and reference.
        dae.g[self.gPin] = self.porder + (1/self.R) * (1 - omega) - pin
        #Mechanical output
        dae.g[self.gTm] = xg3 + (self.T4/self.T5) * (xg2 + (self.T3/self.Tc) * xg1) - tm
        #Connection with generator
        dae.g[self.gen0Gov] += -1 * tm

    def gxcall(self, dae):
        #matrix size
        ng_nx = (dae.ng, dae.nx)
        # gpin w.r.t omega
        dae.gx += csc_matrix((ones(self.n),(self.gPin, self.genOmega)), shape=ng_nx)
        # gTm w.r.t xg1
        dae.gx += csc_matrix(((self.T4/self.T5)*(self.T3/self.Tc),(self.gTm, self.xg1)), shape=ng_nx)
        # gTm w.r.t xg2
        dae.gx += csc_matrix(((self.T4/self.T5),(self.gTm, self.xg2)), shape=ng_nx)
        # gTm w.r.t xg3
        dae.gx += csc_matrix((ones(self.n),(self.gTm, self.xg3)), shape=ng_nx)


    def gycall(self, dae):
        #matrix size
        ng_ny = (dae.ng, dae.ny)
        # gPin w.r.t pin
        dae.gy += csc_matrix((- 1 * ones(self.n), (self.gPin, self.pin)), shape=ng_ny)
        # gTm w.r.t tm
        dae.gy += csc_matrix((- 1 * ones(self.n), (self.gTm, self.tm)), shape=ng_ny)
        # Generator
        dae.gy += csc_matrix((- 1 * ones(self.n), (self.gen0Gov, self.tm)), shape=ng_ny)


    def gucall(self, dae): pass



