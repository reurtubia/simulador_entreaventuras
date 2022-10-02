import json
import math

from objects import Die

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

    def __str__(self):
        return f'{self.__name} @ {self.__actor.name.split()[0]}'

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
            elvenAccuracy (bool): Es True si tiene el rasgo de elvenAccuracy
            extraBonuses (list): Lista de bonos, pueden ser enteros o dados

        Returns:
            int: Número logrado en el check
        """

        # TODO: Agregar ventajas de Rune Knight|

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
            elvenAccuracy (bool): Es True si tiene el rasgo de elvenAccuracy
            extraBonuses (list): Lista de bonos, pueden ser enteros o dados

        Returns:
            float: Número del check promedio
        """

        # Tirada de d20
        roll = Die(20).decideAvgRoll(**kwargs)

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

class Character:
    """
    Clase que representa un personaje.
    - Atributos:
        name: nombre del personaje
        background: trasfondo del personaje
        level: nivel del personaje
        subclasses: diccionario con los nombres y niveles de sus subclases
        hitDice: lista con los dados de golpe
        proficiency: modificador de competencia
        abilityScores: diccionario con las puntuaciones de habilidad
        skills: diccionario con las habilidades y su nivel de competencia
    """

    ### Initializer ###
    def __init__(self, path):
        # Global
        self.__classes = list()
        self.__classes.append('Artificer')
        self.__classes.append('Barbarian')
        self.__classes.append('Bard')
        self.__classes.append('Cleric')
        self.__classes.append('Druid')
        self.__classes.append('Fighter')
        self.__classes.append('Monk')
        self.__classes.append('Paladin')
        self.__classes.append('Ranger')
        self.__classes.append('Rogue')
        self.__classes.append('Sorcerer')
        self.__classes.append('Warlock')
        self.__classes.append('Wizard')
        self.__skillDefinition = dict()
        self.__skillDefinition['acr'] = {'Attribute': 'dex', 'Name': 'acrobatics'}
        self.__skillDefinition['ani'] = {'Attribute': 'wis', 'Name': 'animalHandling'}
        self.__skillDefinition['arc'] = {'Attribute': 'int', 'Name': 'arcana'}
        self.__skillDefinition['ath'] = {'Attribute': 'str', 'Name': 'athletics'}
        self.__skillDefinition['dec'] = {'Attribute': 'cha', 'Name': 'deception'}
        self.__skillDefinition['his'] = {'Attribute': 'int', 'Name': 'history'}
        self.__skillDefinition['ins'] = {'Attribute': 'wis', 'Name': 'insight'}
        self.__skillDefinition['itm'] = {'Attribute': 'cha', 'Name': 'intimidation'}
        self.__skillDefinition['inv'] = {'Attribute': 'int', 'Name': 'investigation'}
        self.__skillDefinition['med'] = {'Attribute': 'wis', 'Name': 'medicine'}
        self.__skillDefinition['nat'] = {'Attribute': 'int', 'Name': 'nature'}
        self.__skillDefinition['prc'] = {'Attribute': 'wis', 'Name': 'perception'}
        self.__skillDefinition['prf'] = {'Attribute': 'cha', 'Name': 'performance'}
        self.__skillDefinition['per'] = {'Attribute': 'cha', 'Name': 'persuasion'}
        self.__skillDefinition['rel'] = {'Attribute': 'int', 'Name': 'religion'}
        self.__skillDefinition['slt'] = {'Attribute': 'dex', 'Name': 'sleightOfHand'}
        self.__skillDefinition['ste'] = {'Attribute': 'dex', 'Name': 'stealth'}
        self.__skillDefinition['sur'] = {'Attribute': 'wis', 'Name': 'survival'}
        self.__skillDefinition['str'] = {'Attribute': 'str', 'Name': 'strength'}
        self.__skillDefinition['dex'] = {'Attribute': 'dex', 'Name': 'dexterity'}
        self.__skillDefinition['con'] = {'Attribute': 'con', 'Name': 'constitution'}
        self.__skillDefinition['int'] = {'Attribute': 'int', 'Name': 'intelligence'}
        self.__skillDefinition['wis'] = {'Attribute': 'wis', 'Name': 'wisdom'}
        self.__skillDefinition['cha'] = {'Attribute': 'cha', 'Name': 'charisma'}
        self.__skillDefinition['art'] = {'Attribute': 'int', 'Name': 'artisanTool'}
        self.__skillDefinition['mus'] = {'Attribute': 'cha', 'Name': 'musicalInstrument'}
        self.__skillDefinition['gam'] = {'Attribute': 'wis', 'Name': 'gamingSet'}
        self.__tools = list()
        self.__tools.append('art')
        self.__tools.append('alchemist')
        self.__tools.append('brewer')
        self.__tools.append('calligrapher')
        self.__tools.append('carpenter')
        self.__tools.append('cartographer')
        self.__tools.append('cobbler')
        self.__tools.append('cook')
        self.__tools.append('glassblower')
        self.__tools.append('jeweler')
        self.__tools.append('leatherworker')
        self.__tools.append('mason')
        self.__tools.append('painter')
        self.__tools.append('potter')
        self.__tools.append('smith')
        self.__tools.append('tinker')
        self.__tools.append('weaver')
        self.__tools.append('woodcarver')
        self.__tools.append('navg')
        self.__tools.append('thief')
        self.__kits = list()
        self.__kits.append('disg')
        self.__kits.append('forg')
        self.__kits.append('herb')
        self.__kits.append('pois')
        self.__musicalInstruments = list()
        self.__musicalInstruments.append('music')
        self.__musicalInstruments.append('bagpipes')
        self.__musicalInstruments.append('drum')
        self.__musicalInstruments.append('dulcimer')
        self.__musicalInstruments.append('flute')
        self.__musicalInstruments.append('horn')
        self.__musicalInstruments.append('lute')
        self.__musicalInstruments.append('lyre')
        self.__musicalInstruments.append('panflute')
        self.__musicalInstruments.append('shawm')
        self.__musicalInstruments.append('viol')
        self.__gamingSets = list()
        self.__gamingSets.append('game')
        self.__gamingSets.append('chess')
        self.__gamingSets.append('dice')
        self.__gamingSets.append('card')
        # Local
        self.__name = None
        self.__background = None
        self.__level = 0
        self.__subclasses = dict()
        self.__hitDice = list()
        self.__proficiency = 1
        self.__abilityScores = dict()
        self.__skills = dict()
        self.loadCharacter(path)

    def __str__(self):
        return f'{self.__name} @ Level {self.__level}'

    ### Getters & Setters ###
    # Atributos
    def __get_name(self): return self.__name
    name = property(__get_name)
    def __get_subclasses(self): return self.__subclasses
    subclasses = property(__get_subclasses)
    def __get_proficiency(self): return self.__proficiency
    proficiency = property(__get_proficiency)
    def __get_background(self): return self.__background
    background = property(__get_background)
    def __get_abilityScores(self): return self.__abilityScores
    abilityScores = property(__get_abilityScores)
    # Habilidades
    def __get_acrobatics(self): return self.__skills['acr']
    acrobatics = property(__get_acrobatics)
    def __get_animalHandling(self): return self.__skills['ani']
    animalHandling = property(__get_animalHandling)
    def __get_arcana(self): return self.__skills['arc']
    arcana = property(__get_arcana)
    def __get_athletics(self): return self.__skills['ath']
    athletics = property(__get_athletics)
    def __get_deception(self): return self.__skills['dec']
    deception = property(__get_deception)
    def __get_history(self): return self.__skills['his']
    history = property(__get_history)
    def __get_insight(self): return self.__skills['ins']
    insight = property(__get_insight)
    def __get_intimidation(self): return self.__skills['itm']
    intimidation = property(__get_intimidation)
    def __get_investigation(self): return self.__skills['inv']
    investigation = property(__get_investigation)
    def __get_medicine(self): return self.__skills['med']
    medicine = property(__get_medicine)
    def __get_nature(self): return self.__skills['nat']
    nature = property(__get_nature)
    def __get_perception(self): return self.__skills['prc']
    perception = property(__get_perception)
    def __get_performance(self): return self.__skills['prf']
    performance = property(__get_performance)
    def __get_persuasion(self): return self.__skills['per']
    persuasion = property(__get_persuasion)
    def __get_religion(self): return self.__skills['rel']
    religion = property(__get_religion)
    def __get_sleightOfHand(self): return self.__skills['slt']
    sleightOfHand = property(__get_sleightOfHand)
    def __get_stealth(self): return self.__skills['ste']
    stealth = property(__get_stealth)
    def __get_survival(self): return self.__skills['sur']
    survival = property(__get_survival)
    # Checks
    def __get_strength(self): return self.__skills['str']
    strength = property(__get_strength)
    def __get_dexterity(self): return self.__skills['dex']
    dexterity = property(__get_dexterity)
    def __get_constitution(self): return self.__skills['con']
    constitution = property(__get_constitution)
    def __get_intelligence(self): return self.__skills['int']
    intelligence = property(__get_intelligence)
    def __get_wisdom(self): return self.__skills['wis']
    wisdom = property(__get_wisdom)
    def __get_charisma(self): return self.__skills['cha']
    charisma = property(__get_charisma)
    # Otros
    def __get_tool(self): return self.__skills['art']
    tool = property(__get_tool)
    def __get_instrument(self): return self.__skills['mus']
    instrument = property(__get_instrument)
    def __get_gamingSet(self): return self.__skills['gam']
    gamingSet = property(__get_gamingSet)
    def __get_weaponAttack(self): # TODO: Funcionalidad de armas
        if self.__skills['acr'].avgRoll() > self.__skills['ath'].avgRoll():
            return self.__skills['acr']
        else:
            return self.__skills['ath']
    weaponAttack = property(__get_weaponAttack)

    def skills(self, skill):
        checks = dict()
        checks['acrobatics'] = self.acrobatics
        checks['animalHandling'] = self.animalHandling
        checks['arcana'] = self.arcana
        checks['athletics'] = self.athletics
        checks['deception'] = self.deception
        checks['history'] = self.history
        checks['insight'] = self.insight
        checks['intimidation'] = self.intimidation
        checks['investigation'] = self.investigation
        checks['medicine'] = self.medicine
        checks['nature'] = self.nature
        checks['perception'] = self.perception
        checks['performance'] = self.performance
        checks['persuasion'] = self.persuasion
        checks['religion'] = self.religion
        checks['sleightOfHand'] = self.sleightOfHand
        checks['stealth'] = self.stealth
        checks['survival'] = self.survival
        checks['strength'] = self.strength
        checks['dexterity'] = self.dexterity
        checks['constitution'] = self.constitution
        checks['intelligence'] = self.intelligence
        checks['wisdom'] = self.wisdom
        checks['charisma'] = self.charisma
        checks['tool'] = self.tool
        checks['instrument'] = self.instrument
        checks['gamingSet'] = self.gamingSet
        checks['weaponAttack'] = self.weaponAttack
        return checks[skill]

    ### Métodos de la Clase ###
    # Carga el personaje desde un json
    def loadCharacter(self, path):
        with open(path, 'r', encoding = 'utf8') as fcc_file:
            data = json.load(fcc_file)
            # Nombre
            self.__name = data['name']
            # Background
            self.__background = data['data']['details']['background']
            self.__background = self.__background.replace(' ', '')
            self.__background = self.__background[0].lower() + self.__background[1:]
            # Ability Scores
            self.__abilityScores['str'] = data['data']['abilities']['str']['value']
            self.__abilityScores['dex'] = data['data']['abilities']['dex']['value']
            self.__abilityScores['con'] = data['data']['abilities']['con']['value']
            self.__abilityScores['int'] = data['data']['abilities']['int']['value']
            self.__abilityScores['wis'] = data['data']['abilities']['wis']['value']
            self.__abilityScores['cha'] = data['data']['abilities']['cha']['value']
            # Level
            self.__level = 0
            for item in data['items']:
                if type(item) == dict:
                    if 'name' in item:
                        if item['name'] in self.__classes:
                            classLevel = item['data']['levels']
                            subclass = item['data']['subclass']
                            self.__level += classLevel
                            self.__subclasses[subclass] = classLevel
                            dado = item['data']['hitDice']
                            dado = Die(int(dado[1:]))
                            for i in range(0, classLevel):
                                self.__hitDice.append(dado)
                        elif item['name'] == 'Gauntlets of Ogre Power': 
                            self.__abilityScores['str'] = max(self.__abilityScores['str'], 19)
                        elif item['name'] == 'Headband of Intellect':
                            self.__abilityScores['int'] = max(self.__abilityScores['int'], 19)
                        elif item['name'] == 'Amulet of Health':
                            self.__abilityScores['con'] = max(self.__abilityScores['con'], 19)
            self.__proficiency = math.ceil(1 + self.__level/4)
            # Skills
            profDict = dict()
            profDict[0] = 'not'
            profDict[0.5] = 'jot'
            profDict[1] = 'pro'
            profDict[2] = 'exp'
            skills = dict()
            skills['acr'] = profDict[data['data']['skills']['acr']['value']]
            skills['ani'] = profDict[data['data']['skills']['ani']['value']]
            skills['arc'] = profDict[data['data']['skills']['arc']['value']]
            skills['ath'] = profDict[data['data']['skills']['ath']['value']]
            skills['dec'] = profDict[data['data']['skills']['dec']['value']]
            skills['his'] = profDict[data['data']['skills']['his']['value']]
            skills['ins'] = profDict[data['data']['skills']['ins']['value']]
            skills['itm'] = profDict[data['data']['skills']['itm']['value']]
            skills['inv'] = profDict[data['data']['skills']['inv']['value']]
            skills['med'] = profDict[data['data']['skills']['med']['value']]
            skills['nat'] = profDict[data['data']['skills']['nat']['value']]
            skills['prc'] = profDict[data['data']['skills']['prc']['value']]
            skills['prf'] = profDict[data['data']['skills']['prf']['value']]
            skills['per'] = profDict[data['data']['skills']['per']['value']]
            skills['rel'] = profDict[data['data']['skills']['rel']['value']]
            skills['slt'] = profDict[data['data']['skills']['slt']['value']]
            skills['ste'] = profDict[data['data']['skills']['ste']['value']]
            skills['sur'] = profDict[data['data']['skills']['sur']['value']]
            skills['str'] = 'not'
            skills['dex'] = 'not'
            skills['con'] = 'not'
            skills['int'] = 'not'
            skills['wis'] = 'not'
            skills['cha'] = 'not'
            skills['art'] = 'not'
            skills['mus'] = 'not'
            skills['gam'] = 'not'
            # Tools
            tools = data['data']['traits']['toolProf']['value']
            for tool in tools:
                if tool in self.__tools:
                    skills['art'] = 'pro'
                elif tool in self.__musicalInstruments:
                    skills['mus'] = 'pro'
                elif tool in self.__gamingSets:
                    skills['gam'] = 'pro'
            # Ingresa los datos
            for skill in skills:
                attribute = self.__skillDefinition[skill]['Attribute']
                name = self.__skillDefinition[skill]['Name']
                self.__skills[skill] = Skill(self, name, attribute, proficient = skills[skill])

    # Obtiene el modificador a partir de la puntuación de habilidad
    def getMod(self, abbr):
        score = self.__abilityScores[abbr]
        modifier = math.floor((score - 10)/2)
        return modifier

    # Obtiene el dado de golpe más grande
    def getMaxHitDie(self):
        faces = 0
        for die in self.__hitDice:
            if die.faces >= faces:
                faces = die.faces
        return Die(faces)

