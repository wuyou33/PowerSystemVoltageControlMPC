# NOTA!!!!!!!
# Todo todo absolutamente todo, incluyendo los parámetros de las máquinas es en base de 100MVA!!!!

#Devices
from devices.topo import Bus
from devices.branch import Lne
from devices.branch import Tr2W
from devices.load import LoadExp
# SM
from devices.sm import Syn4
from devices.sm import Syn6
#Exciter
from devices.smControllers import IeeeT1
#Turbine - Governor
from devices.smControllers import constantTG
from devices.smControllers import GovTypeI
from devices.smControllers import GovTypeII
# Containers
from System import System
from DAE import DAE
#Methods
from methods import makeYbus
from methods import powerFlow
#Solvers
from methods import cSimulation
#Control!
from control import singleAgent


#Standar Libraries
# scipy
from scipy.sparse.linalg import inv
from scipy.sparse.linalg import spsolve
from scipy.sparse import identity
from scipy.sparse import hstack
from scipy.sparse import vstack
#numpy
from numpy import r_
from numpy import zeros
from numpy import nonzero
from numpy import savetxt
#others
import time
from copy import deepcopy
import matplotlib.pyplot as plt



# -----------------------------------------------------
# Events
# -----------------------------------------------------
def stepChange(tEvent, System , DAE, t, dt):
    if tEvent-dt < t and t < tEvent + dt:
        # DAE.u[System.ieee1.vref[0]] += 0.001
        # System.load.p[0] = 1.0
        System.lne.status[15] = 0
        flagEvent = True
    else:
        flagEvent = False
    return flagEvent



