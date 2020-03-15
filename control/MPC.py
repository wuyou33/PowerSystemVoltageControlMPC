
from scipy import sparse
from scipy import linalg
from scipy.linalg import solve_discrete_are

import numpy as np
import osqp


import matplotlib.pyplot as plt


def computeQf(A, B, Q, R):
    A = A.toarray() if sparse.issparse(A) else 1 * A
    B = B.toarray() if sparse.issparse(B) else 1 * B
    Q = Q.toarray() if sparse.issparse(Q) else 1 * Q
    R = R.toarray() if sparse.issparse(R) else 1 * R


    # Compute solution of Ricatti algebraic equation
    return  sparse.csc_matrix(solve_discrete_are(A, B, Q, R))


def mpc(A, B, C, D,  F0, G0, xk, ek, uk1, yrk1, xmax, xmin, umax, umin, dumax, dumin, ymax, ymin, yrmax, yrmin, dyrmax, dyrmin, qx, qe, qu, qyr, qxf, qef, zmax, zmin, Cz, Dz, Gz, N= 10, dT = 250e-3):
    # =========================================================================================
    # Calculos
    # Calcular cantidad de elementos.
    [nx, nu] = B.shape
    [ny, nx] = C.shape
    [nz, nx] = Cz.shape





# -------------------------------------------------------------------------  
    #Calcular las matrices del estado aumentado
    A_ = sparse.vstack([
        sparse.hstack([A, sparse.csc_matrix((nx, ny))]),
        sparse.hstack([dT * C, sparse.eye(ny)])
    ], format='csc')

    B_ = sparse.vstack([
        sparse.hstack([B, sparse.csc_matrix((nx, ny))]),
        sparse.hstack([dT * D, -1 * dT * sparse.eye(ny)])
    ], format='csc')

    #Condiciones iniciales del estado aumentado
    xk_ = np.hstack([xk, ek])

    #Calcular tamaño del estado aumentado
    [nx_, nu_] = B_.shape

    #Calcular las matrices de las variables algebraicas considerando el estado aumentado.
    Cz_ = sparse.hstack([Cz, sparse.csc_matrix((nz, ny))], format = 'csc')
    Dz_ = sparse.hstack([Dz, sparse.csc_matrix((nz, ny))], format = 'csc')
