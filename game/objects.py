import numpy as np

class Die:
    """
    Clase que representa un dado.
    - Su único atributo es la cantidad de caras.
    - Tiene métodos para realizar lanzamientos activos
    - Tiene métodos para obtener el promedio de algunos lanzamientos
    """

    ### Initializer ###
    def __init__(self, faces):
        self.__faces = faces

    ### Getters & Setters ###
    def __get_faces(self): return self.__faces
    faces = property(__get_faces)

    ### Class Methods ###
    # Lanza un dado aleatorio dentro del rango permitido
    def roll(self):
        min = 1
        max = self.__faces + 1
        return np.random.randint(min, max)

    # Lanza dos dados aleatorios y se queda con el menor
    def rollDisadvantage(self):
        return min(self.roll(), self.roll())

    # Lanza dos dados aleatorios y se queda con el mejor
    def rollAdvantage(self):
        return max(self.roll(), self.roll())

    # Lanza tres dados aleatorios y se queda con el mejor
    def rollElvenAccuracy(self):
        return max(self.roll(), self.roll(), self.roll())

    # Lógica para decidir el tipo de lanzamiento
    def decideRoll(self, **kwargs):
        advantage = kwargs.get('advantage', False)
        disadvantage = kwargs.get('disadvantage', False)
        elvenAccuracy = kwargs.get('elvenAccuracy', False)
        if not advantage and not disadvantage:
            return self.roll()
        elif advantage and not disadvantage:
            if elvenAccuracy:
                return self.rollElvenAccuracy()
            else:
                return self.rollAdvantage()
        elif not advantage and disadvantage:
            return self.rollDisadvantage()
        else:
            return self.roll()

    # Lanzamiento promedio de un dado
    def avgRoll(self):
        return (0.5 + self.__faces/2)

    # Lanzamiento promedio del peor de dos dados
    def avgRollDisadvantage(self):
        return (self.__faces + 1 - (4*self.__faces*self.__faces + 3*self.__faces - 1.)/(6*self.__faces))

    # Lanzamiento promedio del mejor de dos dados
    def avgRollAdvantage(self):
        return (4*self.__faces*self.__faces + 3*self.__faces - 1.)/(6*self.__faces)
