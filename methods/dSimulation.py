# standard modules.
import numpy as np
import scipy.sparse as sp

def reLinearize(DAE, System, dT):
    #If there is an event compute again the matrices and linearize.
    #Compute admitance matrix
    System.makeYbus()
    #Reinit matrices.
    DAE.reInitG()
    DAE.reInitF()
    #Evaluate system dynamics
    System.computeF(DAE)
    System.computeG(DAE, System.Ybus)
    # Linearize and discretize system.    
    DAE.linearize()
    DAE.discretize(dT = dT)
    #Initial state
    x0 = 1 * DAE.x[:]
    y0 = 1 * DAE.y[:]
    u0 = 1 * DAE.u[:]  

    return x0, y0, u0

#----------------------------------------------------------------------------------------
def dSimulation(System, DAE, tMax = 0.5, dT = 100e-3, event = None, control = None):
    #Compute number of steps
    nStep = round(tMax/dT)
    #Number of variables
    nx = DAE.nx
    ny = DAE.ny
    nu = DAE.nu
    # Identity
    Ix = sp.eye(nx)

    #Results
    DAE.xOut = np.zeros((nStep,nx))
    DAE.yOut = np.zeros((nStep,ny))
    DAE.uOut = np.zeros((nStep,nu))
    DAE.tOut = np.zeros(nStep)

    #Linearize and discretize system
    x0, y0, u0 = reLinearize(DAE, System, dT)

    #Initialize time
    t = 0
    #Loop...
    for step in range(nStep):
        #Show Progress
        if (t/tMax)*100 % 10 < (dT/tMax)*100:
            print('Progress: '+str(round((t/tMax)*100)))

        #Eval event
        if not event == None:
            flagEvent = event(t, dT)
            if flagEvent:
                x0, y0, u0 = reLinearize(DAE, System, dT)


       
        # control.execute(System, DAE)
        
        #Current values
        xk = 1 * DAE.x[:]
        yk = 1 * DAE.y[:]
        uk = 1 * DAE.u[:]

        # xkp1 = A x + B u + G + (I - A) x0 - B u0 
        xc =  DAE.Fd - DAE.Ad * x0 - DAE.Bd * uk + x0 #Constant value.
        DAE.x[:] = DAE.Ad * xk + DAE.Bd * uk + xc

        yc = DAE.G - DAE.C * x0 - DAE.D * u0 + y0 
        DAE.y[:] = DAE.C * xk + DAE.D * uk + yc

        # Store results
        DAE.xOut[step,:] = xk
        DAE.yOut[step,:] = yk
        DAE.tOut[step] = t

        # if step%10 == 0:
        #     #Linearize and discretize system
        #     x0, y0, u0 = reLinearize(DAE, System, dT) 

        t = step*dT