from methods import linearize
from methods import discretize
import numpy as np
from scipy import sparse as sparse 
import matplotlib.pyplot as plt

from time import time 

from .MPC import mpc
class  singleAgent():
    # From now the system will be considered in deviation variables!
    def __init__(self, system, dae, daeSS, bus, uIdx = [], buspilot = [], N= 20, dT = 250e-3, zIdx = [], zUb = [], zLb = []):
        #Prediction horizon
        self.N = N
        #Sampling time
        self.dT = dT
        # Every AVR will participate
        self.buspilot = buspilot
        #Bus Index
        self.busIdx = [bus.deviceIdx[busi] for busi in self.buspilot]
        #Index of voltage magnitude variable
        self.vmIdx = [bus.vm[i] for i in self.busIdx]

        # Inputs
        self.uIdx = uIdx

        #Initialize variables
        ny = len(self.vmIdx)
        self.ek = 0
        self.yrk1 = np.zeros(ny) #Deviation variables
        # self.yrk1 = dae.y[self.vmIdx]

        # Steady-State variables
        self.daeSS = daeSS

        #Store Output values
        self.nExe = 0 #Cantidad de ejecuciones.
        self.yrOut = np.array([self.daeSS.y[self.vmIdx]]) #Initial value of reference 
        self.tOut = np.array([0])
        self.eOut = np.zeros(ny)

        # Algrbraic variables of interest
        self.zIdx = zIdx #Index
        self.zUb = np.array(zUb) #Upper Limit
        self.zLb = np.array(zLb) #Lower Limit

    def computeAll(self, system, dae):
        #Reinit jacobians
        self.daeSS.reInitG()
        self.daeSS.reInitF()
        #compute functions
        system.computeF(self.daeSS)
        system.computeG(self.daeSS, system.Ybus)

    
    def linearizeSystem(self, dae):
        #Get jacobians.
        fx = 1 * dae.fx
        fy = 1 * dae.fy
        fu = 1 * dae.fu
        gx = 1 * dae.gx
        gy = 1 * dae.gy
        gu = 1 * dae.gu
        #Get value of the functions.
        f0 = 1 * dae.f
        g0 = 1 * dae.g
        #Get the initial values.
        x0 = 1 * dae.x
        y0 = 1 * dae.y
        u0 = 1 * dae.u

        return  linearize(fx, fy, fu, gx, gy, gu, f0, g0, x0, y0, u0)

   

    def execute(self, system, dae):
        # Steady state variables
        xss = np.array(self.daeSS.x) #States
        yss = np.array(self.daeSS.y[self.vmIdx]) #Outputs
        uss = np.array(self.daeSS.u[self.uIdx]) #Inputs
        zss = np.array(self.daeSS.y[self.zIdx]) #Algebraic variables.
        #Initial states
        xk = dae.x[:] - xss
        #Initial outputs
        yk1 = dae.y[self.vmIdx] - yss
        #Previous input
        uk1 = dae.u[self.uIdx] - uss
        #Previous reference
        yrk1 = self.yrk1[:]
        #Update error
        self.ek =  (yk1 - yrk1)
        #Initial value for error
        ek = np.array(self.ek)

        #Number of states, inputs,  outputs and algebraic variables
        nx = xss.shape[0]
        ny = yss.shape[0]
        nu = uss.shape[0]
        nz = zss.shape[0]

        
        #Linearize system!
        (A, B, C, D, F, G) = self.linearizeSystem(self.daeSS) #Use steady state variables
        # Discretize system
        Ad, Bd, Fd = discretize( A, B,  F, dT = self.dT)  
        #Prediction model
        # For advanced indexing documentation see:  https://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#advanced-indexing 
        Idx = np.ix_(range(nx), range(nx))
        Ad = Ad[Idx]

        Idx = np.ix_(range(nx), self.uIdx)  
        Bd = Bd[Idx]    

        Idx = list(range(nx))
        Fd = Fd[Idx]  
        #Outputs!!!       
        Idx = np.ix_(self.vmIdx, range(nx))
        Cd = C[Idx]
        Idx = np.ix_(self.vmIdx, self.uIdx)    
        Dd = D[Idx]
        Idx = self.vmIdx
        Gd = G[Idx]

        #Compute constant terms
        Fc = np.array(Fd)
        Gc = np.array(Gd)

        # Algebraic variables
        Idx = np.ix_(self.zIdx, range(nx))
        Cz = C[Idx] 
        Idx = np.ix_(self.zIdx, self.uIdx)    
        Dz = D[Idx]
        Idx = self.zIdx
        Gz = G[Idx]

        # Fc = Fd - Ad.dot(xk) - Bd.dot(uk1) + xk
        # Gc = G - C.dot(xk) - D.dot(uk1) + yk1

        # yk = C.dot(xk) + D.dot(uk1) +  Gc   

        # Estas lineas son para probar que el modelo funciona
        # xn = np.zeros((nx, 20))
        # yn = np.zeros((ny, 20))
        # for i in range(20):
        #     xk = Ad.dot(xk) + Bd.dot(uk1) + Fc
        #     yk = C.dot(xk) + D.dot(uk1) +  Gc
        #     xn[:, i] = xk
        #     yn[:, i] = yk

        #     if i == 1:
        #         uk1[0] += 0.001


        # plt.plot(yn[0,:])
        # plt.show()

        #Disturbances
        Bw = sparse.csc_matrix((nx, 1))
        Dw = sparse.csc_matrix((ny, 1))
        wk = np.zeros(1)


        #Restictions: This is temporal!!!
        #states
        xmax = np.inf * np.ones(nx) - xss
        xmin = - np.inf * np.ones(nx) - xss
        #inputs
        umax = 1.5 * np.ones(nu) - uss
        umin = -1.5 * np.ones(nu) - uss
        #Rate of change
        dumax = 0.02 * np.ones(nu)
        dumin = - 0.02 * np.ones(nu)
        #Outputs
        ymax = 1.1 * np.ones(ny) - yss
        ymin = 0.9 * np.ones(ny) - yss
        #Outputs
        yrmax = 0.02 * np.ones(ny)
        yrmin = -0.02 * np.ones(ny)
        #Rate of change
        dyrmax = 0.001 * np.ones(ny)
        dyrmin = -0.001 * np.ones(ny)
        # Algebraic
        zmax = self.zUb - zss
        zmin = self.zLb - zss

        # --------------------------------------------------
        #Weigths!!!
        qx = 0.0 * np.ones(nx)
        qe = 20.0 * np.ones(ny)
        qu = 0.5 * np.ones(nu)
        qyr = 10.0 * np.ones(ny)

        qxf = 0.0* np.ones(nx)
        qef = 20* np.ones(ny)

        #Horizon
        N = self.N

        #Compute inputs
        if abs(dae.f[1]) > 1e-5:
            t1 = time()
            uk, yrk, z = mpc(Ad, Bd, Cd, Dd,  Fc, Gc, xk, ek, uk1, yrk1, xmax, xmin, umax, umin, dumax, dumin, ymax, ymin, yrmax, yrmin, dyrmax, dyrmin, qx, qe, qu, qyr, qxf, qef, zmax, zmin, Cz, Dz, Gz, N= N)
            print('Elapsed Time: %.3f' %(time() - t1) )
        else:
            uk, yrk = (uk1, yrk1)


        #Update References!    
        self.yrk1 = np.array(yrk)

        #Update inputs!!!
        dae.u[self.uIdx] = uk[:] + uss

        #Store Reference values
        self.nExe += 1
        self.tOut = np.append(self.tOut, self.nExe * self.dT)
        self.yrOut = np.vstack( (self.yrOut, yrk[:] + yss[:]))
        
        #Store error
        self.eOut = np.vstack( (self.eOut, ek))


        
        



        





        

    



