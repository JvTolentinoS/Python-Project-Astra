GRAVITATIONAL_VALUE = 6.67430e-11                                               # m^3 kg^-1 s^-2

class object_:
    def __init__(self, designation, mass, radius):
        self.designation = designation                                          # Nomeação
        self.mass = mass                                                        # kg
        self.radius = radius                                                    # m

    def setDesignation(self, designation): self.designation = designation
    def setMass(self, mass): self.mass = mass
    def setRadius(self, radius): self.radius = radius
   
    def getId(self): return self.id
    def getDesignation(self): return self.designation
    def getMass(self): return self.mass
    def getRadius(self): return self.radius

class system_:

    system_list = []
    def setObject(self, object_): self.system_list.append(object_)
    def getObjects(self): return self.system_list
