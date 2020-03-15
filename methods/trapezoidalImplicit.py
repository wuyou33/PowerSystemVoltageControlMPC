#Libraries
from scipy.sparse.linalg import inv
from scipy.sparse.linalg import spsolve

from scipy.sparse import identity
from scipy.sparse import hstack
from scipy.sparse import vstack
from scipy.sparse import csc_matrix
from numpy import r_
from numpy import zeros
from numpy import empty
from numpy import Inf
from numpy.linalg import norm
from numpy import vstack as npvstack

def trapezoidalImplicit(System, DAE, tMax = 1,  dt = 10e-3, iterMax = 10, tol = 1e-5, event = None):
    #dt0 Initial time step
    #dtMax maximum time step.
    #dtMin minimum time step
    
    #Compute elements size
    nx = DAE.nx
    ny = DAE.ny
    nu = DAE.nu
    #Identity Matrix
    Ix = identity(nx) 
    #Event 
    flagEvent = False
    #Initialize time
    t = 0
    #Compute number of steps
    nStep = round(tMax/dt)
    #
    DAE.xOut = zeros((1,nx))
    DAE.yOut = zeros((1,ny))
    DAE.uOut = zeros((1,nu))
    DAE.tOut = zeros(1)

    #steps counter
    i = 0
    while  t <= tMax:
        #Show Progress
        if (t/tMax)*100 % 10 < (dt/tMax)*100:
            print('Progress: '+str(round((t/tMax)*100)))

        #Eval event
        if not event == None:
            flagEvent = event(t, dt)
        
        #In the case an  event has occurred compute again the ybus matrix.
        if flagEvent:
            System.makeYbus()
        
        # ------------------------------------------------------------------
        #Compute DAE matrices
        # Reinitilize matrices
        DAE.reInitG()
        DAE.reInitF()
        # Compute functions and jacobians
        System.computeF(DAE)
        System.computeG(DAE, System.Ybus)

        #Current state
        ft = DAE.f[:]
        gt = DAE.g[:]
        xt = DAE.x[:]
        yt = DAE.y[:]
        ut = DAE.u[:]
        
                
        #Solve this integration step
        converged = False
        nIter = 0
        while not converged:
            nIter += 1
            #Compute matrices
            DAE.reInitG()
            DAE.reInitF()

            System.computeF(DAE)
            System.computeG(DAE, System.Ybus)

            xi = DAE.x[:]
            fi = DAE.f[:]
            fxi = DAE.fx[:,:]
            fyi = DAE.fy[:,:]

            gi = DAE.g[:]
            gxi = DAE.gx[:,:]
            gyi = DAE.gy[:,:]

            qi = xi - xt - 0.5*dt*(fi + ft)

            Ac = hstack([
                vstack([Ix - 0.5*dt*fxi, gxi]), 
                vstack([-0.5*dt*fyi, gyi])
            ])

            phi = r_[qi, gi]

            #Compute update term
            dz = -1*spsolve(csc_matrix(Ac), phi)
            dx = dz[range(nx)]
            dy = dz[range(nx, nx+ny)]
            #Compute norm.
            normF = norm(dz, Inf)
            if normF < tol:
                converged = True            

            DAE.x = DAE.x + dx
            DAE.y = DAE.y + dy

            #Check number of iterations...
            if not converged and nIter > iterMax:
                print('Maximum number of iterations reached, process did not converged and will return..')
                break

                
        
        
        #Store Results
        if t == 0:
            DAE.xOut[0, :] = DAE.x
            DAE.yOut[0, :] = DAE.y
            DAE.uOut[0, :] = DAE.u
            DAE.tOut[0] = t
        else:
             DAE.xOut = npvstack([DAE.xOut, xt])
             DAE.yOut = npvstack([DAE.yOut, yt])
             DAE.uOut = npvstack([DAE.uOut, ut])
             DAE.tOut = npvstack([DAE.tOut, t])

        #Update time
        t += dt
        #Update counter
        i += 1

        #Store results

        #If there is not convergence then return
        if not converged:            
            return            