if __name__ == '__main__':
    #  Bus Data
    buses = [
        {"name":1,"vb":69,"vm0":1.06,"va0":0,"busType":3},
        {"name":2,"vb":69,"vm0":1.045,"va0":0,"busType":2},
        {"name":3,"vb":69,"vm0":1.01,"va0":0,"busType":2},
        {"name":4,"vb":69,"vm0":1.0119812500064,"va0":0,"busType":1},
        {"name":5,"vb":69,"vm0":1.01601212851648,"va0":0,"busType":1},
        {"name":6,"vb":13.8,"vm0":1.07,"va0":0,"busType":2},
        {"name":7,"vb":13.8,"vm0":1.04933554546119,"va0":0,"busType":1},
        {"name":8,"vb":18,"vm0":1.09,"va0":0,"busType":2},
        {"name":9,"vb":13.8,"vm0":1.03275628704842,"va0":0,"busType":1},
        {"name":10,"vb":13.8,"vm0":1.03176981634471,"va0":0,"busType":1},
        {"name":11,"vb":13.8,"vm0":1.0470800642238,"va0":0,"busType":1},
        {"name":12,"vb":13.8,"vm0":1.05342793937614,"va0":0,"busType":1},
        {"name":13,"vb":13.8,"vm0":1.04696694017315,"va0":0,"busType":1},
        {"name":14,"vb":13.8,"vm0":1.02070131123928,"va0":0,"busType":1}
    ]
    #Line data
    lines = [{"name":"Ln1","bus0":2,"bus1":5,"r":0.05695,"x":0.17388,"b":0.034,"status":1},
        {"name":"Ln2","bus0":6,"bus1":12,"r":0.12291,"x":0.25581,"b":0,"status":1},
        {"name":"Ln3","bus0":12,"bus1":13,"r":0.22092,"x":0.19988,"b":0,"status":1},
        {"name":"Ln4","bus0":6,"bus1":13,"r":0.06615,"x":0.13027,"b":0,"status":1},
        {"name":"Ln5","bus0":6,"bus1":11,"r":0.09498,"x":0.1989,"b":0,"status":1},
        {"name":"Ln6","bus0":11,"bus1":10,"r":0.08205,"x":0.19207,"b":0,"status":1},
        {"name":"Ln7","bus0":9,"bus1":10,"r":0.03181,"x":0.0845,"b":0,"status":1},
        {"name":"Ln8","bus0":9,"bus1":14,"r":0.12711,"x":0.27038,"b":0,"status":1},
        {"name":"Ln9","bus0":14,"bus1":13,"r":0.17093,"x":0.34802,"b":0,"status":1},
        {"name":"Ln10","bus0":7,"bus1":9,"r":0,"x":0.11001,"b":0,"status":1},
        {"name":"Ln11","bus0":1,"bus1":2,"r":0.01938,"x":0.05917,"b":0.0528,"status":1},
        {"name":"Ln12","bus0":3,"bus1":2,"r":0.04699,"x":0.19797,"b":0.0438,"status":1},
        {"name":"Ln13","bus0":3,"bus1":4,"r":0.06701,"x":0.17103,"b":0.0346,"status":1},
        {"name":"Ln14","bus0":1,"bus1":5,"r":0.05403,"x":0.22304,"b":0.0492,"status":1},
        {"name":"Ln15","bus0":5,"bus1":4,"r":0.01335,"x":0.04211,"b":0.0128,"status":1},
        {"name":"Ln16","bus0":2,"bus1":4,"r":0.05811,"x":0.17632,"b":0.0374,"status":1}, 
        {"name":"Ln20","bus0":8,"bus1":7,"r":0,"x":0.17615,"b":0,"status":1}
    ]

    # Tr2W data
    tr2ws = [
        {"name":"Ln17","bus0":5,"bus1":6,"r":0,"x":0.25202,"b":0,"status":1, 'ratio1': 0.932, 'ratio2': 1, 'shift': 0},
        {"name":"Ln18","bus0":4,"bus1":9,"r":0,"x":0.55618,"b":0,"status":1, 'ratio1': 0.969, 'ratio2': 1, 'shift': 0},
        {"name":"Ln19","bus0":4,"bus1":7,"r":0,"x":0.20912,"b":0,"status":1, 'ratio1': 0.978, 'ratio2': 1, 'shift': 0}
    ]
    #Load data
    loads = [
        {"name":'lod11',"bus0":11,"p":0.035,"q":0.018,"alpha":2,"beta":2,"status":1},
        {"name":'lod13',"bus0":13,"p":0.135,"q":0.058,"alpha":2,"beta":2,"status":1},
        {"name":'lod3',"bus0":3,"p":0.942,"q":0.19,"alpha":0,"beta":2,"status":1},
        {"name":'lod5',"bus0":5,"p":0.076,"q":0.016,"alpha":0,"beta":2,"status":1},
        {"name":'lod2',"bus0":2,"p":0.217,"q":0.127,"alpha":0,"beta":2,"status":1},
        {"name":'lod6',"bus0":6,"p":0.112,"q":0.075,"alpha":0,"beta":2,"status":1},
        {"name":'lod4',"bus0":4,"p":0.478,"q":0.04,"alpha":2,"beta":2,"status":1},
        {"name":'lod14',"bus0":14,"p":0.149,"q":0.05,"alpha":2,"beta":2,"status":1},
        {"name":'lod12',"bus0":12,"p":0.061,"q":0.016,"alpha":2,"beta":2,"status":1},
        {"name":'lod10',"bus0":10,"p":0.09,"q":0.058,"alpha":2,"beta":2,"status":1},
        {"name":'lod9',"bus0":9,"p":0.295,"q":0.166,"alpha":2,"beta":2,"status":1}
    ]

    #Generators
    syn4s = []
    syn6s = [
        {"name":'G1',"bus0":1,"sn":615,"vn":69,"fn":60,"ra":0,"xd":0.8979,"xd1":0.2998,"xd2":0.23,"Td10":7.4,"Td20":0.03,"xq":0.646,"xq1":0.646,"xq2":0.4,"Tq10":0.5,"Tq20":0.033,"H":5.148,"D":2,"pgen":0,"qgen":0.},
        {"name":'G2',"bus0":3,"sn":60,"vn":69,"fn":60,"ra":0.0031,"xd":1.05,"xd1":0.185,"xd2":0.13,"Td10":6.1,"Td20":0.04,"xq":0.98,"xq1":0.36,"xq2":0.13,"Tq10":0.3,"Tq20":0.099,"H":6.54,"D":2,"pgen":0.4,"qgen":0.},
        {"name":'G3',"bus0":2,"sn":60,"vn":69,"fn":60,"ra":0.0031,"xd":1.05,"xd1":0.185,"xd2":0.13,"Td10":6.1,"Td20":0.04,"xq":0.98,"xq1":0.36,"xq2":0.13,"Tq10":0.3,"Tq20":0.099,"H":6.54,"D":2,"pgen":0,"qgen":0.},
        {"name":'G4',"bus0":8,"sn":25,"vn":18,"fn":60,"ra":0.0014,"xd":1.25,"xd1":0.232,"xd2":0.12,"Td10":4.75,"Td20":0.06,"xq":1.22,"xq1":0.715,"xq2":0.12,"Tq10":1.5,"Tq20":0.21,"H":5.06,"D":2,"pgen":0,"qgen":0.},
        {"name":'G5',"bus0":6,"sn":25,"vn":13.8,"fn":60,"ra":0.0014,"xd":1.25,"xd1":0.232,"xd2":0.12,"Td10":4.75,"Td20":0.06,"xq":1.22,"xq1":0.715,"xq2":0.12,"Tq10":1.5,"Tq20":0.21,"H":5.06,"D":2,"pgen":0,"qgen":0.}
        ]

    exciters = [
        {"gen0":'G1',"name":'Exc1',"vrmax":7.32,"vrmin":0,"Ka":200,"Ta":0.02,"Kf":0.002,"Tf":1,"Te":0.2,"Ke":1,"Tr":0.001,"Ae":0.0006,"Be":0.9},
        {"gen0":'G3',"name":'Exc3',"vrmax":4.38,"vrmin":0,"Ka":20,"Ta":0.02,"Kf":0.001,"Tf":1,"Te":1.98,"Ke":1,"Tr":0.001,"Ae":0.0006,"Be":0.9},
        {"gen0":'G2',"name":'Exc2',"vrmax":4.38,"vrmin":0,"Ka":20,"Ta":0.02,"Kf":0.001,"Tf":1,"Te":1.98,"Ke":1,"Tr":0.001,"Ae":0.0006,"Be":0.9},
        {"gen0":'G4',"name":'Exc4',"vrmax":6.81,"vrmin":1.395,"Ka":20,"Ta":0.02,"Kf":0.001,"Tf":1,"Te":0.7,"Ke":1,"Tr":0.001,"Ae":0.0006,"Be":0.9},
        {"gen0":'G5',"name":'Exc5',"vrmax":6.81,"vrmin":1.395,"Ka":20,"Ta":0.02,"Kf":0.001,"Tf":1,"Te":0.7,"Ke":1,"Tr":0.001,"Ae":0.0006,"Be":0.9}
    ]

    #TG
    cTGs = [
            {'gen0': 'G1', 'name': 'cTG1'},
            {'gen0': 'G2', 'name': 'cTG2'},
            {'gen0': 'G3', 'name': 'cTG3'},
            {'gen0': 'G4', 'name': 'cTG4'},
            {'gen0': 'G5', 'name': 'cTG5'}
    ]





    # =============================================================
    #Instances
    # System instance
    system = System()
    # Devices
    system.bus = Bus() #Bus
    system.load = LoadExp()    #Loads
    system.lne = Lne() #Transmision line
    system.syn6 = Syn6() #Syncrhonpus machine 6 order
    system.tr2w = Tr2W() #2W transformers
    system.ieeet1 = IeeeT1() #Exciter
    system.cTG = constantTG()
    
    #Algebraic and States deposit
    dae = DAE()

    #List of devices.
    system.deviceList = ['bus', 'load', 'lne', 'syn6', 'tr2w', 'ieeet1', 'cTG']

