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

def cSimulation(system, dae, tMax = 1, dT = 10e-3,  iterMax = 10, tol = 1e-12, event = None, control= None):
    #dT0 Initial time step
    #dTMax maximum time step.
    #dTMin minimum time step
    
    #How often the control is to be executed...
    tControl = 0.25
    sControl = round(tControl/dT)

    #Number of elements
    nx = dae.nx
    ny = dae.ny
    nu = dae.nu
    #Number of steps
    nStep = round(tMax/dT)
    #Identity matrix
    Ix = identity(nx) 
    #Initialize time
    t = 0
    #Initialize Output
    dae.xOut = zeros((nStep,nx))
    dae.yOut = zeros((nStep,ny))
    dae.uOut = zeros((nStep,nu))
    dae.tOut = zeros(nStep)

    #Initialize flag event: Used to indicate that an event has ocurred...
    flagEvent = False

    #Loop!!!
    for step in range(nStep):
        #Show Progress
        if (step/nStep * 100 ) % 10 == 0:
            print('Progress: '+str(round(step/nStep * 100))+'%')

        #Eval event
        if not event == None:
            flagEvent = event(t, dT)
            #If an event an ocurred update system
            if flagEvent:
                #Topology
                system.makeYbus()
                print('========================================')
                print('*********An event has ocurred***********')
                print('========================================')
                # Inform the control agents about the change in topology
                if control != None:
                    control.computeAll(system, dae)
                #ReinitFlag
                flagEvent = False

        #Eval control
        if control != None and step%sControl == 0:
            control.execute(system, dae)

                
        #Compute matrices
        dae.reInitG()
        dae.reInitF()

        system.computeF(dae)
        system.computeG(dae, system.Ybus)


        #Current state
        ft = 1 * dae.f
        gt = 1 * dae.g
        xt = 1 * dae.x
        yt = 1 * dae.y
        ut = 1 * dae.u

        #Store Results
        dae.xOut[step, :] = dae.x
        dae.yOut[step, :] = dae.y
        dae.uOut[step, :] = dae.u
        dae.tOut[step] = t
        
        #Solve this integration step using Newton-Rhapson method
        converged = False
        nIter = 0
        while not converged:
            nIter += 1
            #Compute matrices
            dae.reInitG()
            dae.reInitF()

            system.computeF(dae)
            system.computeG(dae, system.Ybus)

            xi = 1 * dae.x
            fi = 1 * dae.f
            fxi = 1 * dae.fx
            fyi = 1 * dae.fy

            gi = 1 * dae.g
            gxi = 1 * dae.gx
            gyi = 1 * dae.gy

            qi = xi - xt - 0.5*dT*(fi + ft)

            Ac = hstack([
                vstack([Ix - 0.5*dT*fxi, gxi]), 
                vstack([-0.5*dT*fyi, gyi])
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

            dae.x = dae.x + dx
            dae.y = dae.y + dy    

        #If there is not convergence then return
        if not converged:            
            return

        #Update time
        t += dT            


