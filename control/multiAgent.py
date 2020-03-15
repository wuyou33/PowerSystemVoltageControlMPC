import numpy as np
from copy import deepcopy
from  time import time


from methods import PowerFlux
from methods import linearize
from methods import discretize
from .MPC import mpc

class multiAgent():
    def __init__(self, system, dae, system1, dae1, system2, dae2,  busp1, busp2, zIdx1, zUb1, zLb1, zIdx2, zUb2, zLb2,  N= 80, dT = 250e-3):
        #Prediction horizon
        self.N = N
        #Sampling time
        self.dT = dT
        #Subsystems
        self.dae1 = dae1
        self.dae2 = dae2
        self.system1 = system1
        self.system2 = system2
        #Create steady state copy
        self.dae1ss = deepcopy(dae1)
        self.dae2ss = deepcopy(dae2)
        #Crear mapeo de cada dispositivo en cada subsistema.
        for devi in system1.deviceList:
            system1.__dict__[devi].idxFull = []
            for namei in system1.__dict__[devi].name:
                try: 
                    system1.__dict__[devi].idxFull.append(system.__dict__[devi].deviceIdx[namei])
                except:
                    pass


        for devi in system2.deviceList:
            system2.__dict__[devi].idxFull = []
            for namei in system2.__dict__[devi].name:
                try: 
                    system2.__dict__[devi].idxFull.append(system.__dict__[devi].deviceIdx[namei])
                except:
                    pass
        
        # ------------------------------------------------------------------------
        # Inputs
        self.uIdx1 = system1.exc.vref
        self.uIdx2 = system2.exc.vref


        self.uIdx1Dae = [0, 1, 6, 7, 8]
        self.uIdx2Dae = [2, 3, 4, 5]

        # ------------------------------------------------------------------------
        #Bus Index
        self.busIdx1 = [system1.bus.deviceIdx[busi] for busi in busp1]
        self.busIdx2 = [system2.bus.deviceIdx[busi] for busi in busp2]
        #Index of voltage magnitude variable
        self.vmIdx1 = [system1.bus.vm[i] for i in self.busIdx1]
        self.vmIdx2 = [system2.bus.vm[i] for i in self.busIdx2]

        # ------------------------------------------------------------------------
        # Algrbraic variables of interest
        self.zIdx1 = zIdx1 #Index
        self.zUb1 = np.array(zUb1) #Upper Limit
        self.zLb1 = np.array(zLb1) #Lower Limit
        # Algrbraic variables of interest
        self.zIdx2 = zIdx2 #Index
        self.zUb2 = np.array(zUb2) #Upper Limit
        self.zLb2 = np.array(zLb2) #Lower Limit

        # ------------------------------------------------------------------------
       #Initialize variables
        self.ek1 = 0
        self.yr1k1 = np.zeros(len(self.vmIdx1)) #Deviation variables

        self.ek2 = 0
        self.yr1k2 = np.zeros(len(self.vmIdx2)) #Deviation variables

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


    def updateSubsystems(self, system, dae):
        for devi in self.system1.deviceList:
            #Skip controllable loads
            if devi == 'loadu':
                continue

            idxVar = self.system1.__dict__[devi].idxFull
            for statei in self.system1.__dict__[devi].states:
                idxVarDae = np.array(system.__dict__[devi].__dict__[statei], dtype = 'int')[idxVar]
                self.dae1.x[self.system1.__dict__[devi].__dict__[statei]] = dae.x[idxVarDae]

            for algi in self.system1.__dict__[devi].algebraics:
                idxVarDae = np.array(system.__dict__[devi].__dict__[algi], dtype = 'int')[idxVar]
                self.dae1.y[self.system1.__dict__[devi].__dict__[algi]] = dae.y[idxVarDae]
                
            for inputi in self.system1.__dict__[devi].inputs:
                idxVarDae = np.array(system.__dict__[devi].__dict__[inputi], dtype = 'int')[idxVar]
                self.dae1.u[self.system1.__dict__[devi].__dict__[inputi]] = dae.u[idxVarDae]

            for pari in self.system1.__dict__[devi].parameters:
                self.system1.__dict__[devi].__dict__[pari] = system.__dict__[devi].__dict__[pari][idxVar]


        for devi in self.system2.deviceList:
            #Skip controllable loads
            if devi == 'loadu':
                continue
            idxVar = self.system2.__dict__[devi].idxFull
            for statei in self.system2.__dict__[devi].states:
                idxVarDae = np.array(system.__dict__[devi].__dict__[statei], dtype = 'int')[idxVar]
                self.dae2.x[self.system2.__dict__[devi].__dict__[statei]] = dae.x[idxVarDae]

            for algi in self.system2.__dict__[devi].algebraics:
                idxVarDae = np.array(system.__dict__[devi].__dict__[algi], dtype = 'int')[idxVar]
                self.dae2.y[self.system2.__dict__[devi].__dict__[algi]] = dae.y[idxVarDae]
                
            for inputi in self.system2.__dict__[devi].inputs:
                idxVarDae = np.array(system.__dict__[devi].__dict__[inputi], dtype = 'int')[idxVar]
                self.dae2.u[self.system2.__dict__[devi].__dict__[inputi]] = dae.u[idxVarDae]

            for pari in self.system2.__dict__[devi].parameters:
                self.system2.__dict__[devi].__dict__[pari] = system.__dict__[devi].__dict__[pari][idxVar]

        #Actualizar cargas virtuales.
        # Compute power flux
        sFrom, sTo = PowerFlux(system, dae)
        # system1
        self.dae1.u[self.system1.loadu.ph] = np.hstack([- 1 * sTo[18].real, -1 * sFrom[20].real])
        self.dae1.u[self.system1.loadu.qh] = np.hstack([- 1 * sTo[18].imag, -1 * sFrom[20].imag])

        # system2
        self.dae2.u[self.system2.loadu.ph] = np.hstack([-1 * sFrom[18].real, -1 * sTo[20].real])
        self.dae2.u[self.system2.loadu.qh] = np.hstack([-1 * sFrom[18].imag, -1 * sTo[20].imag])
    
    
    def computeAll(self, system, dae):
        #Update variables and parameters
        self.updateSubsystems(system, dae)
        # Compute admittance matrices
        self.system1.makeYbus()
        self.system2.makeYbus()
        #Reinit jacobians
        self.dae1ss.reInitG()
        self.dae1ss.reInitF()
        self.dae2ss.reInitG()
        self.dae2ss.reInitF()
        #compute functions
        self.system1.computeF(self.dae1ss)
        self.system1.computeG(self.dae1ss, self.system1.Ybus)
        self.system2.computeF(self.dae2ss)
        self.system2.computeG(self.dae2ss, self.system2.Ybus)
    def execute(self, system, dae):
        #Update subsystems
        self.updateSubsystems(system, dae)
        # Steady state variables
        xss1 = np.array(self.dae1ss.x) #States
        yss1 = np.array(self.dae1ss.y[self.vmIdx1]) #Outputs
        uss1 = np.array(self.dae1ss.u[self.uIdx1]) #Inputs
        zss1 = np.array(self.dae1ss.y[self.zIdx1]) #Algebraic variables.

        xss2 = np.array(self.dae2ss.x) #States
        yss2 = np.array(self.dae2ss.y[self.vmIdx2]) #Outputs
        uss2 = np.array(self.dae2ss.u[self.uIdx2]) #Inputs
        zss2 = np.array(self.dae2ss.y[self.zIdx2]) #Algebraic variables.

        # =========================================================================================0
        # System 1
        #Initial states
        xk1 = self.dae1.x[:] - xss1
        #Initial outputs
        y1k1 = self.dae1.y[self.vmIdx1] - yss1
        #Previous input
        u1k1 = self.dae1.u[self.uIdx1] - uss1
        #Previous reference
        yr1k1 = self.yr1k1[:]
        #Update error
        self.ek1 =  (y1k1 - yr1k1)
        #Initial value for error
        ek1 = np.array(self.ek1)

        #Number of states, inputs,  outputs and algebraic variables
        nx1 = xss1.shape[0]
        ny1 = yss1.shape[0]
        nu1 = uss1.shape[0]
        nz1 = zss1.shape[0]

        #Linearize system!
        (A1, B1, C1, D1, F1, G1) = self.linearizeSystem(self.dae1ss) #Use steady state variables
        # Discretize system
        Ad1, Bd1, Fd1 = discretize( A1, B1,  F1, dT = self.dT)  

        #Prediction model
        # For advanced indexing documentation see:  https://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#advanced-indexing 
        Idx = np.ix_(range(nx1), range(nx1))
        Ad1 = Ad1[Idx]

        Idx = np.ix_(range(nx1), self.uIdx1)  
        Bd1 = Bd1[Idx]    

        Idx = list(range(nx1))
        Fd1 = Fd1[Idx]  
        #Outputs!!!       
        Idx = np.ix_(self.vmIdx1, range(nx1))
        Cd1 = C1[Idx]
        Idx = np.ix_(self.vmIdx1, self.uIdx1)    
        Dd1 = D1[Idx]
        Idx = self.vmIdx1
        Gd1 = G1[Idx]

        #Compute constant terms
        Fc1 = np.array(Fd1)
        Gc1 = np.array(Gd1)

        # Algebraic variables
        Idx = np.ix_(self.zIdx1, range(nx1))
        Cz1 = C1[Idx] 
        Idx = np.ix_(self.zIdx1, self.uIdx1)    
        Dz1 = D1[Idx]
        Idx = self.zIdx1
        Gz1 = G1[Idx]

        # -----------------------------------------------------------
        #Restictions: 
        #states
        xmax1 = np.inf * np.ones(nx1) - xss1
        xmin1 = - np.inf * np.ones(nx1) - xss1
        #inputs
        umax1 = 1.5 * np.ones(nu1) - uss1
        umin1 = -1.5 * np.ones(nu1) - uss1
        #Rate of change
        dumax1 = 0.02 * np.ones(nu1)
        dumin1 = - 0.02 * np.ones(nu1)
        #Outputs
        ymax1 = 1.1 * np.ones(ny1) - yss1
        ymin1 = 0.9 * np.ones(ny1) - yss1
        #Outputs
        yrmax1 = 0.02 * np.ones(ny1)
        yrmin1 = -0.02 * np.ones(ny1)
        #Rate of change
        dyrmax1 = 0.001 * np.ones(ny1)
        dyrmin1 = -0.001 * np.ones(ny1)
        # Algebraic
        zmax1 = self.zUb1 - zss1
        zmin1 = self.zLb1 - zss1

        # --------------------------------------------------
        #Weigths!!!
        qx1 = 0.0 * np.ones(nx1)
        qe1 = 20.0 * np.ones(ny1)
        qe1[-2:] = 0.0 #Sin penalidad en la primera iteracion
        qu1 = 0.5 * np.ones(nu1)
        qyr1 = 1.0 * np.ones(ny1)

        qxf1 = 0.0* np.ones(nx1)
        qef1 = 20* np.ones(ny1)
        qef1[-2:] = 0.0

        #Horizon
        N = self.N

        #Compute inputs
        if abs(dae.f[system.syn4.omega].mean()) > 1.25e-5:
            t1 = time()
            uk, yrk, z = mpc(Ad1, Bd1, Cd1, Dd1,  Fc1, Gc1, xk1, ek1, u1k1, yr1k1, xmax1, xmin1, umax1, umin1, dumax1, dumin1, ymax1, ymin1, yrmax1, yrmin1, dyrmax1, dyrmin1, qx1, qe1, qu1, qyr1, qxf1, qef1, zmax1, zmin1, Cz1, Dz1, Gz1, N= N)
            print('Elapsed Time: %.3f' %(time() - t1) )
            z1 = z + zss1
        else:
            uk, yrk = (u1k1, yr1k1)
            z1 = np.array(zss1)
        



        # =======================================================================================
        # System 2
        #Initial states
        xk2 = self.dae2.x[:] - xss2
        #Initial outputs
        y1k2 = self.dae2.y[self.vmIdx2] - yss2
        #Previous input
        u1k2 = self.dae2.u[self.uIdx2] - uss2
        #Previous reference
        yr1k2 = self.yr1k2[:]
        #Update error
        self.ek2 =  (y1k2 - yr1k2)
        #Initial value for error
        ek2 = np.array(self.ek2)

        #Number of states, inputs,  outputs and algebraic variables
        nx2 = xss2.shape[0]
        ny2 = yss2.shape[0]
        nu2 = uss2.shape[0]
        nz2 = zss2.shape[0]

        #Linearize system!
        (A2, B2, C2, D2, F2, G2) = self.linearizeSystem(self.dae2ss) #Use steady state variables
        # Discretize system
        Ad2, Bd2, Fd2 = discretize( A2, B2,  F2, dT = self.dT)  

        #Prediction model
        # For advanced indexing documentation see:  https://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#advanced-indexing 
        Idx = np.ix_(range(nx2), range(nx2))
        Ad2 = Ad2[Idx]

        Idx = np.ix_(range(nx2), self.uIdx2)  
        Bd2 = Bd2[Idx]    

        Idx = list(range(nx2))
        Fd2 = Fd2[Idx]  
        #Outputs!!!       
        Idx = np.ix_(self.vmIdx2, range(nx2))
        Cd2 = C2[Idx]
        Idx = np.ix_(self.vmIdx2, self.uIdx2)    
        Dd2 = D2[Idx]
        Idx = self.vmIdx2
        Gd2 = G2[Idx]

        #Compute constant terms
        Fc2 = np.array(Fd2)
        Gc2 = np.array(Gd2)

        # Algebraic variables
        Idx = np.ix_(self.zIdx2, range(nx2))
        Cz2 = C2[Idx] 
        Idx = np.ix_(self.zIdx2, self.uIdx2)    
        Dz2 = D2[Idx]
        Idx = self.zIdx2
        Gz2 = G2[Idx]

        # -----------------------------------------------------------
        #Restictions: 
        #states
        xmax2 = np.inf * np.ones(nx2) - xss2
        xmin2 = - np.inf * np.ones(nx2) - xss2
        #inputs
        umax2 = 1.5 * np.ones(nu2) - uss2
        umin2 = -1.5 * np.ones(nu2) - uss2
        #Rate of change
        dumax2 = 0.1 * np.ones(nu2)
        dumin2 = - 0.1 * np.ones(nu2)
        #Outputs
        ymax2 = 1.1 * np.ones(ny2) - yss2
        ymin2 = 0.9 * np.ones(ny2) - yss2
        #Outputs
        yrmax2 = 0.02 * np.ones(ny2)
        yrmin2 = -0.02 * np.ones(ny2)
        #Rate of change
        dyrmax2 = 0.001 * np.ones(ny2)
        dyrmin2 = -0.001 * np.ones(ny2)
        # Algebraic
        zmax2 = self.zUb2 - zss2
        zmin2 = self.zLb2 - zss2

        # --------------------------------------------------
        #Weigths!!!
        qx2 = 0.0 * np.ones(nx2)
        qe2 = 20.0 * np.ones(ny2)
        qe2[-2:] = 0.0
        qu2 = 0.5 * np.ones(nu2)
        qyr2 = 1.0 * np.ones(ny2)

        qxf2 = 0.0* np.ones(nx2)
        qef2 = 20* np.ones(ny2)
        qef2[-2:] = 0.0
       #Compute inputs
        if abs(dae.f[system.syn4.omega].mean()) > 1.25e-5:
            t1 = time()
            uk, yrk, z = mpc(Ad2, Bd2, Cd2, Dd2,  Fc2, Gc2, xk2, ek2, u1k2, yr1k2, xmax2, xmin2, umax2, umin2, dumax2, dumin2, ymax2, ymin2, yrmax2, yrmin2, dyrmax2, dyrmin2, qx2, qe2, qu2, qyr2, qxf2, qef2, zmax2, zmin2, Cz2, Dz2, Gz2, N= N)
            print('Elapsed Time: %.3f' %(time() - t1) )
            z2 = z + zss2
        else:
            uk, yrk = (u1k2, yr1k2)
            z2 = np.array(zss2)




        # -----------------------------------------------------------------------
        # ===========================================================================
        # Second Iteration
        #Reference for voltage at boarder
        v116 =  z1[-1]
        v117 =  z1[-2]
        v115 =  z1[-3]
        v114 =  z1[-4]

        v217 = z2[-1]
        v216 = z2[-2]
        v214 = z2[-3]
        v215 = z2[-4]

        v14 = (v214 + v114) * 0.5
        v15 = (v115 + v215) * 0.5
        v16 = (v116 + v216) * 0.5
        v17 = (v217 + v117) * 0.5

        #Previous reference
        yr1k1[-2:] = np.array([v14, v17]) - yss1[-2:]
        #Initial value for error
        self.ek1 =  (y1k1 - yr1k1)
        ek1 = np.array(self.ek1)


        #Previous reference
        yr1k2[-2:] = np.array([v15, v16]) - yss2[-2:]
        #Initial value for error
        self.ek2 =  (y1k2 - yr1k2)
        ek2 = np.array(self.ek2)

        qe1[-2:] = 1.0
        qef1[-2:] = 1.0
        qe2[-2:] = 1.0
        qef2[-2:] = 1.0
        #Compute inputs
        if abs(dae.f[system.syn4.omega].mean()) > 1.25e-5:
            t1 = time()
            uk, yrk, z = mpc(Ad1, Bd1, Cd1, Dd1,  Fc1, Gc1, xk1, ek1, u1k1, yr1k1, xmax1, xmin1, umax1, umin1, dumax1, dumin1, ymax1, ymin1, yrmax1, yrmin1, dyrmax1, dyrmin1, qx1, qe1, qu1, qyr1, qxf1, qef1, zmax1, zmin1, Cz1, Dz1, Gz1, N= N)
            print('Elapsed Time: %.3f' %(time() - t1) )
            z1 = z + zss1
        else:
            uk, yrk = (u1k1, yr1k1)
            z1 = np.array(zss1)
        


        #Update References!    
        self.yr1k1 = np.array(yrk)
        #Update inputs!!!
        dae.u[self.uIdx1Dae] = uk[:] + uss1


        # --------------------------------------------------
        # system2
       #Compute inputs
        if abs(dae.f[system.syn4.omega].mean()) > 1.25e-5:
            t1 = time()
            uk, yrk, z = mpc(Ad2, Bd2, Cd2, Dd2,  Fc2, Gc2, xk2, ek2, u1k2, yr1k2, xmax2, xmin2, umax2, umin2, dumax2, dumin2, ymax2, ymin2, yrmax2, yrmin2, dyrmax2, dyrmin2, qx2, qe2, qu2, qyr2, qxf2, qef2, zmax2, zmin2, Cz2, Dz2, Gz2, N= N)
            print('Elapsed Time: %.3f' %(time() - t1) )
            z2 = z + zss2
        else:
            uk, yrk = (u1k2, yr1k2)
            z2 = np.array(zss2)

        #Reference for boarder

        #Update References!    
        self.yr1k2 = np.array(yrk)
        #Update inputs!!!
        dae.u[self.uIdx2Dae] = uk[:] + uss2