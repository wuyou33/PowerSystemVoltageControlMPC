from numpy import array, angle, exp, linalg, conj, r_, Inf, pi, ones, unique
from numpy import flatnonzero as find
from numpy import array

import numpy as np

from scipy.sparse import csc_matrix, hstack, vstack
from scipy.sparse.linalg import spsolve

from pypower.api import dSbus_dV

def powerFlow(Ybus, Bus, Gen, Load, tol = 1e-10, maxIter = 20):

    #Bus parameters.
    nbus = Bus.n
    vm = array(Bus.vm0)
    va = array(Bus.va0 * pi/ 180)
    busType = array(Bus.busType)

    # Bus type
    ref = find(busType == 3) # ref bus index
    if not ref.size:
        ref  = array([find(busType == 2)[0]], dtype='int') # PV bus indices
        busType[ref] = 3
        print('No slack bus was set, will use bus with index: ' + str(ref))

    ref = find(busType == 3) # ref bus index
    pv  = find(busType == 2) # PV bus indices
    pq = find(busType == 1) # PQ bus indices

    # Gen parameters
    ngen = 0 #Number of generators
    genBus = array([], dtype = int) #Generator buses.
    pgen = array([])
    qgen = array([])
    for geni in Gen:  
        genBus = r_[genBus, geni.bus0Idx] #generators buses
        pgen = r_[pgen, geni.pgen] #generators buses
        qgen = r_[qgen, geni.qgen] #generators buses

        ngen += geni.n

    sgen = pgen + 1j * qgen

    # load parameters
    nload = 0 #Number of generators
    loadBus = array([], dtype = int) #Generator buses.
    pload = array([])
    qload = array([])
    for loadi in Load:
        loadi.loadIdx = array(range(nload, nload + loadi.n)) #Assign index to generators        
        loadBus = r_[loadBus, loadi.bus0Idx] #load buses
        pload = r_[pload, loadi.p] #Active power
        qload = r_[qload, loadi.q] #Reactive power
        nload += loadi.n
    
    sload = pload + 1j * qload

    #Check consistency....
    if not ref.size:
        raise Exception('There is no slack bus...')
    elif not (ref == genBus).any():
        raise Exception('No generator at slack bus...')




    ## set up indexing for updating V
    pvpq = r_[pv, pq]
    npv = len(pv)
    npq = len(pq)
    
    j1 = 0;         j2 = npv           ## j1:j2 - V angle of pv buses
    j3 = j2;        j4 = j2 + npq      ## j3:j4 - V angle of pq buses
    j5 = j4;        j6 = j4 + npq      ## j5:j6 - V mag of pq buses

    # Compute connectivity matrices
    Cg = csc_matrix((ones(ngen), (genBus, range(ngen))), shape = (nbus, ngen))
    Cl = csc_matrix((ones(nload), (loadBus, range(nload))), shape = (nbus, nload))

    #Compute SBUS
    sbus  = Cg*sgen - Cl*sload
    #Initial condition
    v = vm*exp(1j*va)

    #Evaluate F(x0)
    mis = v * conj(Ybus * v) - sbus

    F = r_[ mis[pv].real,
            mis[pq].real,
            mis[pq].imag ]

    normF = linalg.norm(F, Inf)

    if normF < tol:
        converged = True
    else:
        converged = False
    
    #Initilize
    iter = 0

    #Iterate!!!!
    while (not converged and iter <= maxIter):
        iter += 1
        ## evaluate Jacobian
        dS_dVm, dS_dVa = dSbus_dV(Ybus, v)

        J11 = dS_dVa[array([pvpq]).T, pvpq].real
        J12 = dS_dVm[array([pvpq]).T, pq].real
        J21 = dS_dVa[array([pq]).T, pvpq].imag
        J22 = dS_dVm[array([pq]).T, pq].imag

        J = vstack([
                hstack([J11, J12]),
                hstack([J21, J22])
            ], format="csr")

        ## compute update step
        dx = -1 * spsolve(J, F)


        ## update voltage
        if npv:
            va[pv] = va[pv] + dx[j1:j2]
        if npq:
            va[pq] = va[pq] + dx[j3:j4]
            vm[pq] = vm[pq] + dx[j5:j6]

        v = vm * exp(1j * va)

        ## evalute F(x)
        mis = v * conj(Ybus * v) - sbus
        F = r_[  mis[pv].real,
                 mis[pq].real,
                 mis[pq].imag  ]

        ## check for convergence
        normF = linalg.norm(F, Inf)
        if normF < tol:
            converged = True

    if not converged:
        raise Exception('Power Flow did not converged....')

    else: #Update elements
        Bus.vm0 = abs(v)
        Bus.va0 = angle(v)*180/pi

        #Update reactive power.
        sinj = v*conj(Ybus*v)
        sload = Cl*sload

        sgen = sinj + sload


        
        ua,uncount=unique(genBus,return_counts=True) #FInds the unique elements and count how many times each one appears in the array.

        for geni in Gen:
            for i in range(geni.n):
                #Divide reactive power between generators
                geniBus =  geni.bus0Idx[i] #generators buses
                j = find(ua == geniBus)
                geni.qgen[i] = sgen[ua[j]].imag / uncount[j] #Can be several generators at one bus.
                #Divide active power for generators at slack buses
                if (geniBus == ref).any():
                    j = find(ua == geniBus)
                    geni.pgen[i] = sgen[ua[j]].real / uncount[j]


            



def PowerFlux(system, dae):
    vmIdx = system.bus.vm
    vaIdx = system.bus.va
    bus0Idx = system.lne.bus0Idx
    bus1Idx = system.lne.bus1Idx
    #Compute complex voltage
    vm = dae.y[vmIdx]
    va = dae.y[vaIdx]
    v = vm * np.exp(1j * va)
    #Compute power injections
    status = system.lne.status
    sFrom = status * v[bus0Idx] * np.conj(system.YfLne * v)
    sTo   = status * v[bus1Idx] * np.conj(system.YtLne * v)

    return sFrom, sTo