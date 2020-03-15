from numpy import array
from numpy import ones
from numpy import conj
from numpy import pi
from numpy import exp
from numpy import angle
from numpy import sin
from numpy import cos


from scipy.sparse import csc_matrix
class Syn4():
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
        self.parameters = ['bus0', 'name', 'H', 'D',  'Td10', 'Tq10', 'ra', 'xd','xd1', 'xq', 'xq1','sn', 'vn', 'fn', 'pgen', 'qgen']
        self.impendances = ['ra', 'xd', 'xd1', 'xq', 'xq1']
        self.powers = ['H', 'D']
        self.bus0 = []
        self.name = []
        self.H = [] #Inertia constant
        self.D = []
        self.Td10 = [] #d-axis transient time constant
        self.Tq10 = [] #q-axis transient time constant
        self.ra = [] #Armature resistance.
        self.xd = [] #d-axis reactance 
        self.xd1 = [] #d-axis transient reactance       
        self.xq = [] #q-axis reactance 
        self.xq1 = [] #q-axis transient reactance 
        self.sn = [] #MVA base.
        self.vn = [] #kV base.
        self.fn = [] #base frequency.
        self.pgen = [] #Initial active power
        self.qgen = [] #Initial reactive power
        #States
        self.states = ['delta', 'omega', 'ed1', 'eq1']
        self.omega = []
        self.delta = []
        self.ed1 = []
        self.eq1 = []

        #Algebraic
        self.algebraics = ['vd', 'vq', 'Id', 'Iq', 'pe', 'pm', 'vf',  'qh']
        self.inputs = []

        self.pm = [] #Mechanical power
        self.pe = [] #Air gap electrical power
        self.vq = [] #q-axis component of terminal voltage
        self.vd = [] #d-axis component of terminal voltage
        self.Iq = [] #q-axis component of terminal current
        self.Id = [] #d-axis component of terminal current
        self.vf = [] #Field voltage
        self.qh = [] #Reactive power generated

 


        #Algebraic equations;
        self.algEq = ['gvd', 'gvq',  'gpe', 'g6', 'g7', 'gGov', 'gAVR', 'gqh']
        self.gvq = [] #Change of reference frame
        self.gvd = [] #Change of reference frame
        self.gpe = [] #airgap electrical power
        self.g6 = [] #voltage equation vd
        self.g7 = [] #voltage equation vq
        self.gGov = [] #Governor equation
        self.gAVR = [] #Governor equation
        self.gqh = [] #Reactive power


        #Bus variables and equations
        self.busVariables = ['bus0Idx', 'bus0Vm', 'bus0Va', 'bus0ph', 'bus0qh', 'busVb']
        self.bus0Idx = [] #Bus Idx
        self.bus0Vm = [] #Bus voltage magnitude Index
        self.bus0Va = [] #Bus voltage angle Index        
        self.bus0ph = [] #Bus injected active power index
        self.bus0qh = [] #Bus injected reactive power index
        self.bus0Vb = [] #Bus base voltage
 

    #----------------------------------------------------------------------
    def addDevice(self,dae, bus,deviceData):
        #Add device parameters.
        for pari in self.parameters:
            self.__dict__[pari].append(deviceData[pari])

        #Assing index for state variables.
        for statei in self.states:
            self.__dict__[statei].append(dae.nx)
            dae.nx += 1
        #Assing index for algebraic variables.
        for algi in self.algebraics:
            self.__dict__[algi].append(dae.ny)
            dae.ny += 1
        
        #Assing index for input variables.
        for algi in self.inputs:
            self.__dict__[algi].append(dae.nu)
            dae.nu += 1
        #Assing index for algebraic variables.
        for algi in self.algEq:
            self.__dict__[algi].append(dae.ng)
            dae.ng += 1        

        
        #bus variables and equations
        busIdx = bus.deviceIdx[self.bus0[-1]]
        self.bus0Idx.append(busIdx)
        self.bus0Vm.append(bus.vm[busIdx])
        self.bus0Va.append(bus.va[busIdx])
        self.bus0ph.append(bus.ph[busIdx])
        self.bus0qh.append(bus.qh[busIdx])
        self.bus0Vb.append(bus.vb[busIdx])
        
        #Internal index
        self.deviceIdx[self.name[-1]] = self.n
        self.n += 1

    #----------------------------------------------------------------------
    def setUp(self):
        #Convert parameter lists to numpy arrays.
        for pari in self.parameters:
            self.__dict__[pari] = array(self.__dict__[pari])

        # convert to system base!
        for pari in self.powers:
            self.__dict__[pari] = self.__dict__[pari] * self.sn / 100 #100MVA per default
        
        zbSystem = array(self.bus0Vb)**2 / 100
        zbMachine = self.vn**2/self.sn

        for pari in self.impendances:
            self.__dict__[pari] = self.__dict__[pari] * zbMachine/zbSystem



    #----------------------------------------------------------------------
    def initialize(self, dae):
        vm = dae.y[self.bus0Vm]
        va = dae.y[self.bus0Va]

        #Compute initial complex voltage
        v = (vm + 0j)*exp(1j*va)
        #Compute Apparent power
        s = self.pgen + 1j*self.qgen
        #Compute current
        i = conj(s/v)
        #compute internal FEM
        e = v + (self.ra + 1j*self.xq)*i
        #Compute initial angle
        delta = dae.x[self.delta] = angle(e)
        #Compute dq variables
        vdq = v*exp(-1j*(delta - pi/2))
        idq = i*exp(-1j*(delta - pi/2))

        vd = dae.y[self.vd] = vdq.real
        vq = dae.y[self.vq] = vdq.imag
        Id = dae.y[self.Id] = idq.real
        Iq = dae.y[self.Iq] = idq.imag

        #Power at airgap
        pe = dae.y[self.pe] = (vq + self.ra*Iq)*Iq +(vd + self.ra*Id)*Id
        
        #Internal voltages
        eq1 = dae.x[self.eq1] = vq + self.ra * Iq + self.xd1 * Id
        ed1 = dae.x[self.ed1] = vd + self.ra * Id - self.xq1 * Iq

        #Field voltage
        vf = dae.y[self.vf] = eq1 + (self.xd - self.xd1) * Id
        
       #Mechanical
        omega = dae.x[self.omega] = 1
        pm = dae.y[self.pm] = pe

        #Active and reactive power.
        dae.y[self.qh] = 1 * self.qgen

    #----------------------------------------------------------------------
    # Compute F(x,y,u)
    def fcall(self, dae):
        wn = 2*pi*self.fn
        #States
        omega = dae.x[self.omega]
        ed1 = dae.x[self.ed1]
        eq1 = dae.x[self.eq1]
        #Algebraic variables
        pe = dae.y[self.pe]
        Iq = dae.y[self.Iq]
        Id = dae.y[self.Id]
        vf = dae.y[self.vf]
        #Mechanical power
        pm = dae.y[self.pm]
        # Equations of motion
        dae.f[self.delta] = wn*(omega - 1)
        dae.f[self.omega] = (1/(2*self.H))*(pm - pe - self.D*(omega - 1))


        dae.f[self.eq1] = (-eq1 - (self.xd - self.xd1) * Id + vf)/self.Td10     #Milano (15.29)   
        dae.f[self.ed1] = (-ed1 + (self.xq - self.xq1)*Iq)/self.Tq10  #Milano (15.29) 


    def fxcall(self, dae):
        #Matrix shape
        nx_nx = (dae.nx, dae.nx)
        
        wn = 2*pi*self.fn

        # f1 w.r.t delta
        # f1 w.r.t omega
        dae.fx += csc_matrix((wn, (self.delta, self.omega)), shape=nx_nx)

        # f2 w.r.t delta
        # f2 w.r.t omega
        dae.fx += csc_matrix((-1.*self.D/(2.*self.H), (self.omega, self.omega)), shape=nx_nx)
        #f3 w.r.t ed1
        dae.fx += csc_matrix((-1/self.Tq10, (self.ed1, self.ed1)), shape=nx_nx)
        #f4 w.r.t eq1
        dae.fx += csc_matrix((-1/self.Td10, (self.eq1, self.eq1)), shape=nx_nx)


    def fycall(self, dae):
        nx_ny = (dae.nx, dae.ny)        
        # f1
        # f2 
        dae.fy += csc_matrix((-1/(2.*self.H), (self.omega, self.pe)), shape=nx_ny)   
        dae.fy += csc_matrix((1/(2.*self.H), (self.omega, self.pm)), shape=nx_ny) 
        # f3 w.r.t Iq
        dae.fy += csc_matrix(((self.xq - self.xq1)/self.Tq10, (self.ed1, self.Iq)), shape=nx_ny)
        # f4 w.r.t Id
        dae.fy += csc_matrix((-1*(self.xd - self.xd1)/self.Td10, (self.eq1, self.Id)), shape=nx_ny)
        # f4 w.r.t vf
        dae.fy += csc_matrix((1/self.Td10, (self.eq1, self.vf)), shape=nx_ny)



    #----------------------------------------------------------------------
    def gcall(self, dae):
        vm = dae.y[self.bus0Vm]
        va = dae.y[self.bus0Va]
        #States
        delta = dae.x[self.delta]
        ed1 = dae.x[self.ed1]
        eq1 = dae.x[self.eq1]

        #Algebraic variables
        vq = dae.y[self.vq]
        vd = dae.y[self.vd]
        Iq = dae.y[self.Iq]
        Id = dae.y[self.Id]
        pe = dae.y[self.pe]
        pm = dae.y[self.pm]
        vf = dae.y[self.vf]
        qh = dae.y[self.qh]

        #Change of reference frame.
        dae.g[self.gvd] = vm*sin(delta - va) - vd
        dae.g[self.gvq] = vm*cos(delta - va) - vq  

        #Power at airgap
        dae.g[self.gpe] = (vq + self.ra*Iq)*Iq +(vd + self.ra*Id)*Id - pe  
        #Voltage at terminals
        dae.g[self.g6] = vd + self.ra*Id - ed1 - self.xq1*Iq #Direct axis         
        dae.g[self.g7] = vq + self.ra*Iq - eq1 + self.xd1*Id #Quadrature axis

        #Governor equation
        dae.g[self.gGov] += pm
        #Governor equation
        dae.g[self.gAVR] += vf

        #Generated power 
        dae.g[self.gqh] = vq*Id - vd*Iq - qh
        # Interface equations 
        dae.g[self.bus0ph] += vd*Id + vq*Iq
        dae.g[self.bus0qh] += vq*Id - vd*Iq
    #----------------------------------------------------------------------
    def gxcall(self, dae):
        #Bus variables
        vm = dae.y[self.bus0Vm]
        va = dae.y[self.bus0Va]
        #States
        delta = dae.x[self.delta]

        #matrix size
        ng_nx = (dae.ng, dae.nx)
        
        #Change of reference frame.
        # g1 - gvd
        dae.gx += csc_matrix((vm*cos(delta - va), (self.gvd, self.delta)), shape = ng_nx)
        # g2 - gvq
        dae.gx += csc_matrix((-vm*sin(delta - va), (self.gvq, self.delta)), shape = ng_nx)
        #g6 w.r.t ed1
        dae.gx += csc_matrix((-1*ones(self.n), (self.g6, self.ed1)), shape = ng_nx)
        #g7 w.r.t eq1
        dae.gx += csc_matrix((-1*ones(self.n), (self.g7, self.eq1)), shape = ng_nx)
    #----------------------------------------------------------------------
    def gycall(self, dae):
        #Bus variables
        vm = dae.y[self.bus0Vm]
        va = dae.y[self.bus0Va]

        #States
        delta = dae.x[self.delta]
        
        #Algebraic variables        
        vd = dae.y[self.vd]
        vq = dae.y[self.vq]        
        Id = dae.y[self.Id]
        Iq = dae.y[self.Iq]

        #matrix size
        ng_ny = (dae.ng, dae.ny)
        
        #Change of reference frame
        # gvd - g3
        dae.gy += csc_matrix((-1*ones(self.n), (self.gvd, self.vd)), shape = ng_ny)
        dae.gy += csc_matrix((sin(delta - va), (self.gvd, self.bus0Vm)), shape = ng_ny) #w.r.t bus voltage magnitude
        dae.gy += csc_matrix((-vm*cos(delta - va), (self.gvd, self.bus0Va)), shape = ng_ny) #w.r.t bus voltage angle

        # gvq - g2
        dae.gy += csc_matrix((-1*ones(self.n), (self.gvq, self.vq)), shape = ng_ny)
        dae.gy += csc_matrix((cos(delta - va), (self.gvq, self.bus0Vm)), shape = ng_ny) #w.r.t bus voltage magnitude
        dae.gy += csc_matrix((vm*sin(delta - va), (self.gvq, self.bus0Va)), shape = ng_ny) #w.r.t bus voltage angle

        #Electrical power
        # gpe - g5
        dae.gy += csc_matrix((Iq, (self.gpe, self.vq)), shape = ng_ny)
        dae.gy += csc_matrix((vq + 2*Iq*self.ra, (self.gpe, self.Iq)), shape = ng_ny)
        dae.gy += csc_matrix((Id, (self.gpe, self.vd)), shape = ng_ny)        
        dae.gy += csc_matrix((vd + 2*Id*self.ra, (self.gpe, self.Id)), shape = ng_ny)        
        dae.gy += csc_matrix((-1*ones(self.n), (self.gpe, self.pe)), shape = ng_ny)

        #Voltage at terminals     
        #g6
        dae.gy += csc_matrix((ones(self.n), (self.g6, self.vd)), shape = ng_ny)        
        dae.gy += csc_matrix((self.ra, (self.g6, self.Id)), shape = ng_ny)
        dae.gy += csc_matrix((-1*self.xq1, (self.g6, self.Iq)), shape = ng_ny)
        #g7
        dae.gy += csc_matrix((ones(self.n), (self.g7, self.vq)), shape = ng_ny)
        dae.gy += csc_matrix((self.ra, (self.g7, self.Iq)), shape = ng_ny)        
        dae.gy += csc_matrix((self.xd1, (self.g7, self.Id)), shape = ng_ny)        

        #Governor equation
        dae.gy += csc_matrix((ones(self.n), (self.gGov, self.pm)), shape = ng_ny)

        #AVR equation
        dae.gy += csc_matrix((ones(self.n), (self.gAVR, self.vf)), shape = ng_ny)
        #Power injections
        # ph
        dae.gy += csc_matrix((Id, (self.bus0ph, self.vd)), shape = ng_ny)
        dae.gy += csc_matrix((Iq, (self.bus0ph, self.vq)), shape = ng_ny)
        dae.gy += csc_matrix((vd, (self.bus0ph, self.Id)), shape = ng_ny)
        dae.gy += csc_matrix((vq, (self.bus0ph, self.Iq)), shape = ng_ny)
        
        # qh
        dae.gy += csc_matrix((-Iq, (self.gqh, self.vd)), shape = ng_ny)
        dae.gy += csc_matrix((Id, (self.gqh, self.vq)), shape = ng_ny)
        dae.gy += csc_matrix((vq, (self.gqh, self.Id)), shape = ng_ny)
        dae.gy += csc_matrix((-vd, (self.gqh, self.Iq)), shape = ng_ny)
        dae.gy += csc_matrix((-ones(self.n), (self.gqh, self.qh)), shape = ng_ny)

        dae.gy += csc_matrix((ones(self.n), (self.bus0qh, self.qh)), shape = ng_ny)


    def gucall(self, dae): pass