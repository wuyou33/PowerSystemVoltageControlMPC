from numpy import array
from numpy import ones
from numpy import conj
from numpy import pi
from numpy import exp
from numpy import angle
from numpy import sin
from numpy import cos


from scipy.sparse import csc_matrix
class Syn2():
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
            'gucall': False,
            'type': 'gen' 
            }

        #Internal parameters
        self.n = 0 #Internal counter.
        self.deviceIdx = {} #Internal index.
        #Parameters
        self.parameters = ['bus0', 'name', 'H', 'D',  'ra', 'xd1', 'sn', 'vn', 'fn', 'pgen', 'qgen']
        self.impendances = ['ra',  'xd1']
        self.powers = ['H', 'D']
        self.bus0 = []
        self.name = []
        self.H = []
        self.D = []
        self.ra = [] #Armature resistance.
        self.xd1 = [] #Direct axis transient reactance       
        self.sn = [] #MVA base.
        self.vn = [] #kV base.
        self.fn = [] #base frequency.
        self.pgen = [] #Initial active power
        self.qgen = [] #Initial reactive power
        #States
        self.states = ['delta', 'omega']
        self.omega = []
        self.delta = []

        #Algebraic
        self.algebraics = ['vd', 'vq', 'Id', 'Iq', 'pe', 'pm']
        self.inputs = []

        self.pm = [] #Mechanical power
        self.pe = [] #Air gap electrical power
        self.vq = [] #q-axis component of terminal voltage
        self.vd = [] #d-axis component of terminal voltage
        self.Iq = [] #q-axis component of terminal current
        self.Id = [] #d-axis component of terminal current


        #Note: This is not an algebraic variable, nor a parameter. This value remains constant.
        self.eq1 = [] #q-axis transient voltage


        #Algebraic equations;
        self.algEq = ['gvd', 'gvq',  'gpe', 'g6', 'g7', 'gGov']
        self.gvq = [] #Change of reference frame
        self.gvd = [] #Change of reference frame
        self.gpe = [] #airgap electrical power
        self.g6 = [] #voltage equation vd
        self.g7 = [] #voltage equation vq
        self.gGov = [] #Governor equation


        #Bus variables and equations
        self.busVariables = ['bus0Idx', 'bus0Vm', 'bus0Va', 'bus0ph', 'bus0qh']
        self.bus0Idx = [] #Bus Idx
        self.bus0Vm = [] #Bus voltage magnitude Index
        self.bus0Va = [] #Bus voltage angle Index        
        self.bus0ph = [] #Bus injected active power index
        self.bus0qh = [] #Bus injected reactive power index


    #----------------------------------------------------------------------
    def addDevice(self,DAE, Bus,deviceData):
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
        
        #Assing index for input variables.
        for algi in self.inputs:
            self.__dict__[algi].append(DAE.nu)
            DAE.nu += 1
        #Assing index for algebraic variables.
        for algi in self.algEq:
            self.__dict__[algi].append(DAE.ng)
            DAE.ng += 1        

        
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
        vm = DAE.y[self.bus0Vm]
        va = DAE.y[self.bus0Va]

        #Compute initial complex voltage
        v = (vm + 0j)*exp(1j*va)
        #Compute Apparent power
        s = self.pgen + 1j*self.qgen
        #Compute current
        i = conj(s/v)
        #compute internal FEM
        e = v + (self.ra + 1j*self.xd1)*i
        #Compute initial angle
        delta = DAE.x[self.delta] = angle(e)
        #Compute dq variables
        vdq = v*exp(-1j*(delta - pi/2))
        idq = i*exp(-1j*(delta - pi/2))

        vd = DAE.y[self.vd] = vdq.real
        vq = DAE.y[self.vq] = vdq.imag
        Id = DAE.y[self.Id] = idq.real
        Iq = DAE.y[self.Iq] = idq.imag


        #Power at airgap
        pe = DAE.y[self.pe] = (vq + self.ra*Iq)*Iq +(vd + self.ra*Id)*Id
        
        #Internal voltage
        self.eq1 = vq + self.ra*Iq + self.xd1*Id
        
       #Mechanical
        omega = DAE.x[self.omega] = 1
        pm = DAE.y[self.pm] = pe

    #----------------------------------------------------------------------
    # Compute F(x,y,u)
    def fcall(self, DAE):
        wn = 2*pi*self.fn
        #States
        omega = DAE.x[self.omega]
        #Algebraic variables
        pe = DAE.y[self.pe]
        #Inputs
        pm = DAE.y[self.pm]

        DAE.f[self.delta] = wn*(omega - 1)
        DAE.f[self.omega] = (1/(2*self.H))*(pm - pe - self.D*(omega - 1))

    def fxcall(self, DAE):
        #Matrix shape
        nx_nx = (DAE.nx, DAE.nx)
        
        wn = 2*pi*self.fn

        # f1 w.r.t delta
        # f1 w.r.t omega
        DAE.fx += csc_matrix((wn, (self.delta, self.omega)), shape=nx_nx)

        # f2 w.r.t delta
        # f2 w.r.t omega
        DAE.fx += csc_matrix((-1.*self.D/(2.*self.H), (self.omega, self.omega)), shape=nx_nx)

    def fycall(self, DAE):
        nx_ny = (DAE.nx, DAE.ny)        
        # f1
        # f2 
        DAE.fy += csc_matrix((-1/(2.*self.H), (self.omega, self.pe)), shape=nx_ny)   
        DAE.fy += csc_matrix((1/(2.*self.H), (self.omega, self.pm)), shape=nx_ny) 



    #----------------------------------------------------------------------
    def gcall(self, DAE):
        vm = DAE.y[self.bus0Vm]
        va = DAE.y[self.bus0Va]
        #States
        delta = DAE.x[self.delta]

        #Algebraic variables
        vq = DAE.y[self.vq]
        vd = DAE.y[self.vd]
        Iq = DAE.y[self.Iq]
        Id = DAE.y[self.Id]
        pe = DAE.y[self.pe]
        pm = DAE.y[self.pm]

        #Change of reference frame.
        DAE.g[self.gvd] = vm*sin(delta - va) - vd
        DAE.g[self.gvq] = vm*cos(delta - va) - vq  

        #Power at airgap
        DAE.g[self.gpe] = (vq + self.ra*Iq)*Iq +(vd + self.ra*Id)*Id - pe  
        #Voltage at terminals
        DAE.g[self.g6] = vd + self.ra*Id - self.xd1*Iq #Direct axis
        DAE.g[self.g7] = vq + self.ra*Iq - self.eq1 + self.xd1*Id #Quadrature axis

        #Governor equation
        DAE.g[self.gGov] += pm
        # Interface equations 
        DAE.g[self.bus0ph] += vd*Id + vq*Iq
        DAE.g[self.bus0qh] += vq*Id - vd*Iq
    #----------------------------------------------------------------------
    def gxcall(self, DAE):
        #Bus variables
        vm = DAE.y[self.bus0Vm]
        va = DAE.y[self.bus0Va]

        #States
        delta = DAE.x[self.delta]

        #matrix size
        ng_nx = (DAE.ng, DAE.nx)
        
        #Change of reference frame.
        # g1 - gvd
        DAE.gx += csc_matrix((vm*cos(delta - va), (self.gvd, self.delta)), shape = ng_nx)
        # g2 - gvq
        DAE.gx += csc_matrix((-vm*sin(delta - va), (self.gvq, self.delta)), shape = ng_nx)
    #----------------------------------------------------------------------
    def gycall(self, DAE):
        #Bus variables
        vm = DAE.y[self.bus0Vm]
        va = DAE.y[self.bus0Va]

        #States
        delta = DAE.x[self.delta]
        
        #Algebraic variables        
        vd = DAE.y[self.vd]
        vq = DAE.y[self.vq]        
        Id = DAE.y[self.Id]
        Iq = DAE.y[self.Iq]

        #matrix size
        ng_ny = (DAE.ng, DAE.ny)
        
        #Change of reference frame
        # gvd - g3
        DAE.gy += csc_matrix((-1*ones(self.n), (self.gvd, self.vd)), shape = ng_ny)
        DAE.gy += csc_matrix((sin(delta - va), (self.gvd, self.bus0Vm)), shape = ng_ny) #w.r.t bus voltage magnitude
        DAE.gy += csc_matrix((-vm*cos(delta - va), (self.gvd, self.bus0Va)), shape = ng_ny) #w.r.t bus voltage angle

        # gvq - g2
        DAE.gy += csc_matrix((-1*ones(self.n), (self.gvq, self.vq)), shape = ng_ny)
        DAE.gy += csc_matrix((cos(delta - va), (self.gvq, self.bus0Vm)), shape = ng_ny) #w.r.t bus voltage magnitude
        DAE.gy += csc_matrix((vm*sin(delta - va), (self.gvq, self.bus0Va)), shape = ng_ny) #w.r.t bus voltage angle

        #Electrical power
        # gpe - g5
        DAE.gy += csc_matrix((Iq, (self.gpe, self.vq)), shape = ng_ny)
        DAE.gy += csc_matrix((vq + 2*Iq*self.ra, (self.gpe, self.Iq)), shape = ng_ny)
        DAE.gy += csc_matrix((Id, (self.gpe, self.vd)), shape = ng_ny)        
        DAE.gy += csc_matrix((vd + 2*Id*self.ra, (self.gpe, self.Id)), shape = ng_ny)        
        DAE.gy += csc_matrix((-1*ones(self.n), (self.gpe, self.pe)), shape = ng_ny)

        #Voltage at terminals     
        #g6
        DAE.gy += csc_matrix((ones(self.n), (self.g6, self.vd)), shape = ng_ny)        
        DAE.gy += csc_matrix((self.ra, (self.g6, self.Id)), shape = ng_ny)
        DAE.gy += csc_matrix((-1*self.xd1, (self.g6, self.Iq)), shape = ng_ny)
        #g7
        DAE.gy += csc_matrix((ones(self.n), (self.g7, self.vq)), shape = ng_ny)
        DAE.gy += csc_matrix((self.ra, (self.g7, self.Iq)), shape = ng_ny)        
        DAE.gy += csc_matrix((self.xd1, (self.g7, self.Id)), shape = ng_ny)        

        #Governor equation
        DAE.gy += csc_matrix((ones(self.n), (self.gGov, self.pm)), shape = ng_ny)
        #Power injections
        # ph
        DAE.gy += csc_matrix((Id, (self.bus0ph, self.vd)), shape = ng_ny)
        DAE.gy += csc_matrix((Iq, (self.bus0ph, self.vq)), shape = ng_ny)
        DAE.gy += csc_matrix((vd, (self.bus0ph, self.Id)), shape = ng_ny)
        DAE.gy += csc_matrix((vq, (self.bus0ph, self.Iq)), shape = ng_ny)
        
        # qh
        DAE.gy += csc_matrix((-Iq, (self.bus0qh, self.vd)), shape = ng_ny)
        DAE.gy += csc_matrix((Id, (self.bus0qh, self.vq)), shape = ng_ny)
        DAE.gy += csc_matrix((vq, (self.bus0qh, self.Id)), shape = ng_ny)
        DAE.gy += csc_matrix((-vd, (self.bus0qh, self.Iq)), shape = ng_ny)


    def gucall(self, DAE): pass