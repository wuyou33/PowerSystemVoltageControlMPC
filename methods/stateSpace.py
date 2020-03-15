from scipy.sparse.linalg import inv, expm
from scipy.sparse import csc_matrix, eye
from scipy.sparse  import hstack, vstack
from scipy import signal
from numpy import zeros


# def discretize( A, B,  F, dT = 1):
#     nx = A.shape[0] #Number of states
#     I = eye(nx)

#     Ad = expm(A * dT)
#     Bd = inv(A) * (expm(A*dT) - I) * B
#     Fd = inv(A) * (expm(A*dT) - I) * F
    
#     return Ad, Bd, Fd

def discretize( A, B,  F, dT = 1):
    nx = A.shape[0]
    Ad = expm(A * dT)
    M = expm(dT * vstack([hstack([A, eye(nx)]),  csc_matrix((nx, 2 * nx))]))
    integral = M[:nx, nx:]
    Bd = integral * B
    Fd = integral * F

    return Ad, Bd, Fd




# def discretize( A, B,  F, dT = 1):
#     nx = A.shape[0] #Number of states
#     I = eye(nx)

#     Ad = (I + dT * A)
#     Bd = dT * B
#     Fd = dT * F

#     return Ad, Bd, Fd



   
def linearize(fx, fy, fu, gx, gy, gu, f0, g0, x0, y0, u0):
    # dX/dt = A * x + B * u + F0
    A = (fx - fy * inv(gy) * gx)
    B = (fu - fy * inv(gy) * gu)
    F = (f0 - fy * inv(gy) * g0) 

    # y = C * x + D * u + G0
    C = - inv(gy) * gx
    D = - inv(gy) * gu
    G = - inv(gy) * g0

    return A, B, C, D, F, G