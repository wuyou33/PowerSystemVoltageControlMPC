#Devices
from devices.topo import Bus
from devices.branch import Lne
from devices.load import LoadExp
# SM
from devices.sm import Syn2
from devices.sm import Syn4
#Exciter
from devices.smControllers import IeeeT1
from devices.smControllers import constantEXC
#Turbine - Governor
from devices.smControllers import GovTypeI
from devices.smControllers import GovTypeII
from devices.smControllers import constantTG

# Containers
from System import System
from DAE import DAE

#Methods
from methods import makeYbus
from methods import powerFlow
from methods import linearize
from methods import findPilot

#Solvers
from methods import cSimulation
from methods import dSimulation


#Scipy
from scipy.sparse.linalg import inv
from scipy.sparse.linalg import spsolve
from scipy.sparse import identity
from scipy.sparse import hstack
from scipy.sparse import vstack

#Numpy
import numpy as np
from numpy import r_
from numpy import zeros
from numpy import nonzero
from numpy import savetxt


import time

from copy import deepcopy


#Control!
from control import singleAgent

import matplotlib.pyplot as plt

# -----------------------------------------------------
# Events
# -----------------------------------------------------
def stepChange(tEvent, System , DAE, t, dt):
    if tEvent-dt < t and t < tEvent + dt:
        # DAE.u[System.ieee1.vref[0]] += 0.001
        # System.load.p[0] = 0.45
        # System.load.q[0] = 0.15
        System.lne.status[4] = 0
        flagEvent = True
    else:
        flagEvent = False
    return flagEvent
        


