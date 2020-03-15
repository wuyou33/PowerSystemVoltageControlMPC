from scipy.sparse import csc_matrix
from numpy import r_, ones, conj, pi, exp
def makeYbus(Bus, Lne = None, Tr2w = None):
    nb = Bus.n
    A = csc_matrix((nb,nb))
    if Lne == None:
        YLne = csc_matrix((nb, nb))
    else:
        #Lne        
        nl = Lne.n

        f = Lne.bus0Idx
        t = Lne.bus1Idx

        #Admitance and suceptance
        Ys = Lne.status / (Lne.r + 1j*Lne.x)
        Bc = Lne.status*Lne.b

        ##      | If |   | Yff  Yft |   | Vf |
        ##      |    | = |          | * |    |
        ##      | It |   | Ytf  Ytt |   | Vt |
        
        Ytt = Ys + 1j*Bc/2
        Yff = Ytt
        Yft = -1*Ys
        Ytf = -1*Ys


        ## connection matrix for line & from buses
        Cf = csc_matrix((ones(nl), (range(nl), f)), (nl, nb))
        ## connection matrix for line & to buses
        Ct = csc_matrix((ones(nl), (range(nl), t)), (nl, nb))

        i = r_[range(nl), range(nl)]


        YfLne = csc_matrix((r_[Yff, Yft], (i, r_[f, t])), (nl, nb))
        YtLne = csc_matrix((r_[Ytf, Ytt], (i, r_[f, t])), (nl, nb))

        YLne = Cf.T * YfLne + Ct.T * YtLne

        A = A + csc_matrix((ones(2*nl), (r_[f,t], r_[t,f])), (nb, nb))

    

    #-------------------------------------------------
    #Transformers
    if Tr2w == None:
        Ytr2w = csc_matrix((nb, nb))
    else:

        nl = Tr2w.n

        f = Tr2w.bus0Idx
        t = Tr2w.bus1Idx

        Ys = Tr2w.status / (Tr2w.r + 1j*Tr2w.x)
        a1 = Tr2w.ratio1*exp(1j * pi/180 * Tr2w.shift) #Transformer ratio and shift
        Ytt = Ys + 0.5 * Tr2w.b
        Yff = Ytt / (a1 * conj(a1))
        Yft = - Ys / conj(a1);
        Ytf = - Ys / a1;
        ## connection matrix for line & from buses
        Cf = csc_matrix((ones(nl), (range(nl), f)), (nl, nb))
        ## connection matrix for line & to buses
        Ct = csc_matrix((ones(nl), (range(nl), t)), (nl, nb))

        i = r_[range(nl), range(nl)]


        Yf = csc_matrix((r_[Yff, Yft], (i, r_[f, t])), (nl, nb))
        Yt = csc_matrix((r_[Ytf, Ytt], (i, r_[f, t])), (nl, nb))

        Ytr2w = Cf.T * Yf + Ct.T * Yt
        A = A + csc_matrix((ones(2*nl), (r_[f,t], r_[t,f])), (nb, nb))
        
    #Consolidate
    Ybus = YLne + Ytr2w
    
    return Ybus, A, YfLne, YtLne