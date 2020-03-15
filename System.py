from methods import makeYbus
class System():
    def __init__(self, baseMVA = 100, fn = 60):
        self.baseMVA = baseMVA
        self.fn = 60 
        self.deviceList = []

        #Init devices
        self.lne = None
        self.tr2w = None
        self.bus = None

    #---------------------------------------------------------
    #setUp devices.
    def setUpDevices(self):
        for devi in self.deviceList:
            self.__dict__[devi].setUp()


    #---------------------------------------------------------
    def initDevices(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['init']:
                self.__dict__[devi].initialize(DAE)

    
    #Compute Admitance matrix
    def makeYbus(self):

        #Check if there are lines and transformers in the system
        if 'lne'!= None:
            lne = self.lne
        else:
            lne = None

        if 'tr2w' != None:
            tr2w = self.tr2w
        else:
            tr2w = None
        
        #buses!
        bus = self.bus
        #Compute Ybus!
        self.Ybus, self.A, self.YfLne, self.YtLne = makeYbus(bus, Lne = lne, Tr2w= tr2w)
    #---------------------------------------------------------
    #Call state functions
    #---------------------------------------------------------
    def fcall(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['fcall']:
                self.__dict__[devi].fcall(DAE)

    def fxcall(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['fxcall']:
                self.__dict__[devi].fxcall(DAE)

    def fycall(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['fycall']:
                self.__dict__[devi].fycall(DAE)

    def fucall(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['fucall']:
                self.__dict__[devi].fucall(DAE)

    #---------------------------------------------------------
    #Call algebraic functions
    #---------------------------------------------------------
    def gcall(self, DAE, Ybus):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['gcall']:
                if self.__dict__[devi].properties['type'] == 'bus': #Device is the busBar?
                    self.__dict__[devi].gcall(DAE, Ybus)
                else:
                    self.__dict__[devi].gcall(DAE)

    def gxcall(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['gxcall']:
                self.__dict__[devi].gxcall(DAE)

    def gycall(self, DAE, Ybus):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['gycall']:
                if self.__dict__[devi].properties['type'] == 'bus': #Device is the busBar?
                    self.__dict__[devi].gycall(DAE, Ybus)
                else:
                    self.__dict__[devi].gycall(DAE)

    def gucall(self, DAE):
        for devi in self.deviceList:
            if self.__dict__[devi].properties['gucall']:
                self.__dict__[devi].gucall(DAE)


    def computeF(self, DAE):
        self.fcall(DAE)
        self.fxcall(DAE)
        self.fycall(DAE)
        self.fucall(DAE)

    def computeG(self, DAE, Ybus):        
        self.gcall(DAE, Ybus)
        self.gxcall(DAE)
        self.gycall(DAE, Ybus)
        self.gucall(DAE)