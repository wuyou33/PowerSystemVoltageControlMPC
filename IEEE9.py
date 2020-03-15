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

#Solvers
from methods import cSimulation
from methods import dSimulation


#Libraries
from scipy.sparse.linalg import inv
from scipy.sparse.linalg import spsolve
from scipy.sparse import identity
from scipy.sparse import hstack
from scipy.sparse import vstack

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
        # System.load.p[0] = 1.0
        System.lne.status[4] = 0
        flagEvent = True
    elif tEvent + 1 -dt < t and t < tEvent + 1 + dt:
        # DAE.u[System.ieee1.vref[0]] += 0.001
        # System.load.p[0] = 1.0
        System.lne.status[4] = 1
        flagEvent = True

    else:
        flagEvent = False
    return flagEvent
        


if __name__ == '__main__':
    #Data test
    B1 = {'name':1,	'vm0':1.0399999619,	'va0':0,	            'busType':2,	'vb':16.5}
    B2 = {'name':2,	'vm0':1.0250903822,	'va0':9.2771202164,	    'busType':2,	'vb':18}
    B3 = {'name':3,	'vm0':1.0249799136,	'va0':4.6639970783,	    'busType':3,	'vb':13.8}
    B4 = {'name':4,	'vm0':1.0258031244,	'va0':-2.2167292632,	'busType':1,	'vb':230}
    B5 = {'name':5,	'vm0':0.9956693748, 'va0':-3.9884666054,	'busType':1,	'vb':230}
    B6 = {'name':6,	'vm0':1.0126661843,	'va0':-3.6875953007,	'busType':1,	'vb':230}
    B7 = {'name':7,	'vm0':1.0258306828,	'va0':3.717641665,	    'busType':1,	'vb':230}
    B8 = {'name':8,	'vm0':1.0159208137,	'va0':0.72619223781,	'busType':1,	'vb':230}
    B9 = {'name':9,	'vm0':1.0323560524,	'va0':1.9659174013,	    'busType':1,	'vb':230}

    
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


    # G1 = {'name': 'G1', 'bus0':1,	'sn':100,	'vn':16.5,	'fn':60,	'ra':0, 	'xd1':0.0608,	'H':23.64,	'D':0.8,	'pgen':0.716,	'qgen':0.27}
    # G2 = {'name': 'G2', 'bus0':2,	'sn':100,	'vn':18,	'fn':60,	'ra':0,		'xd1':0.1198,	'H':6.4,	'D':0.8,	'pgen':1.63,	'qgen':0.067}
    # G3 = {'name': 'G3', 'bus0':3,	'sn':100,	'vn':13.8,	'fn':60,	'ra':0,		'xd1':0.1813,	'H':3.01,	'D':0.8,	'pgen':0.85,	'qgen':-0.109}

    Gov1 = {'gen0':'G1', 'name': 'gov1', 'R': 1.0e6 , 'T1': 0.3, 'T2': 0.1, 'pmax': 1., 'pmin': 0}
    Gov2 = {'gen0':'G2', 'name': 'gov2', 'R': 0.05 , 'T1': 0.3, 'T2': 0.1, 'pmax': 2., 'pmin': 0}
    Gov3 = {'gen0':'G3', 'name': 'gov3', 'R': 0.05 , 'T1': 0.3, 'T2': 0.1, 'pmax': 1., 'pmin': 0}


    Gov1 = {'gen0':'G1', 'name': 'gov1'}
    Gov2 = {'gen0':'G2', 'name': 'gov2'}
    Gov3 = {'gen0':'G3', 'name': 'gov3'}



    # Gov1 = {'gen0': 'G1', 'name': 'gov1', 'R': 0.02, 'Ts': 0.1, 'Tc': 0.45, 'T3': 0, 'T4': 0, 'T5': 50, 'pmax': 1.2, 'pmin': 0.3}
    # Gov2 = {'gen0': 'G2', 'name': 'gov2', 'R': 0.02, 'Ts': 0.1, 'Tc': 0.45, 'T3': 0, 'T4': 0, 'T5': 50, 'pmax': 1.2, 'pmin': 0.3}
    # Gov3 = {'gen0': 'G3', 'name': 'gov3', 'R': 0.02, 'Ts': 0.1, 'Tc': 0.45, 'T3': 0, 'T4': 0, 'T5': 50, 'pmax': 1.2, 'pmin': 0.3}
    
    # Ex1 = {'gen0':'G1',	'vrmax':5.00,	'vrmin':-5.00,	'Ka':20.0, 'Ta':0.20, 'Kf':0.0635, 'Ke': 1.0, 'Tf':0.35, 'Te':0.314, 'Tr':0.001, 'Ae':0.0039, 'Be':1.555,	'name':'Ex1'}
    # Ex2 = {'gen0':'G2',	'vrmax':5.00,	'vrmin':-5.00,	'Ka':20.0,	'Ta':0.20, 'Kf':0.0635,	'Ke': 1.0,'Tf':0.35, 'Te':0.314, 'Tr':0.001, 'Ae':0.0039, 'Be':1.555,	'name':'Ex2'}
    # Ex3 = {'gen0':'G3',	'vrmax':5.00,	'vrmin':-5.00,	'Ka':20.0,	'Ta':0.20, 'Kf':0.0635,	'Ke': 1.0,'Tf':0.35, 'Te':0.314, 'Tr':0.001, 'Ae':0.0039, 'Be':1.555,	'name':'Ex3'}

    Ex1 = {'gen0':'G1',	'name':'Ex1'}
    Ex2 = {'gen0':'G2',	'name':'Ex2'}
    Ex3 = {'gen0':'G3',	'name':'Ex3'}


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
    system.deviceList = ['bus', 'load', 'lne', 'syn4', 'gov1', 'gov2', 'ieee1', 'cExc', 'cTg']

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

    # system.gov2.addDevice(dae, system.syn4, Gov1)
    # system.gov2.addDevice(dae, system.syn4, Gov2)
    # system.gov2.addDevice(dae, system.syn4, Gov3)

    system.cTg.addDevice(dae, system.syn4, Gov1)
    system.cTg.addDevice(dae, system.syn4, Gov2)
    system.cTg.addDevice(dae, system.syn4, Gov3)

    # system.gov1.addDevice(dae, system.syn4, Gov1)
    # system.gov1.addDevice(dae, system.syn4, Gov2)
    # system.gov1.addDevice(dae, system.syn4, Gov3)

    system.cExc.addDevice(dae, system.syn4, Ex1)
    system.cExc.addDevice(dae, system.syn4, Ex2)
    system.cExc.addDevice(dae, system.syn4, Ex3)

    # system.ieee1.addDevice(dae, system.syn4, Ex1)
    # system.ieee1.addDevice(dae, system.syn4, Ex2)
    # system.ieee1.addDevice(dae, system.syn4, Ex3)
    

    
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

    # Control!!!
    buspilot = [4,5]
    # agent = singleAgent(system, dae, daeSS, system.bus, [system.ieee1], buspilot = buspilot)
    # agent.execute(system, dae)
    
    # # Dynamic simulation!!!!
    tMax = 10 #(s)
    dT = 50e-3 #(s)
    #Discrete simulation.
    event = lambda t, dtMin:  stepChange(1, system, dae, t, dtMin)
    t1 = time.time()
    # dSimulation(system, dae, tMax=tMax, dT = 1e-3, event=event, control=agent)
    cSimulation(system, dae, tMax = tMax, dT = dT,  iterMax = 10, tol = 1e-4, event = event, control= None)

    print('Elapsed time: '+str(time.time()- t1))
 

    fig, axs = plt.subplots(2,2)
    #Voltages
    axs[0,0].plot(dae.tOut, dae.yOut[:,1])
    axs[0,0].plot(dae.tOut, dae.yOut[:,3])
    axs[0,0].plot(dae.tOut, dae.yOut[:,5])
    axs[0,0].plot(dae.tOut, dae.yOut[:,7])
    axs[0,0].plot(dae.tOut, dae.yOut[:,9])
    axs[0,0].plot(dae.tOut, dae.yOut[:,11])
    axs[0,0].plot(dae.tOut, dae.yOut[:,13])
    axs[0,0].plot(dae.tOut, dae.yOut[:,15])
    axs[0,0].plot(dae.tOut, dae.yOut[:,17])
    #Angle
    axs[0,1].plot(dae.tOut, dae.xOut[:,0])
    #Speed
    axs[1,0].plot(dae.tOut, dae.xOut[:,1])
    #AVR
    # axs[1,1].plot(dae.tOut, dae.uOut[:,0])
    # axs[1,1].plot(dae.tOut, dae.uOut[:,1])
    # axs[1,1].plot(dae.tOut, dae.uOut[:,2])


    plt.show()


    savetxt('xOut.out', dae.xOut, delimiter=',')
    savetxt('yOut.out', dae.yOut, delimiter=',')
    savetxt('uOut.out', dae.uOut, delimiter=',')
    savetxt('tOut.out', dae.tOut, delimiter=',')
    
    # print('hello')



    
