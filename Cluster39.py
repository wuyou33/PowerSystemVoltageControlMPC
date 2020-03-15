from IEEE39 import case39
from methods import plot_dendrogram
from methods import  findPilot
import scipy.sparse as sp
import numpy as np
from pypower.api import dSbus_dV

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans

from matplotlib import pyplot as plt

def cluster(system, dae, busVc):
    # Initial voltage
    vm = np.array(system.bus.vm0)
    va = np.array(system.bus.va0) * np.pi/180
    v = vm * np.exp(1j * va)
    #Ybus matrix
    Ybus = sp.csc_matrix(system.Ybus)
    #Number of buses
    nBus = system.bus.n
    #Number of control devices
    nDev = len(busVc)
    # Compute jacobians
    dS_dVm, dS_dVa = dSbus_dV(Ybus, v)
    dQ_dV = dS_dVm.imag
    #Index of buses
    busIdx = [system.bus.deviceIdx[busi] for busi in busVc]
    #Conectivity matrix
    ir = busIdx
    ic = range(nDev)
    Cu = sp.csc_matrix((np.ones(nDev), (ir, ic)), shape = (nBus, nDev))
    # Sensitivity matrix
    Su = -sp.linalg.spsolve(dQ_dV, Cu)
    #Modified sensitivity matrix
    Xu = -np.log(abs(Su.toarray()))

    #Cluster
    A = sp.csc_matrix(system.A).toarray()
    nClusters = 2
    model = AgglomerativeClustering(affinity='euclidean',  n_clusters = nClusters, connectivity= A[0:29, 0:29])
    clusters = model.fit_predict(Xu[0:29, :])
    #Plot dendogram
    fig, ax = plt.subplots(1)
    labels = range(1, 30)
    plot_dendrogram(model, truncate_mode='level', p=30, labels= labels, ax=ax, color_threshold = 27.0, above_threshold_color = 'b')
    # Turn off tick labels
    ax.set_yticklabels([])
    ax.yaxis.set_ticks_position('none') 
    #Add text
    ax.text(0.15, 0.895, 'Area 1',  transform=ax.transAxes, fontsize=15)
    ax.text(0.85, 0.9275, 'Area 2',  transform=ax.transAxes, fontsize=15)
    #Change color
    t = ax.get_children()
    t[2].set_color('tab:gray')
    t[1].set_color('tab:red')
    t[0].set_color('tab:blue')
    #Save Figure
    oFile = 'dendrogram.eps'
    fig.savefig(oFile, format = 'eps')

    lIdx = list(range(29))
    gIdx = list(range(29, 39))



    cll = np.zeros(len(lIdx))
    cll[[2,3,6,7,11,14,15,17,19,20,22,23,24,25,26,27,28]] = 1

    pilotBus1 = findPilot(Ybus, v, gIdx, lIdx, cll, nPilot=8)
 
    # plt.show()

    return clusters

    



if __name__ == '__main__':
    system, dae, system1, dae1, system2, dae2= case39()
    #Buses with control devices
    busVc = [30, 32, 33, 34, 35, 36, 37, 38, 39] #by name!!!
    #Compute clusters
    cluster(system, dae, busVc)

    print('Hello')