# ----------------------------------------------
    #Add devices
    # buses
    for busi in buses:
        system.bus.addDevice(dae, busi)
    # Lines
    for devi in lines:
        system.lne.addDevice(dae, system.bus, devi)    
    # Tr2W
    for devi in tr2ws:
        system.tr2w.addDevice(dae, system.bus, devi)
    # Loads
    for devi in loads:
        system.load.addDevice(dae, system.bus, devi)
    #SM 6
    for devi in syn6s:
        system.syn6.addDevice(dae, system.bus, devi)

    for devi in exciters:
        system.ieeet1.addDevice(dae, system.syn6, devi)

    for devi in cTGs:
        system.cTG.addDevice(dae, system.syn6, devi)


    #Set Up devices
    dae.setUp()
    system.setUpDevices() 

    #Compute Ybus
    system.makeYbus()

    #runPF
    powerFlow(system.Ybus, system.bus, [system.syn6], [system.load])
    
    #Initialize devices
    system.initDevices(dae)

    #Compute matrices
    dae.reInitG()
    dae.reInitF()

    system.computeF(dae)
    system.computeG(dae, system.Ybus)


    # # Dynamic simulation!!!!
    tMax = 10 #(s)
    dT = 10e-3 #(s)
    event = lambda t, dtMin:  stepChange(1, system, dae, t, dtMin)
    # dSimulation(system, dae, tMax=tMax, dT = 1e-3, event=event, control=agent)
    cSimulation(system, dae, tMax = tMax, dT = dT,  iterMax = 10, tol = 1e-4, event = event, control= None)

    fig, axs = plt.subplots(2,2)
    #Voltages
    axs[0,0].plot(dae.tOut, dae.yOut[:,19])
    axs[0,0].plot(dae.tOut, dae.yOut[:,21])
    axs[0,0].plot(dae.tOut, dae.yOut[:,23])
    axs[0,0].plot(dae.tOut, dae.yOut[:,25])
    axs[0,0].plot(dae.tOut, dae.yOut[:,27])

    #Angle
    axs[0,1].plot(dae.tOut, dae.xOut[:,0])
    #Speed
    axs[1,0].plot(dae.tOut, dae.xOut[:,1])    

    #AVR
    axs[1,1].plot(dae.tOut, dae.uOut[:,0])
    axs[1,1].plot(dae.tOut, dae.uOut[:,1])
    axs[1,1].plot(dae.tOut, dae.uOut[:,2])

    
    plt.show()
    
    print('hello')

    savetxt('xOut.out', dae.xOut, delimiter=',')
    savetxt('yOut.out', dae.yOut, delimiter=',')
    savetxt('uOut.out', dae.uOut, delimiter=',')
    savetxt('tOut.out', dae.tOut, delimiter=',')