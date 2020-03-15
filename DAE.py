from numpy import zeros
from numpy import empty
from scipy.sparse import csc_matrix, eye
from scipy.sparse.linalg import inv, expm
#My methods
import methods

class DAE():
    def __init__(self):
        self.nx = 0 #State variable counter
        self.ny = 0 #Algebraic variable counter
        self.nu = 0 #System inputs
        self.ng = 0 ##Algebraic equations counter

        self.xOut = empty(0) #Simulated states
        self.yOut = empty(0)  #Simulated algebraic variables

        self.uOut = empty(0) #Simulated input variables
        self.tOut = empty(0) #Simulation time 
# -------------------------------------------------------------
    def setUp(self):
        #Initialize arrays.
        self.x = zeros(self.nx) #States
        self.y = zeros(self.ny) #Algebraics
        self.u = zeros(self.nu) #Inputs
        
        self.f = zeros(self.nx) #Function f     
        self.g = zeros(self.ng) #Function g

        #Initialize jacobian matrix
        self.fx = csc_matrix((self.nx, self.nx))
        self.fy = csc_matrix((self.nx, self.ny))
        self.fu = csc_matrix((self.nx, self.nu))

        self.gx = csc_matrix((self.ng, self.nx))
        self.gy = csc_matrix((self.ng, self.ny))
        self.gu = csc_matrix((self.ng, self.nu))
# -------------------------------------------------------------

    def reInitF(self): 
        self.f = zeros(self.nx) #Function f    
        #Initialize jacobian matrix
        self.fx = csc_matrix((self.nx, self.nx))
        self.fy = csc_matrix((self.nx, self.ny))
        self.fu = csc_matrix((self.nx, self.nu))


# -------------------------------------------------------------
    def reInitG(self):
        self.g = zeros(self.ng) #Function g

        self.gx = csc_matrix((self.ng, self.nx))
        self.gy = csc_matrix((self.ng, self.ny))
        self.gu = csc_matrix((self.ng, self.nu))

# -------------------------------------------------------------    
    def linearize(self):
        #Get jacobians.
        fx = 1 * self.fx
        fy = 1 * self.fy
        fu = 1 * self.fu
        gx = 1 * self.gx
        gy = 1 * self.gy
        gu = 1 * self.gu
        #Get value of the functions.
        f0 = 1 * self.f
        g0 = 1 * self.g
        #Get the initial values.
        x0 = 1 * self.x
        y0 = 1 * self.y
        u0 = 1 * self.u
        #Linearize system.
        self.A, self.B, self.C, self.D, self.F, self.G = methods.linearize(fx, fy, fu, gx, gy, gu, f0, g0, x0, y0, u0)
# -------------------------------------------------------------
   
    def discretize(self, dT= 10e-3):
        self.Ad, self.Bd, self.Fd = methods.discretize(self.A, self.B, self.F,  dT=dT)


    # def linearize(self):
    #     # dX/dt = A * x + B * u + F0
    #     self.A = (self.fx - self.fy * inv(self.gy) * self.gx)
    #     self.B = (self.fu - self.fy * inv(self.gy) * self.gu)
    #     self.F0 = (self.f - self.fy * inv(self.gy) * self.g)

    #     # y = C * x + D * u
    #     self.C = - inv(self.gy) * self.gx
    #     self.D = - inv(self.gy) * self.gu
        # self.G0 = - inv(self.gy) * self.g


    
    # def discretize(self, dT = 1):
    #     I = eye(self.nx)

    #     #Uses the variation of parameters (lagrange method) to solve the set of linear equations of the form : dx/dt = Ax + f(t)
    #     self.Ad = expm(self.A * dT)
    #     self.Bd = inv(self.A) * (expm(self.A * dT) - I) * self.B
    #     self.F0d = inv(self.A) * (expm(self.A * dT) - I) * self.F0
        
    #     self.Cd = self.C
    #     self.Dd = self.D
    #     self.G0d = self.G0


