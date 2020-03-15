
from pypower.api import case9
from pypower.api import dSbus_dV
from pypower.api import runpf
from pypower.api import makeYbus
from pypower.api import ext2int
from pypower.idx_bus import VM, VA

import numpy as np

from scipy.sparse import csc_matrix
from scipy.sparse import vstack
from scipy.sparse import diags
from scipy.sparse.linalg import inv
from scipy.sparse import eye

def findPilot(Ybus, V, gIdx, lIdx, cll, nPilot = 1):
    dS_dVm, dS_dVa = dSbus_dV(Ybus, V)
    S = dS_dVm.imag

    Sgg = S[np.ix_(gIdx, gIdx)]
    Sgl = S[np.ix_(gIdx, lIdx)]
    Slg = S[np.ix_(lIdx, gIdx)]
    Sll = S[np.ix_(lIdx, lIdx)]

    # Compute elements quantity
    nG, nL = Sgl.shape 

    # Pilot node selection
    M = inv(Sll) #(3)
    B = -1 * inv(Sll) * Slg #(4)

    Qx = eye(nL)
    pIdx = []
    pOption = list(range(nL))
    
    CLL = diags(cll) #Load disturbances are modelled by a vector of Gaussian random variables with means equal to 0 and a covariance matrix denominated CLL.
    PL = M * CLL * M.transpose()
    #Inicializar
    C = csc_matrix((0, nL)) #Crear matriz de dimension 0 x nL
    for i in range(nPilot):
        fitBest = 1e6
        bestIdx = 0
        for j in pOption:
            Crow = csc_matrix(([1], ([0], [j])), shape=(1, nL))
            Ctmp = vstack([C, Crow], format='csc')
            CB = Ctmp * B 
            F = (CB).transpose() * inv(CB *CB.transpose())
            F = csc_matrix(F).reshape(nG, i+1)
            X = (eye(nL) - B * F * Ctmp)
            I = np.trace(( PL * X.transpose() * Qx * X).toarray())
            
            if I < fitBest:
                Cbest = 1 * Ctmp
                fitBest = 1 * I
                bestIdx = 1 * j
        
        C = 1 * Cbest
        pOption.remove(bestIdx)
        pIdx.append(bestIdx)

    pilotBus = [lIdx[i] for i in pIdx]

    return pilotBus






if __name__ == '__main__':
    print('-----------Start-----------')
    ppc, success = runpf(case9())
    ppc = ext2int(ppc)
    baseMVA = ppc['baseMVA']
    bus = ppc['bus']
    branch = ppc['branch']

    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)

    vm = bus[:, VM]
    va = 2 * np.pi * bus[:, VA]
    V = vm * np.exp(1j * va)

    gIdx = [0, 1, 2]
    lIdx = [3, 4, 5, 6, 7, 8]

    nPilot = 2
    pilotBus = findPilot(Ybus, V, gIdx, lIdx, nPilot)
    print(pilotBus)
