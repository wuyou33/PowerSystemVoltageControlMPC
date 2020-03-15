# Import case data
from IEEE39 import case39
#Solvers
from methods import cSimulation
#Plotter
import matplotlib.pyplot as plt
#Standard
import time
#Control
from control import multiAgent
# Standard
import numpy as np
# -----------------------------------------------------
# Events
# -----------------------------------------------------
def stepChange(tEvent, System , DAE, t, dt):
    if tEvent-dt < t and t < tEvent + dt:
        # DAE.u[System.ieee1.vref[0]] += 0.001
        # System.load.p[5] = 0.0
        # System.load.q[5] = 0.0
        System.lne.status[23] = 0
        flagEvent = True
    else:
        flagEvent = False
    return flagEvent


if __name__ == '__main__':
    #Import system data
    system, dae, system1, dae1, system2, dae2 = case39()

    # -----------------------------------------------------
    #Control
    busp1= [5, 9, 14, 25, 28, 14, 17] # Pilot bus by name - last two are the boarder
    busp2= [20, 21, 23, 15, 16] # Pilot bus by name - last two are the boarder
    zIdx1= [45, 47, 49, 51, 53, 27, 55, 29, 57] # 
    zUb1= 1.1 * np.ones(len(zIdx1))
    zLb1= 0.9 * np.ones(len(zIdx1))
    zIdx2= [17, 19, 21, 23, 1, 25, 3, 27] # Last four 15, 14, 16, 17
    zUb2= 1.1 * np.ones(len(zIdx2))
    zLb2= 0.9 * np.ones(len(zIdx2))
    myControl = multiAgent(system, dae, system1, dae1, system2, dae2, busp1, busp2, zIdx1, zUb1, zLb1, zIdx2, zUb2, zLb2)
    # # Dynamic simulation!!!!
    tMax = 20 #(s)
    dT = 250e-3 #(s)
    #Discrete simulation.
    event = lambda t, dtMin:  stepChange(1, system, dae, t, dtMin)
    t1 = time.time()
    # dSimulation(system, dae, tMax=tMax, dT = 1e-3, event=event, control=agent)
    cSimulation(system, dae, tMax = tMax, dT = dT,  iterMax = 10, tol = 1e-4, event = event, control= myControl)

    print('Elapsed time: '+str(time.time()- t1))

    
    # Plot Results
    fig, axs = plt.subplots(2,2)
    idxvm = system.bus.vm
    idxAVR = system.exc.vref
    idxqh = system.syn4.qh
    #Voltages Averega
    axs[0,0].plot(dae.tOut, dae.yOut[:,idxvm].mean(axis = 1))
    #Angle
    axs[0,1].plot(dae.tOut, dae.yOut[:,idxvm])
    #Speed
    axs[1,0].plot(dae.tOut, dae.yOut[:,idxqh])
    #AVR
    axs[1,1].plot(dae.tOut, dae.uOut[:,idxAVR])
    plt.show()