# -------------------------------------------------------------------------    
    #Generar las matrices de pesos.
    Q = sparse.diags(np.hstack([qx, qe]), format='csc')
    R = sparse.diags(np.hstack([qu, qyr]), format='csc')
    

    
    
    # Qf = computeQf(A_, B_, Q, R) # Calcular la ganancia de la condición final tal que cumpla la ecuación de Ricatti.
    Qf = sparse.diags(np.hstack([qxf, qef]), format='csc') #Assigned directly.





    # Input diferences
    # dU = Kdu * u
    # Kdu =  sparse.kron(sparse.hstack([sparse.csc_matrix((N-1, 1)), sparse.eye(N-1)]), sparse.eye(nu_)) - sparse.kron(sparse.hstack([sparse.eye(N-1), sparse.csc_matrix((N-1, 1))]), sparse.eye(nu_))
    # # Rdu = Kdu.T * R * Kdu
    # Rdu = Kdu.transpose() * sparse.kron(sparse.eye(N-1), R ) * Kdu
  

    # Plantear problema de optimización
    # Problema de la forma : 0.5 xT P x + qT x
    # - quadratic objective
    qH = np.arange(1, N+1) / N
    # P = sparse.block_diag([sparse.kron(sparse.diags(qH), Q), #Estados durante el horizonte de predicción
    #                                             Qf,  # Estados al final del horizonte de predicción
    #                                             Rdu], format='csc') #Cambio en las entradas durante el horizonte de predicción

    P = sparse.block_diag([sparse.kron(sparse.diags(qH), Q), #Estados durante el horizonte de predicción
                                                Qf,  # Estados al final del horizonte de predicción
            sparse.kron(sparse.eye(N), R)], format='csc') #Entradas durante el horizonte de predicción

    # - linear objective
    q = np.zeros( (N+1)*nx_ + N*nu_)


    #==============================================================================
    #Restrictions
    #------------------------------------------------------------------------------
    #Equality restriction 
    #------------------------------------------------------------------------------
    #linear dynamics.
    # Aeq * [x, e, u, yr].T
    Ax = sparse.kron(sparse.eye(N+1),-sparse.eye(nx_)) + sparse.kron(sparse.eye(N+1, k=-1), A_)
    Bu = sparse.kron(sparse.vstack([sparse.csc_matrix((1, N)), sparse.eye(N)]), B_)
    Aeq = sparse.hstack([Ax, Bu])


    bk = - 1 * np.hstack([xk, ek, np.zeros(N*nx_)])
    b0 = - 1 * np.hstack([np.zeros(nx_), np.kron(np.ones(N), np.hstack([F0, dT * G0]))])
    b = b0  + bk 
    #Relajar un poco las restricciones de igualdad
    leq = b - 0.05 * abs(b)
    ueq = b + 0.05 * abs(b)
    #------------------------------------------------------------------------------
    #Inequality restriction 
    #------------------------------------------------------------------------------
    # - Bounds!!!!!
    xmin_ = np.hstack([xmin,np.kron(np.ones(ny), -np.inf)]) 
    xmax_ = np.hstack([xmax,np.kron(np.ones(ny), np.inf)])

    umin_ = np.hstack([umin, yrmin])
    umax_ = np.hstack([umax, yrmax])


    ABound = sparse.eye((N+1)*nx_ + N*nu_)
    lBound= np.hstack([np.kron(np.ones(N+1), xmin_), np.kron(np.ones(N), umin_)])
    uBound = np.hstack([np.kron(np.ones(N+1), xmax_), np.kron(np.ones(N), umax_)])



    #Maximum rate of change 
    dumin_ = np.hstack([dumin, dyrmin])
    dumax_ = np.hstack([dumax, dyrmax])
    uk1_ = np.hstack([uk1, yrk1])
    #Maximum rate of change
    Au = sparse.hstack([sparse.csc_matrix((N*nu_, (N+1)*nx_)),
            sparse.kron(sparse.eye(N), sparse.eye(nu_)) + sparse.kron(sparse.eye(N, k=-1), -1 * sparse.eye(nu_))])

    ldu = np.hstack([dumin_ + uk1_, np.kron(np.ones(N-1), dumin_)])
    udu = np.hstack([dumax_ + uk1_, np.kron(np.ones(N-1), dumax_)])



    # Algebraic variables
    Az = sparse.hstack([
        sparse.kron(sparse.hstack([sparse.eye(N), sparse.csc_matrix((N, 1))]), Cz_),
        sparse.kron(sparse.eye(N), Dz_)
    ])

    lz = np.kron(np.ones(N), zmin) - np.kron(np.ones(N), Gz)
    uz = np.kron(np.ones(N), zmax) - np.kron(np.ones(N), Gz)




    #------------------------------------------------------------------------------ 
    # - Solver constraints 
    #In general, the contraints have the form:
    #    lb <= Ax <= ub
    Aconst = sparse.vstack([Aeq, ABound, Au, Az], format='csc')
    lb = np.hstack([leq, lBound, ldu, lz])
    ub = np.hstack([ueq, uBound, udu, uz])

    #Condiciones iniciales  para las variables de optimización [x, e, u] a lo largo de todo el horizonte de predicción.
    _Xk_ = np.hstack ([np.kron(np.ones(N+1), xk_),np.kron(np.ones(N), uk1_)]) 
    # Create an OSQP object
    prob = osqp.OSQP()
    # ------------------------------------
    # Setup workspace
    #eps_abs: Absolute tolerance
    # eps_prim_inf: Primal  infeasibility  tolerance
    # eps_dual_inf: Dual  infeasibility  tolerance
    prob.setup(P, q, Aconst, lb, ub, verbose = False, polish = True,  eps_abs = 1e-6, eps_prim_inf=1e-5, eps_dual_inf = 1e-03)    
    # ------------------------------------
    #Start using initial conditions.
    prob.warm_start(x = _Xk_)
    #Solve problem
    res = prob.solve()

    # Check solver status
    if res.info.status not in  ['solved', 'solved inaccurate']:
        # The inaccurate status define when the optimality, primal infeasibility or dual infeasibility conditions are satisfied with tolerances 10 times largerthan the ones set.
        raise ValueError('OSQP did not solve the problem!')
    
    # Get firts inputs of the augmented state.
    _uk_ = res.x[-N*nu_:-(N-1)*nu_]
    uk = _uk_[:nu]
    yrk = _uk_[-ny:]

    # output = res.x[:N*nx_]

    # output = output.reshape((N, nx_))
    # plt.plot(output[:, 28])
    # plt.show()
    z = (Az * res.x + np.kron(np.ones(N), Gz))[-N*nz:-(N-1)*nz]
    return uk, yrk, z
