import numpy as np

class Die:
    """
    Clase que representa un dado.
    - Su único atributo es la cantidad de caras
    - Tiene métodos para realizar lanzamientos activos
    - Tiene métodos para obtener el promedio de algunos lanzamientos
    """

    ### Initializer ###
    def __init__(self, faces):
        self.__faces = faces

    def __str__(self):
        return f'd{self.__faces}'

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
    
    def avgRollElvenAccuracy(self):
        return 0 # TODO: Buscar la fórmula matemática para esto

    # Lógica para decidir el tipo de lanzamiento
    def decideAvgRoll(self, **kwargs):
        advantage = kwargs.get('advantage', False)
        disadvantage = kwargs.get('disadvantage', False)
        elvenAccuracy = kwargs.get('elvenAccuracy', False)
        if not advantage and not disadvantage:
            return self.avgRoll()
        elif advantage and not disadvantage:
            if elvenAccuracy:
                return self.avgRollElvenAccuracy()
            else:
                return self.avgRollAdvantage()
        elif not advantage and disadvantage:
            return self.avgRollDisadvantage()
        else:
            return self.avgRoll()

class Dice:
    """
    Clase que representa un grupo de dados.
    - Tiene una lista con los dados
    - Tiene una lista con los bonos
    - Tiene métodos para realizar lanzamientos activos
    - Tiene métodos para obtener el promedio de algunos lanzamientos
    """

    ### Initializer ###
    def __init__(self, diceString):
        self.__dice = list()
        self.__bonuses = 0
        self.__string = diceString
        strings = diceString.split('+')
        for string in strings:
            # Si tiene la d es un dado
            if 'd' in string:
                ammount, faces = string.split('d')
                for i in range(int(ammount)):
                    self.__dice.append(Die(int(faces)))
            else:
                self.__bonuses += int(string)

    def __str__(self):
        return self.__string

    ### Class Methods ###
    # Lanza todos los dados
    def roll(self, **kwargs):
        roll = self.__bonuses
        for die in self.__dice:
            roll += die.decideRoll(**kwargs)
        return roll

    # Calcula el promedio de los dados
    def avgRoll(self, **kwargs):
        roll = self.__bonuses
        for die in self.__dice:
            roll += die.decideAvgRoll(**kwargs)
        return roll