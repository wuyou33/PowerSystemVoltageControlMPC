import numpy as np
class svrSA:
    def __init__(self, dae, system, buspilot, avrIdx, qhIdx, alpha, dT = 250e-3):
        nGen = len(avrIdx)
        self.dT = dT
        self.buspilot = buspilot[:]
        self.avrIdx = avrIdx
        #Bus Index
        self.busIdx = [system.bus.deviceIdx[busi] for busi in self.buspilot]
        #Index of voltage magnitude variable
        self.vmIdx = [system.bus.vm[i] for i in self.busIdx]
        #Index of the reactive power generation
        self.qhIdx = qhIdx
        # Initial values
        self.vrss = dae.u[avrIdx] #Voltaje de referencia de los AVR
        self.vmss = dae.y[self.vmIdx] #Voltaje de referencia de los nodos piloto.
        self.vsp = np.array(self.vmss[:]) #Voltaje de setpoint
        self.qhss = dae.y[qhIdx] #Initial reactive power values
        #Controller parameters
        self.T1 = 1./0.05 #(s) Regional reactive loop.
        self.k1 = 0.005 #Regional Proportional gain

        self.T2 = 180 #(s) Local voltage loop integral time.
        self.k2 = 0.0 #(s) Local voltage loop integral time.
        #Controller variables
        self.x1 = 0 #Controller 1 - Regional level
        self.x2 = np.zeros(nGen) #Controller 2 - Local level
        #Ponderated
        self.alpha = alpha
    def computeAll(self, system, dae): pass

    def execute(self, system, dae):
        # Compute error in voltage of pilot nodes
        evPilot = self.vsp  - dae.y[self.vmIdx]
        e1 = evPilot.mean()
        # Compute regional controller signal
        self.x1 = self.x1 +  (1/self.T1) * e1 * self.dT # State variable
        dv1 = self.x1  + self.k1 * e1 #Region al PI Controller

        #Local controllers
        dqgen = dae.y[self.qhIdx] - self.qhss
        qTotal = dqgen.sum()
        qref = (qTotal) * self.alpha
        e2 = qref - dqgen
        self.x2 = self.x2 +  (1/self.T2) * e2 * self.dT # State variable
        dv2 = self.x2  + self.k2 * e2 #Region al PI Controller


        
        
        # #Local controller
        # ev = (dQ / nGen) - (dae.y[self.qhIdx] - self.qhss)
        # self.xV = self.xV + (1/self.Tv) * ev * self.dT 
        #Actualizar entradas.
        dae.u[self.avrIdx] = self.vrss + dv1 + dv2






