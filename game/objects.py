import math
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

class Skill:
    """
    Clase que representa una habilidad.
    - Atributos:
        actor: el personaje al que pertenece la habilidad
        name: el nombre de la habilidad
            ['acr', 'ani', 'arc', 'ath', 'dec', 'his', 'ins', 'itm', 'inv', 'med', 'nat', 'prc', 'prf',
            'per', 'rel', 'slt', 'ste', 'sur', 'str', 'dex', 'con', 'int', 'wis', 'cha', 'art', 'mus', 'gam']
        abilityScore: la estadística que usa la habilidad de forma abreviada
            ['str', 'dex', 'con', 'int', 'wis', 'cha']
        bonuses: lista de bonus que se aplican a la habilidad
        proficient: competencia del personaje
            ['not', 'jot', 'pro', 'exp']
    - Tiene lógica para aplicar beneficios de subclases
    - Tiene métodos para realizar un check activo
    - Tiene métodos para realizar un check pasivo
    """

    ### Initializer ###
    def __init__(self, actor, name, abbr, **kwargs):
        self.__actor = actor
        self.__name = name
        self.__abilityScore = abbr
        self.__bonuses = list()
        self.__bonuses += kwargs.get('bonuses', [])
        self.__proficient = kwargs.get('proficient', 'not')

    ### Getters & Setters ###
    def __get_name(self): return self.__name
    name = property(__get_name)

    ### Class Methods ###
    # Revisa si es competente
    def isProficient(self):
        if self.__proficient in ['pro', 'exp']:
            return True
        return False

    # Check activo
    def check(self, **kwargs):
        """
        Realiza el check de esta habilidad.

        kwargs:
            advantage (bool): Es True si tiene alguna fuente de ventaja, False en otro caso
            disadvantage (bool): Es True si tiene alguna fuente de desventaja, False en otro caso
            elvenAccuracy (): Es True si tiene el rasgo de elvenAccuracy

        Returns:
            int: Número logrado en el check
        """

        # TODO: Agregar ventajas de Rune Knight

        # Tirada de d20
        roll = 0
        roll = Die(20).decideRoll(**kwargs)

        # Bonificaciones de subclase
        if 'Inquisitive' in self.__actor.subclasses and self.__name == 'insight':
            if self.__actor.subclasses['Inquisitive'] >= 3:
                if roll <= 8: roll = 8
        if 'College of Eloquence' in self.__actor.subclasses and (self.__name == 'deception' or self.__name == 'persuasion'):
            if self.__actor.subclasses['College of Eloquence'] >= 3:
                if roll <= 10: roll = 10
        if 'Fey Wanderer' in self.__actor.subclasses and self.__abilityScore == 'cha':
            if self.__actor.subclasses['Fey Wanderer'] >= 3:
                wisMod = self.__actor.getMod('wis')
                if wisMod < 1:
                    roll += 1
                else:
                    roll += wisMod
        # TODO: investigar el resto de subclass features que pueden afectar

        # Adición de bonus
        roll += self.__actor.getMod(self.__abilityScore)
        extraBonuses = kwargs.get('extraBonuses', [])
        if type(extraBonuses) != list:
            extraBonuses = [extraBonuses]
        for bonus in (self.__bonuses + extraBonuses):
            if type(bonus) == Die:
                roll += bonus.roll()
            elif type(bonus) == int:
                roll += bonus

        # Adición de competencia
        if self.__proficient == 'pro':
            roll += self.__actor.proficiency
        elif self.__proficient == 'exp':
            roll += 2*self.__actor.proficiency
        elif self.__proficient == 'jot':
            roll += math.floor(self.__actor.proficiency/2)
        return roll

    # Check pasivo
    def avgRoll(self, **kwargs):

        # TODO: Agregar ventajas de Rune Knight

        """
        Calcula el check promedio de la habilidad.

        kwargs:
            advantage (bool): Es True si tiene alguna fuente de ventaja, False en otro caso
            disadvantage (bool): Es True si tiene alguna fuente de desventaja, False en otro caso
            elvenAccuracy (): Es True si tiene el rasgo de elvenAccuracy

        Returns:
            float: Número del check promedio
        """

        # Tirada de d20
        roll = Die(20).decideAvgRoll()

        # TODO: Agregar modificadores debido a subclase (eloquence, inquisitive, etc)

        # Adición de bonus
        roll += self.__actor.getMod(self.__abilityScore)
        extraBonuses = kwargs.get('extraBonuses', [])
        if type(extraBonuses) != list:
            extraBonuses = [extraBonuses]
        for bonus in (self.__bonuses + extraBonuses):
            if type(bonus) == Die:
                roll += bonus.avgRoll()
            elif type(bonus) == int:
                roll += bonus

        # Adición de competencia
        if self.__proficient == 'pro':
            roll += self.__actor.proficiency
        elif self.__proficient == 'exp':
            roll += 2*self.__actor.proficiency
        elif self.__proficient == 'jot':
            roll += math.floor(self.__actor.proficiency/2)
        return roll