if __name__ == '__main__':
    #Data test

    B1 = {'name':1,	'vm0':1.0107100,	'va0':0,	            'busType':3,	'vb':16.5}
    B2 = {'name':2,	'vm0':1.0264366,	'va0':9.2771202164,	    'busType':2,	'vb':18}
    B3 = {'name':3,	'vm0':1.0481214,	'va0':4.6639970783,	    'busType':2,	'vb':13.8}
    B4 = {'name':4,	'vm0':1.0000000,	'va0':-2.2167292632,	'busType':1,	'vb':230}
    B5 = {'name':5,	'vm0':1.0000000,    'va0':-3.9884666054,	'busType':1,	'vb':230}
    B6 = {'name':6,	'vm0':1.0000000,	'va0':-3.6875953007,	'busType':1,	'vb':230}
    B7 = {'name':7,	'vm0':1.0000000,	'va0':3.717641665,	    'busType':1,	'vb':230}
    B8 = {'name':8,	'vm0':1.0000000,	'va0':0.72619223781,	'busType':1,	'vb':230}
    B9 = {'name':9,	'vm0':1.0000000,	'va0':1.9659174013,	    'busType':1,	'vb':230}

    
    L1 = {'name':'Ln1',	'bus0':9,	'bus1':8,	'r':0.0119,	'x':0.1008,	'b':0.209,	'status':1}
    L2 = {'name':'Ln2',	'bus0':7,	'bus1':8,	'r':0.0085,	'x':0.072,	'b':0.149,	'status':1}
    L3 = {'name':'Ln3',	'bus0':9,	'bus1':6,	'r':0.039,	'x':0.17,	'b':0.358,	'status':1}
    L4 = {'name':'Ln4',	'bus0':7,	'bus1':5,	'r':0.032,	'x':0.161,	'b':0.306,	'status':1}
    L5 = {'name':'Ln5',	'bus0':5,	'bus1':4,	'r':0.01,	'x':0.085,	'b':0.176,	'status':1}
    L6 = {'name':'Ln6',	'bus0':6,	'bus1':4,	'r':0.017,	'x':0.092,	'b':0.158,	'status':1}
    T2 = {'name':'T2',	'bus0':2,	'bus1':7,	'r':0,	'x':0.0625,	'b':0,	'status':1}
    T3 = {'name':'T3',	'bus0':3,	'bus1':9,	'r':0,	'x':0.0586,	'b':0,	'status':1}
    T1 = {'name':'T1',	'bus0':1,	'bus1':4,	'r':0,	'x':0.0576,	'b':0,	'status':1}

    Ld1 = {'bus0':6,	'name':'ld6',	'p':0.9,	'q':0.3, 'alpha': 2.0, 'beta': 2.0, 'status':1}
    Ld2 = {'bus0':8,	'name':'ld8',	'p':1,	'q':0.35, 'alpha': 2.0, 'beta': 2.0,'status':1}
    Ld3 = {'bus0':5,	'name':'ld5',	'p':1.25, 'q':0.5, 'alpha': 2.0, 'beta': 2.0,'status':1}

    G1 = {'name':'G1',	'bus0':1,	'sn':100,	'vn':16.5,	'fn':60,	'ra':0,	'xd':0.146,	'xd1':0.0608,	'Td10':8.96,	'xq':0.0969,	'xq1':0.0969,	'Tq10':0.31,	'H':23.64,	'D':0,	'pgen':0.716,	'qgen':0.27}
    G2 = {'name':'G2',	'bus0':2,	'sn':100,	'vn':18,	'fn':60,	'ra':0,	'xd':0.8958,	'xd1':0.1198,	'Td10':6,	'xq':0.8645,	'xq1':0.1969,	'Tq10':0.535,	'H':6.4,	'D':0,	'pgen':1.63,	'qgen':0.067}
    G3 = {'name':'G3',	'bus0':3,	'sn':100,	'vn':13.8,	'fn':60,	'ra':0,	'xd':1.3125,	'xd1':0.1813,	'Td10':5.89,	'xq':1.2578,	'xq1':0.25,	'Tq10':0.6,	'H':3.01,	'D':0,	'pgen':0.85,	'qgen':-0.109}


    #Constant gvernor
    Gov1 = {'gen0':'G1', 'name': 'gov1'}
    #Simplified TG.    
    Gov2 = {'gen0':'G2', 'name': 'gov2', 'R': 0.05 , 'T1': 0.3, 'T2': 0.1, 'pmax': 2., 'pmin': 0}
    Gov3 = {'gen0':'G3', 'name': 'gov3', 'R': 0.05 , 'T1': 0.3, 'T2': 0.1, 'pmax': 1., 'pmin': 0}

    # Gov1 = {'gen0': 'G1', 'name': 'gov1', 'R': 0.02, 'Ts': 0.1, 'Tc': 0.45, 'T3': 0, 'T4': 0, 'T5': 50, 'pmax': 1.2, 'pmin': 0.3}
    # Gov2 = {'gen0': 'G2', 'name': 'gov2', 'R': 0.02, 'Ts': 0.1, 'Tc': 0.45, 'T3': 0, 'T4': 0, 'T5': 50, 'pmax': 1.2, 'pmin': 0.3}
    # Gov3 = {'gen0': 'G3', 'name': 'gov3', 'R': 0.02, 'Ts': 0.1, 'Tc': 0.45, 'T3': 0, 'T4': 0, 'T5': 50, 'pmax': 1.2, 'pmin': 0.3}
    
    Ex1 = {'gen0':'G1',	'vrmax':5.00,	'vrmin':-5.00,	'Ka':20.0, 'Ta':0.20, 'Kf':0.0635, 'Ke': 1.0, 'Tf':0.35, 'Te':0.314, 'Tr':0.001, 'Ae':0.0039, 'Be':1.555,	'name':'Ex1'}
    Ex2 = {'gen0':'G2',	'vrmax':5.00,	'vrmin':-5.00,	'Ka':20.0,	'Ta':0.20, 'Kf':0.0635,	'Ke': 1.0,'Tf':0.35, 'Te':0.314, 'Tr':0.001, 'Ae':0.0039, 'Be':1.555,	'name':'Ex2'}
    Ex3 = {'gen0':'G3',	'vrmax':5.00,	'vrmin':-5.00,	'Ka':20.0,	'Ta':0.20, 'Kf':0.0635,	'Ke': 1.0,'Tf':0.35, 'Te':0.314, 'Tr':0.001, 'Ae':0.0039, 'Be':1.555,	'name':'Ex3'}


    # =============================================================
    #Instances
    # System instance
    system = System()
    #Devices
    system.bus = Bus()
    system.load = LoadExp()    
    system.lne = Lne()
    # SM
    system.syn4 = Syn4()
    #Turbine- Governor
    system.gov1 = GovTypeI()
    system.gov2 = GovTypeII()
    system.cTg = constantTG()
    #Exciter
    system.ieee1 = IeeeT1()
    system.cExc = constantEXC()
    #Algebraic and States deposit
    dae = DAE()
    #List of devices.
    system.deviceList = ['bus', 'load', 'lne', 'syn4', 'gov2', 'cTg', 'ieee1']

    #Add devices.
    system.bus.addDevice(dae, B1)
    system.bus.addDevice(dae, B2)
    system.bus.addDevice(dae, B3)
    system.bus.addDevice(dae, B4)
    system.bus.addDevice(dae, B5)
    system.bus.addDevice(dae, B6)
    system.bus.addDevice(dae, B7)
    system.bus.addDevice(dae, B8)
    system.bus.addDevice(dae, B9)


    system.lne.addDevice(dae, system.bus, L1)
    system.lne.addDevice(dae, system.bus, L2)
    system.lne.addDevice(dae, system.bus, L3)
    system.lne.addDevice(dae, system.bus, L4)
    system.lne.addDevice(dae, system.bus, L5)
    system.lne.addDevice(dae, system.bus, L6)
    system.lne.addDevice(dae, system.bus, T1)
    system.lne.addDevice(dae, system.bus, T2)
    system.lne.addDevice(dae, system.bus, T3)

    system.load.addDevice(dae, system.bus, Ld1)
    system.load.addDevice(dae, system.bus, Ld2)
    system.load.addDevice(dae, system.bus, Ld3)

    system.syn4.addDevice(dae, system.bus, G1)
    system.syn4.addDevice(dae, system.bus, G2)
    system.syn4.addDevice(dae, system.bus, G3)

    system.cTg.addDevice(dae, system.syn4, Gov1)
    system.gov2.addDevice(dae, system.syn4, Gov2)
    system.gov2.addDevice(dae, system.syn4, Gov3)

    # system.gov1.addDevice(dae, system.syn4, Gov1)
    # system.gov1.addDevice(dae, system.syn4, Gov2)
    # system.gov1.addDevice(dae, system.syn4, Gov3)

    system.ieee1.addDevice(dae, system.syn4, Ex1)
    system.ieee1.addDevice(dae, system.syn4, Ex2)
    system.ieee1.addDevice(dae, system.syn4, Ex3)
    
    
    
    #Set Up devices
    dae.setUp()
    system.setUpDevices()    

    #Compute Ybus
    system.makeYbus()

    #runPF
    powerFlow(system.Ybus, system.bus, [system.syn4], [system.load])

    #Initialize
    system.initDevices(dae)

    #Compute matrices
    dae.reInitG()
    dae.reInitF()

    system.computeF(dae)
    system.computeG(dae, system.Ybus)


    #Create copy of DAE with steady state variables
    daeSS = deepcopy(dae)


    #Encontrar nodos piloto!
    V = dae.y[system.bus.vm] * np.exp(1j * dae.y[system.bus.vm])
    gIdx = [0, 1, 2]
    lIdx = [3, 4, 5, 6, 7, 8]
    cll = [0, 1, 1, 0, 1, 0] #Variance of loads
    buspilot = findPilot(system.Ybus, V, gIdx, lIdx , cll, nPilot = 3) #By index

    # ----------------------------------------------------------------------
    # Control!!!
    buspilot = [5, 6, 8] #By name
    uIdx = [0, 1, 2] #By Index
    #Algebraic variables of interest
    zIdx = [1,3,5]
    zUb =  1.1 * np.ones(len(zIdx))
    zLb =  0.9 * np.ones(len(zIdx))


    myControl = singleAgent(system, dae, daeSS, system.bus, buspilot = buspilot, zIdx = zIdx, zUb = zUb, zLb = zLb, uIdx = uIdx, N = 50)
    # ----------------------------------------------------------------------

    
    # # Dynamic simulation!!!!
    tMax = 200 #(s)
    dT = 25e-3 #(s)
    #Discrete simulation.
    event = lambda t, dtMin:  stepChange(50, system, dae, t, dtMin)
    t1 = time.time()
    # dSimulation(system, dae, tMax=tMax, dT = 1e-3, event=event, control=agent)
    cSimulation(system, dae, tMax = tMax, dT = dT,  iterMax = 10, tol = 1e-6, event = event, control= myControl)

    print('Elapsed time: '+str(time.time()- t1))
 

    # ======================================================================
    # Graphs

    # Variables of interest
    idxqh = system.syn4.qh
    idxvm = system.bus.vm
    idxAVR = system.ieee1.vref
    fig, axs = plt.subplots(2,2)
    #Voltages
    axs[0,0].plot(dae.tOut, dae.yOut[:,idxvm])
    axs[0,0].legend(["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"], loc = 4)
    #Angle
    axs[0,1].plot(dae.tOut, dae.xOut[:,0])
    #Speed
    axs[1,0].plot(dae.tOut, dae.xOut[:,1])
    #AVR
    axs[1,1].plot(dae.tOut, dae.uOut[:,idxAVR])




    fig, axs = plt.subplots(2,2)
    axs[0,0].plot(dae.tOut, dae.yOut[:, idxqh])

    # axs[1,1].plot(dae.tOut, dae.uOut[:,1])
    # axs[1,1].plot(dae.tOut, dae.uOut[:,2])
    

    axs[0,1].plot(myControl.tOut, myControl.yrOut)
    axs[1,0].plot(myControl.tOut, myControl.eOut)
    # plt.show()
    

    tp  = '_zc'

    savetxt('xOut' +tp + '.out', dae.xOut, delimiter=',')
    savetxt('yOut' +tp + '.out', dae.yOut, delimiter=',')
    savetxt('uOut' +tp + '.out', dae.uOut, delimiter=',')
    savetxt('tOut' +tp + '.out', dae.tOut, delimiter=',')
    
    savetxt('yrOut' +tp + '.out', myControl.yrOut, delimiter=',')
    savetxt('tControlOut' +tp + '.out', myControl.tOut, delimiter=',')
    # print('hello')



    
