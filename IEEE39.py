#Devices
from devices.topo import Bus
from devices.branch import Lne
from devices.load import LoadExp
from devices.load import LoadU
from devices.sm import Syn4
from devices.branch import Lne
from devices.branch import Tr2W
from devices.smControllers import IeeeT1
from devices.smControllers import constantEXC
from devices.smControllers import GovTypeII
from devices.smControllers import constantTG
# Containers
from System import System
from DAE import DAE

# Methods
from methods import powerFlow
from methods import PowerFlux

# standard
import numpy as np
from matplotlib import pyplot as plt

def case39():
    # ***********************************************************
    # Buses

    B1 = {"name": 1,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B2 = {"name": 2,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B3 = {"name": 3,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B4 = {"name": 4,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B5 = {"name": 5,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B6 = {"name": 6,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B7 = {"name": 7,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B8 = {"name": 8,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B9 = {"name": 9,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B10 = {"name": 10,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B11 = {"name": 11,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B12 = {"name": 12,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B13 = {"name": 13,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B14 = {"name": 14,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B15 = {"name": 15,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B16 = {"name": 16,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B17 = {"name": 17,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B18 = {"name": 18,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B19 = {"name": 19,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B20 = {"name": 20,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B21 = {"name": 21,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B22 = {"name": 22,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B23 = {"name": 23,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B24 = {"name": 24,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B25 = {"name": 25,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B26 = {"name": 26,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B27 = {"name": 27,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B28 = {"name": 28,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B29 = {"name": 29,    "busType": 1,    "vm0": 1.0,    "va0": 0.0,    "vb": 1}
    B30 = {"name": 30,    "busType": 2,    "vm0": 1.0475,    "va0": -3.7342,    "vb": 1}
    B31 = {"name": 31,    "busType": 3,    "vm0": 0.982,    "va0": 0.0,    "vb": 1}
    B32 = {"name": 32,    "busType": 2,    "vm0": 0.9831,    "va0": 1.7944,    "vb": 1}
    B33 = {"name": 33,    "busType": 2,    "vm0": 0.9972,    "va0": 2.8715,    "vb": 1}
    B34 = {"name": 34,    "busType": 2,    "vm0": 1.0123,    "va0": 1.459,    "vb": 1}
    B35 = {"name": 35,    "busType": 2,    "vm0": 1.0493,    "va0": 4.7751,    "vb": 1}
    B36 = {"name": 36,    "busType": 2,    "vm0": 1.0635,    "va0": 7.4572,    "vb": 1}
    B37 = {"name": 37,    "busType": 2,    "vm0": 1.0278,    "va0": 2.0485,    "vb": 1}
    B38 = {"name": 38,    "busType": 2,    "vm0": 1.0265,    "va0": 7.3024,    "vb": 1}
    B39 = {"name": 39,    "busType": 2,    "vm0": 1.03,    "va0": -10.0638,    "vb": 1}

    busList = [B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, B21, B22, B23, B24, B25, B26, B27, B28, B29, B30, B31, B32, B33, B34, B35, B36, B37, B38, B39]



    ld3    =    {"bus0": 3,    "name": 'ld3',    "p": 3.22,    "q": 0.024,    "alpha": 2,    "beta": 2,    "status": 1}
    ld4    =    {"bus0": 4,    "name": 'ld4',    "p": 5,    "q": 1.84,    "alpha": 2,    "beta": 2,    "status": 1}
    ld7    =    {"bus0": 7,    "name": 'ld7',    "p": 2.338,    "q": 0.84,    "alpha": 2,    "beta": 2,    "status": 1}
    ld8    =    {"bus0": 8,    "name": 'ld8',    "p": 5.22,    "q": 1.76,    "alpha": 2,    "beta": 2,    "status": 1}
    ld12    =    {"bus0": 12,    "name": 'ld12',    "p": 0.075,    "q": 0.88,    "alpha": 2,    "beta": 2,    "status": 1}
    ld15    =    {"bus0": 15,    "name": 'ld15',    "p": 3.2,    "q": 1.53,    "alpha": 2,    "beta": 2,    "status": 1}
    ld16    =    {"bus0": 16,    "name": 'ld16',    "p": 3.29,    "q": 0.323,    "alpha": 2,    "beta": 2,    "status": 1}
    ld18    =    {"bus0": 18,    "name": 'ld18',    "p": 1.58,    "q": 0.3,    "alpha": 2,    "beta": 2,    "status": 1}
    ld20    =    {"bus0": 20,    "name": 'ld20',    "p": 6.28,    "q": 1.03,    "alpha": 2,    "beta": 2,    "status": 1}
    ld21    =    {"bus0": 21,    "name": 'ld21',    "p": 2.74,    "q": 1.15,    "alpha": 2,    "beta": 2,    "status": 1}
    ld23    =    {"bus0": 23,    "name": 'ld23',    "p": 2.475,    "q": 0.846,    "alpha": 2,    "beta": 2,    "status": 1}
    ld24    =    {"bus0": 24,    "name": 'ld24',    "p": 3.086,    "q": -0.922,    "alpha": 2,    "beta": 2,    "status": 1}
    ld25    =    {"bus0": 25,    "name": 'ld25',    "p": 2.24,    "q": 0.472,    "alpha": 2,    "beta": 2,    "status": 1}
    ld26    =    {"bus0": 26,    "name": 'ld26',    "p": 1.39,    "q": 0.17,    "alpha": 2,    "beta": 2,    "status": 1}
    ld27    =    {"bus0": 27,    "name": 'ld27',    "p": 2.81,    "q": 0.755,    "alpha": 2,    "beta": 2,    "status": 1}
    ld28    =    {"bus0": 28,    "name": 'ld28',    "p": 2.06,    "q": 0.276,    "alpha": 2,    "beta": 2,    "status": 1}
    ld29    =    {"bus0": 29,    "name": 'ld29',    "p": 2.835,    "q": 0.269,    "alpha": 2,    "beta": 2,    "status": 1}
    ld31    =    {"bus0": 31,    "name": 'ld31',    "p": 0.092,    "q": 0.046,    "alpha": 2,    "beta": 2,    "status": 1}
    ld39    =    {"bus0": 39,    "name": 'ld39',    "p": 11.04,    "q": 2.5,    "alpha": 2,    "beta": 2,    "status": 1}

    loadList = [ld3,	ld4,	ld7,	ld8,	ld12,	ld15,	ld16,	ld18,	ld20,	ld21,	ld23,	ld24,	ld25,	ld26,	ld27,	ld28,	ld29,	ld31,	ld39]
    
    G1    =    {"bus0": 39,    "name": 'G1',    "pgen": 10.0,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 500,    "ra": 0,    "xd1": 0.006,    "xq1": 0.008,    "xd": 0.02,    "xq": 0.019,    "Td10": 7,    "Tq10": 0.7, "D":0, "fn": 60.0    }
    G2    =    {"bus0": 31,    "name": 'G2',    "pgen": 0.0,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 30.3,    "ra": 0,    "xd1": 0.0697,    "xq1": 0.17,    "xd": 0.295,    "xq": 0.282,    "Td10": 6.56,    "Tq10": 1.5, "D":0, "fn": 60.0    }
    G3    =    {"bus0": 32,    "name": 'G3',    "pgen": 6.5,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 35.8,    "ra": 0,    "xd1": 0.0531,    "xq1": 0.0876,    "xd": 0.2495,    "xq": 0.237,    "Td10": 5.7,    "Tq10": 1.5, "D":0, "fn": 60.0   }
    G4    =    {"bus0": 33,    "name": 'G4',    "pgen": 6.32,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 28.6,    "ra": 0,    "xd1": 0.0436,    "xq1": 0.166,    "xd": 0.262,    "xq": 0.258,    "Td10": 5.69,    "Tq10": 1.5, "D":0, "fn": 60.0   }
    G5    =    {"bus0": 34,    "name": 'G5',    "pgen": 5.08,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 26,    "ra": 0,    "xd1": 0.132,    "xq1": 0.166,    "xd": 0.67,    "xq": 0.62,    "Td10": 5.4,    "Tq10": 0.44, "D":0, "fn": 60.0    }
    G6    =    {"bus0": 35,    "name": 'G6',    "pgen": 6.5,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 34.8,    "ra": 0,    "xd1": 0.05,    "xq1": 0.0814,    "xd": 0.254,    "xq": 0.241,    "Td10": 7.3,    "Tq10": 0.4, "D":0 , "fn": 60.0   }
    G7    =    {"bus0": 36,    "name": 'G7',    "pgen": 5.6,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 26.4,    "ra": 0,    "xd1": 0.049,    "xq1": 0.186,    "xd": 0.295,    "xq": 0.292,    "Td10": 5.66,    "Tq10": 1.5, "D":0, "fn": 60.0    }
    G8    =    {"bus0": 37,    "name": 'G8',    "pgen": 5.4,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 24.3,    "ra": 0,    "xd1": 0.057,    "xq1": 0.0911,    "xd": 0.29,    "xq": 0.28,    "Td10": 6.7,    "Tq10": 0.41, "D":0, "fn": 60.0    }
    G9    =    {"bus0": 38,    "name": 'G9',    "pgen": 8.3,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 34.5,    "ra": 0,    "xd1": 0.057,    "xq1": 0.0587,    "xd": 0.2106,    "xq": 0.205,    "Td10": 4.79,    "Tq10": 1.96, "D":0, "fn": 60.0    }
    G10    =   {"bus0": 30,    "name": 'G10',    "pgen": 2.5,    "qgen": 0.0,    "sn": 100,    "vn": 1,    "H": 42,    "ra": 0,    "xd1": 0.031,    "xq1": 0.008,    "xd": 0.1,    "xq": 0.069,    "Td10": 10.2,    "Tq10": 0.1, "D":0, "fn": 60.0    }

    
    genList = [G1, G2, G3, G4, G5, G6, G7, G8, G9, G10]



    Ln1    =    {"name": 'Ln1',    "bus0": 1,    "bus1": 2,    "r": 0.0035,    "x": 0.0411,    "b": 0.6987,    "status": 1  }
    Ln2    =    {"name": 'Ln2',    "bus0": 1,    "bus1": 39,    "r": 0.001,    "x": 0.025,    "b": 0.75,    "status": 1  }
    Ln3    =    {"name": 'Ln3',    "bus0": 2,    "bus1": 3,    "r": 0.0013,    "x": 0.0151,    "b": 0.2572,    "status": 1  }
    Ln4    =    {"name": 'Ln4',    "bus0": 2,    "bus1": 25,    "r": 0.007,    "x": 0.0086,    "b": 0.146,    "status": 1  }
    Ln5    =    {"name": 'Ln5',    "bus0": 3,    "bus1": 4,    "r": 0.0013,    "x": 0.0213,    "b": 0.2214,    "status": 1  }
    Ln6    =    {"name": 'Ln6',    "bus0": 3,    "bus1": 18,    "r": 0.0011,    "x": 0.0133,    "b": 0.2138,    "status": 1  }
    Ln7    =    {"name": 'Ln7',    "bus0": 4,    "bus1": 5,    "r": 0.0008,    "x": 0.0128,    "b": 0.1342,    "status": 1  }
    Ln8    =    {"name": 'Ln8',    "bus0": 4,    "bus1": 14,    "r": 0.0008,    "x": 0.0129,    "b": 0.1382,    "status": 1  }
    Ln9    =    {"name": 'Ln9',    "bus0": 5,    "bus1": 6,    "r": 0.0002,    "x": 0.0026,    "b": 0.0434,    "status": 1  }
    Ln10    =    {"name": 'Ln10',    "bus0": 5,    "bus1": 8,    "r": 0.0008,    "x": 0.0112,    "b": 0.1476,    "status": 1  }
    Ln11    =    {"name": 'Ln11',    "bus0": 6,    "bus1": 7,    "r": 0.0006,    "x": 0.0092,    "b": 0.113,    "status": 1  }
    Ln12    =    {"name": 'Ln12',    "bus0": 6,    "bus1": 11,    "r": 0.0007,    "x": 0.0082,    "b": 0.1389,    "status": 1  }
    Ln13    =    {"name": 'Ln13',    "bus0": 7,    "bus1": 8,    "r": 0.0004,    "x": 0.0046,    "b": 0.078,    "status": 1  }
    Ln14    =    {"name": 'Ln14',    "bus0": 8,    "bus1": 9,    "r": 0.0023,    "x": 0.0363,    "b": 0.3804,    "status": 1  }
    Ln15    =    {"name": 'Ln15',    "bus0": 9,    "bus1": 39,    "r": 0.001,    "x": 0.025,    "b": 1.2,    "status": 1  }
    Ln16    =    {"name": 'Ln16',    "bus0": 10,    "bus1": 11,    "r": 0.0004,    "x": 0.0043,    "b": 0.0729,    "status": 1  }
    Ln17    =    {"name": 'Ln17',    "bus0": 10,    "bus1": 13,    "r": 0.0004,    "x": 0.0043,    "b": 0.0729,    "status": 1  }
    Ln18    =    {"name": 'Ln18',    "bus0": 13,    "bus1": 14,    "r": 0.0009,    "x": 0.0101,    "b": 0.1723,    "status": 1  }
    Ln19    =    {"name": 'Ln19',    "bus0": 14,    "bus1": 15,    "r": 0.0018,    "x": 0.0217,    "b": 0.366,    "status": 1  }
    Ln20    =    {"name": 'Ln20',    "bus0": 15,    "bus1": 16,    "r": 0.0009,    "x": 0.0094,    "b": 0.171,    "status": 1  }
    Ln21    =    {"name": 'Ln21',    "bus0": 16,    "bus1": 17,    "r": 0.0007,    "x": 0.0089,    "b": 0.1342,    "status": 1  }
    Ln22    =    {"name": 'Ln22',    "bus0": 16,    "bus1": 19,    "r": 0.0016,    "x": 0.0195,    "b": 0.304,    "status": 1  }
    Ln23    =    {"name": 'Ln23',    "bus0": 16,    "bus1": 21,    "r": 0.0008,    "x": 0.0135,    "b": 0.2548,    "status": 1  }
    Ln24    =    {"name": 'Ln24',    "bus0": 16,    "bus1": 24,    "r": 0.0003,    "x": 0.0059,    "b": 0.068,    "status": 1  }
    Ln25    =    {"name": 'Ln25',    "bus0": 17,    "bus1": 18,    "r": 0.0007,    "x": 0.0082,    "b": 0.1319,    "status": 1  }
    Ln26    =    {"name": 'Ln26',    "bus0": 17,    "bus1": 27,    "r": 0.0013,    "x": 0.0173,    "b": 0.3216,    "status": 1  }
    Ln27    =    {"name": 'Ln27',    "bus0": 21,    "bus1": 22,    "r": 0.0008,    "x": 0.014,    "b": 0.2565,    "status": 1  }
    Ln28    =    {"name": 'Ln28',    "bus0": 22,    "bus1": 23,    "r": 0.0006,    "x": 0.0096,    "b": 0.1846,    "status": 1  }
    Ln29    =    {"name": 'Ln29',    "bus0": 23,    "bus1": 24,    "r": 0.0022,    "x": 0.035,    "b": 0.361,    "status": 1  }
    Ln30    =    {"name": 'Ln30',    "bus0": 25,    "bus1": 26,    "r": 0.0032,    "x": 0.0323,    "b": 0.513,    "status": 1  }
    Ln31    =    {"name": 'Ln31',    "bus0": 26,    "bus1": 27,    "r": 0.0014,    "x": 0.0147,    "b": 0.2396,    "status": 1  }
    Ln32    =    {"name": 'Ln32',    "bus0": 26,    "bus1": 28,    "r": 0.0043,    "x": 0.0474,    "b": 0.7802,    "status": 1  }
    Ln33    =    {"name": 'Ln33',    "bus0": 26,    "bus1": 29,    "r": 0.0057,    "x": 0.0625,    "b": 1.029,    "status": 1  }
    Ln34    =    {"name": 'Ln34',    "bus0": 28,    "bus1": 29,    "r": 0.0014,    "x": 0.0151,    "b": 0.249,    "status": 1  }

    lneList = [Ln1,	Ln2,	Ln3,	Ln4,	Ln5,	Ln6,	Ln7,	Ln8,	Ln9,	Ln10,	Ln11,	Ln12,	Ln13,	Ln14,	Ln15,	Ln16,	Ln17,	Ln18,	Ln19,	Ln20,	Ln21,	Ln22,	Ln23,	Ln24,	Ln25,	Ln26,	Ln27,	Ln28,	Ln29,	Ln30,	Ln31,	Ln32,	Ln33,	Ln34]

    

    Tr1    =    {"name": 'Tr1',    "bus0": 2,    "bus1": 30,    "r": 0,    "x": 0.0181,    "b": 0,    "status": 1,    "ratio1": 1.025,    "ratio2": 1,    "shift": 0  }
    Tr2    =    {"name": 'Tr2',    "bus0": 31,    "bus1": 6,    "r": 0,    "x": 0.025,    "b": 0,    "status": 1,    "ratio1": 0.85714,    "ratio2": 1,    "shift": 0  }
    Tr3    =    {"name": 'Tr3',    "bus0": 10,    "bus1": 32,    "r": 0,    "x": 0.02,    "b": 0,    "status": 1,    "ratio1": 1.07,    "ratio2": 1,    "shift": 0  }
    Tr4    =    {"name": 'Tr4',    "bus0": 12,    "bus1": 11,    "r": 0.0016,    "x": 0.0435,    "b": 0,    "status": 1,    "ratio1": 1.006,    "ratio2": 1,    "shift": 0  }
    Tr5    =    {"name": 'Tr5',    "bus0": 12,    "bus1": 13,    "r": 0.0016,    "x": 0.0435,    "b": 0,    "status": 1,    "ratio1": 1.006,    "ratio2": 1,    "shift": 0  }
    Tr6    =    {"name": 'Tr6',    "bus0": 19,    "bus1": 20,    "r": 0.0007,    "x": 0.0138,    "b": 0,    "status": 1,    "ratio1": 1.06,    "ratio2": 1,    "shift": 0  }
    Tr7    =    {"name": 'Tr7',    "bus0": 19,    "bus1": 33,    "r": 0.0007,    "x": 0.0142,    "b": 0,    "status": 1,    "ratio1": 1.07,    "ratio2": 1,    "shift": 0  }
    Tr8    =    {"name": 'Tr8',    "bus0": 20,    "bus1": 34,    "r": 0.0009,    "x": 0.018,    "b": 0,    "status": 1,    "ratio1": 1.009,    "ratio2": 1,    "shift": 0  }
    Tr9    =    {"name": 'Tr9',    "bus0": 22,    "bus1": 35,    "r": 0,    "x": 0.0143,    "b": 0,    "status": 1,    "ratio1": 1.025,    "ratio2": 1,    "shift": 0  }
    Tr10    =    {"name": 'Tr10',    "bus0": 23,    "bus1": 36,    "r": 0.0005,    "x": 0.0272,    "b": 0,    "status": 1,    "ratio1": 1,    "ratio2": 1,    "shift": 0  }
    Tr11    =    {"name": 'Tr11',    "bus0": 25,    "bus1": 37,    "r": 0.0006,    "x": 0.0232,    "b": 0,    "status": 1,    "ratio1": 1.025,    "ratio2": 1,    "shift": 0  }
    Tr12    =    {"name": 'Tr12',    "bus0": 29,    "bus1": 38,    "r": 0.0008,    "x": 0.0156,    "b": 0,    "status": 1,    "ratio1": 1.025,    "ratio2": 1,    "shift": 0  }

    trList = [Tr1,	Tr2,	Tr3,	Tr4,	Tr5,	Tr6,	Tr7,	Tr8,	Tr9,	Tr10,	Tr11,	Tr12]

    
    # Exciters!
    EX1    =    {'name': 'EX1',    'gen0': 'G1' }
    EX2    =    {'Ka': 6.2,    'Ta': 0.05,    'vrmin': -1,    'vrmax': 1,    'Kf': 0.405,    'Tf': 0.5,    'Ke': -0.633,    'Te': 0.405,    'Be': 0.284229887582359,    'Ae': 0.2784375,    'Tr': 0.01,    'name': 'EX2',    'gen0': 'G2' }
    EX3    =    {'Ka': 5,    'Ta': 0.06,    'vrmin': -1,    'vrmax': 1,    'Kf': 0.5,    'Tf': 1,    'Ke': -0.0198,    'Te': 0.5,    'Be': 1.23137542289164,    'Ae': 0.0072666904131895,    'Tr': 0.01,    'name': 'EX3',    'gen0': 'G3'    }
    EX4    =    {'Ka': 5,    'Ta': 0.06,    'vrmin': -1,    'vrmax': 1,    'Kf': 0.5,    'Tf': 1,    'Ke': -0.0525,    'Te': 0.5,    'Be': 1.43026520339115,    'Ae': 0.00132303399603038,    'Tr': 0.01,    'name': 'EX4',    'gen0': 'G4'    }
    EX5    =    {'Ka': 40,    'Ta': 0.02,    'vrmin': -10.5,    'vrmax': 10.5,    'Kf': 0.785,    'Tf': 1,    'Ke': 1,    'Te': 0.785,    'Be': 1.86630600866725,    'Ae': 3.18616294947655E-05,    'Tr': 0.01,    'name': 'EX5',    'gen0': 'G5'    }
    EX6    =    {'Ka': 5,    'Ta': 0.02,    'vrmin': -1,    'vrmax': 1,    'Kf': 0.471,    'Tf': 1.246,    'Ke': -0.0419,    'Te': 0.471,    'Be': 1.14299902736779,    'Ae': 0.00106095931823254,    'Tr': 0.01,    'name': 'EX6',    'gen0': 'G6'    }
    EX7    =    {'Ka': 40,    'Ta': 0.02,    'vrmin': -6.5,    'vrmax': 6.5,    'Kf': 0.73,    'Tf': 1,    'Ke': 1,    'Te': 0.73,    'Be': 0.357394050827424,    'Ae': 0.194718994926263,    'Tr': 0.01,    'name': 'EX7',    'gen0': 'G7'    }
    EX8    =    {'Ka': 5,    'Ta': 0.02,    'vrmin': -1,    'vrmax': 1,    'Kf': 0.528,    'Tf': 1.26,    'Ke': -0.047,    'Te': 0.528,    'Be': 1.28332649480673,    'Ae': 0.00119834718703948,    'Tr': 0.01,    'name': 'EX8',    'gen0': 'G8'    }
    EX9    =    {'Ka': 40,    'Ta': 0.02,    'vrmin': -10.5,    'vrmax': 10.5,    'Kf': 1.4,    'Tf': 1,    'Ke': 1,    'Te': 1.4,    'Be': 0.222364271304254,    'Ae': 0.240607954406676,    'Tr': 0.01,    'name': 'EX9',    'gen0': 'G9'    }
    EX10    =   {'Ka': 5,    'Ta': 0.06,    'vrmin': -1,    'vrmax': 1,    'Kf': 0.25,    'Tf': 1,    'Ke': -0.0485,    'Te': 0.25,    'Be': 0.997142126905033,    'Ae': 0.00233045061447428,    'Tr': 0.01,    'name': 'EX10',    'gen0': 'G10'    }


    excList = [EX2, EX3, EX4, EX5, EX6, EX7, EX8, EX9, EX10]



    #Constant gvernor
    Gov1 = {'gen0':'G1', 'name': 'gov1'}
    Gov2 = {'gen0':'G2', 'name': 'gov2'}
    Gov3 = {'gen0':'G3', 'name': 'gov3'}
    Gov4 = {'gen0':'G4', 'name': 'gov4'}
    Gov5 = {'gen0':'G5', 'name': 'gov5'}
    Gov7 = {'gen0':'G7', 'name': 'gov7'}
    Gov8 = {'gen0':'G8', 'name': 'gov8'}
    Gov9 = {'gen0':'G9', 'name': 'gov9'}

    Gov6 = {'gen0':'G6', 'name': 'gov6', 'R': 0.05 , 'T1': 0.3, 'T2': 0.1, 'pmax': 10., 'pmin': 0}
    Gov10 = {'gen0':'G10', 'name': 'gov10', 'R': 0.05 , 'T1': 0.3, 'T2': 0.1, 'pmax': 10., 'pmin': 0}

    govList = [Gov1, Gov2, Gov3, Gov4, Gov5, Gov7, Gov8, Gov9]
    # ***********************************************************
    #Instances
    # System instance
    system = System()
    #Algebraic and States deposit
    dae = DAE()
    #Devices
    system.bus = Bus()
    system.load = LoadExp() 
    system.loadu = LoadU() 
    system.syn4 = Syn4()
    system.lne = Lne()
    system.tr2w = Tr2W()
    #Exciter
    system.exc = IeeeT1()
    system.cExc = constantEXC()
    #Governor
    system.tG = GovTypeII()
    system.cTg = constantTG()
    # ***********************************************************
    #Add devices
    # Bus
    for devi in busList:
        system.bus.addDevice(dae, devi)

    # Loads
    for devi in loadList: 
        system.load.addDevice(dae, system.bus, devi)
    
    # Generators
    for devi in genList: 
        system.syn4.addDevice(dae, system.bus, devi)
    
    # Lines
    for devi in lneList: 
        system.lne.addDevice(dae, system.bus, devi)

    # Transformers
    for devi in trList: 
        system.tr2w.addDevice(dae, system.bus, devi)

    # Exciters
    for devi in excList: 
        system.exc.addDevice(dae, system.syn4, devi)
    
    system.cExc.addDevice(dae, system.syn4, EX1)

    # Governors
    for devi in govList: 
        system.cTg.addDevice(dae, system.syn4, devi)

    system.tG.addDevice(dae, system.syn4, Gov6)
    system.tG.addDevice(dae, system.syn4, Gov10)


    # system.loadu.addDevice(dae, system.bus, ld2)

    # ***********************************************************
    system.deviceList = ['bus', 'load', 'lne', 'tr2w', 'syn4', 'cExc', 'exc', 'tG', 'cTg']
    #Set Up devices
    dae.setUp()
    system.setUpDevices()   

    #Compute Ybus
    system.makeYbus()
    #runPF
    powerFlow(system.Ybus, system.bus, [system.syn4], [system.load, system.loadu])    

    #Initialize
    system.initDevices(dae)

    #Compute matrices
    dae.reInitG()
    dae.reInitF()

    system.computeF(dae)
    system.computeG(dae, system.Ybus)







    #==================================================================================
    # Subsystems!
    system1 = System()
    system2 = System()
    # Deposits
    dae1 = DAE()
    dae2 = DAE()
    # -----------------------------------------------------------------------------------
    #Buses
    system1.bus = Bus()
    system2.bus = Bus()

    busList1 = [B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B17, B18, B25, B26, B27, B28, B29, B39, B30, B31, B32, B37, B38, B15, B16]
    busList2 = [B15, B16, B19, B20, B21, B22, B23, B24, B33, B34, B35, B36, B14, B17]

    for devi in busList1:
        system1.bus.addDevice(dae1, devi)

    for devi in busList2:
        system2.bus.addDevice(dae2, devi)

    # -----------------------------------------------------------------------------------
    # Loads
    system1.load = LoadExp()
    system2.load = LoadExp()
    loadList1 = [ld3, ld4, ld7, ld8, ld12, ld18, ld25, ld26, ld27, ld28, ld29, ld31, ld39]  
    loadList2 = [ld15, ld16, ld20, ld21, ld23, ld24]  

    for devi in loadList1: 
        system1.load.addDevice(dae1, system1.bus, devi)
    for devi in loadList2: 
        system2.load.addDevice(dae2, system2.bus, devi)
    # -----------------------------------------------------------------------------------
    # Lines
    system1.lne = Lne()
    system2.lne = Lne()
    lneList1 = [Ln1, Ln2, Ln3, Ln4, Ln5, Ln6, Ln7, Ln8, Ln9, Ln10, Ln11, Ln12, Ln13, Ln14, Ln15, Ln16, Ln17, Ln18, Ln25, Ln26, Ln30, Ln31, Ln32, Ln33, Ln34, Ln21, Ln19]
    lneList2 = [Ln20, Ln22, Ln23, Ln24, Ln27, Ln28, Ln29, Ln19, Ln21]

    for devi in lneList1: 
        system1.lne.addDevice(dae1, system1.bus, devi)
    for devi in lneList2: 
        system2.lne.addDevice(dae2, system2.bus, devi)

    

    # -----------------------------------------------------------------------------------
    # Transformers
    trList1 = [Tr1,	Tr2,	Tr3,	Tr4,	Tr5,	Tr11,	Tr12]
    trList2 = [Tr6,	Tr7,	Tr8,	Tr9,	Tr10]
    system1.tr2w = Tr2W()
    system2.tr2w = Tr2W()

    for devi in trList1: 
        system1.tr2w.addDevice(dae1, system1.bus, devi)
    for devi in trList2: 
        system2.tr2w.addDevice(dae2, system2.bus, devi)

    # -----------------------------------------------------------------------------------
    # Generators   
    system1.syn4 = Syn4()
    system2.syn4 = Syn4()
    genList1 = [G1, G2, G3, G8, G9, G10]
    genList2 = [G4, G5, G6, G7]

    for devi in genList1: 
        system1.syn4.addDevice(dae1, system1.bus, devi)
    for devi in genList2: 
        system2.syn4.addDevice(dae2, system2.bus, devi)

    # -----------------------------------------------------------------------------------
    #Exciter
    system1.exc = IeeeT1()
    system1.cExc = constantEXC()
    system2.exc = IeeeT1()

    excList1 = [EX2, EX3, EX8, EX9, EX10]
    excList2 = [EX4, EX5, EX6, EX7]

    for devi in excList1: 
        system1.exc.addDevice(dae1, system1.syn4, devi)    
    system1.cExc.addDevice(dae1, system1.syn4, EX1)

    for devi in excList2: 
        system2.exc.addDevice(dae2, system2.syn4, devi)    

    # -----------------------------------------------------------------------------------
    #Governor
    system1.tG = GovTypeII()
    system1.cTg = constantTG()
    system2.tG = GovTypeII()
    system2.cTg = constantTG()

    govList1 = [Gov1, Gov2, Gov3, Gov8, Gov9]
    govList2 = [ Gov4, Gov5, Gov7]

    for devi in govList1: 
        system1.cTg.addDevice(dae1, system1.syn4, devi)
    for devi in govList2: 
        system2.cTg.addDevice(dae2, system2.syn4, devi)

    system1.tG.addDevice(dae1, system1.syn4, Gov10)
    system2.tG.addDevice(dae2, system2.syn4, Gov6)


    # -----------------------------------------------------------------------------------
    # Cargas controlables
    system1.loadu = LoadU()
    system2.loadu = LoadU()

    # Compute power flux
    sFrom, sTo = PowerFlux(system, dae)
    # system 1
    # bus 15
    ldU15 = {'bus0': 15, 'name': 'ldU15', 'p': - 1 * sTo[18].real, 'q': - 1 * sTo[18].imag}
    # bus 16
    ldU16 = {'bus0': 16, 'name': 'ldU16', 'p': -1 * sFrom[20].real, 'q': -1 * sFrom[20].imag}

    system1.loadu.addDevice(dae1, system1.bus, ldU15)
    system1.loadu.addDevice(dae1, system1.bus, ldU16)

    # system 2
    # bus 14
    ldU14 = {'bus0': 14, 'name': 'ldU14', 'p': -1 * sFrom[18].real, 'q': -1 * sFrom[18].imag}
    # bus 17
    ldU17 = {'bus0': 17, 'name': 'ldU17', 'p': -1 * sTo[20].real, 'q': -1 * sTo[20].imag}

    system2.loadu.addDevice(dae2, system2.bus, ldU14)
    system2.loadu.addDevice(dae2, system2.bus, ldU17)


    # ==============================================================================================
    system1.deviceList = ['bus', 'load', 'loadu', 'lne', 'tr2w', 'syn4', 'cExc', 'exc', 'tG', 'cTg']
    system2.deviceList = ['bus', 'load', 'loadu', 'lne', 'tr2w', 'syn4', 'exc', 'tG', 'cTg']


    #Set Up devices
    dae1.setUp()
    system1.setUpDevices()   

    #Set Up devices
    dae2.setUp()
    system2.setUpDevices()   

    # Compute admittance matrices
    system1.makeYbus()
    system2.makeYbus()

    #runPF
    powerFlow(system1.Ybus, system1.bus, [system1.syn4], [system1.load, system1.loadu])  
    powerFlow(system2.Ybus, system2.bus, [system2.syn4], [system2.load, system2.loadu])

    #Initialize
    system1.initDevices(dae1)
    system2.initDevices(dae2)


    #Compute matrices
    dae1.reInitG()
    dae1.reInitF()
    dae2.reInitG()
    dae2.reInitF()

    system1.computeF(dae1)
    system1.computeG(dae1, system1.Ybus)
    system2.computeF(dae2)
    system2.computeG(dae2, system2.Ybus)







    # # Comparar 
    # busIdx1 = [system.bus.deviceIdx[i] for i in system1.bus.name]

    # fig, ax = plt.subplots(1)
    # data1 = np.vstack([np.array(busIdx1) + 1 , dae.y[np.array(system.bus.vm)[busIdx1]]]).T
    # data1 = data1[np.argsort(data1[:,0])]
    # ax.plot(data1[:,0], data1[:,1], label = 'Overall system', color = 'tab:blue', linewidth=1.0, marker = 'x', markevery=1, markersize = 10)
    # data2 = np.vstack([np.array(busIdx1) + 1 , dae1.y[system1.bus.vm]]).T
    # data2 = data2[np.argsort(data2[:,0])]
    # ax.plot(data2[:, 0], data2[:, 1], label = 'Area 1', color = 'tab:red', linewidth=1.0, marker = 'o', markevery=1, markersize = 5)
    # ax.grid()
    # ax.set_xlabel('Bus number', fontsize=14)
    # ax.set_ylabel('voltage (pu)', fontsize=14)
    
    # ratio = 0.5
    # xleft, xright = ax.get_xlim()
    # ybottom, ytop = ax.get_ylim()
    # # the abs method is used to make sure that all numbers are positive
    # # because x and y axis of an axes maybe inversed.
    # ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
    # lgd = ax.legend(fontsize=10, loc='center', bbox_to_anchor=(0.0, -0.3, 1.00, .102), mode = 'expand', ncol = 6, borderaxespad=0.5)
    # oFile = 'Area1Comparition'
    # fig.savefig(oFile, format = 'eps', bbox_inches='tight', bbox_extra_artists = [lgd])



    # busIdx1 = [system.bus.deviceIdx[i] for i in system2.bus.name]
    # fig, ax = plt.subplots(1)
    # data1 = np.vstack([np.array(busIdx1) + 1 , dae.y[np.array(system.bus.vm)[busIdx1]]]).T
    # data1 = data1[np.argsort(data1[:,0])]
    # ax.plot(data1[:,0], data1[:,1], label = 'Overall system', color = 'tab:blue', linewidth=1.0, marker = 'x', markevery=1, markersize = 10)
    # data2 = np.vstack([np.array(busIdx1) + 1 , dae2.y[system2.bus.vm]]).T
    # data2 = data2[np.argsort(data2[:,0])]
    # ax.plot(data2[:, 0], data2[:, 1], label = 'Area 2', color = 'tab:red', linewidth=1.0, marker = 'o', markevery=1, markersize = 5)
    # ax.grid()
    # ax.set_xlabel('Bus number', fontsize=14)
    # ax.set_ylabel('voltage (pu)', fontsize=14)
    
    # ratio = 0.5
    # xleft, xright = ax.get_xlim()
    # ybottom, ytop = ax.get_ylim()
    # # the abs method is used to make sure that all numbers are positive
    # # because x and y axis of an axes maybe inversed.
    # ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
    # lgd = ax.legend(fontsize=10, loc='center', bbox_to_anchor=(0.0, -0.3, 1.00, .102), mode = 'expand', ncol = 6, borderaxespad=0.5)
    # oFile = 'Area2Comparition.eps'
    # fig.savefig(oFile, format = 'eps', bbox_extra_artists = [lgd], bbox_inches='tight')
    return system, dae, system1, dae1, system2, dae2




if __name__ == '__main__':
    system, dae, system1, dae1, system2, dae2 = case39()