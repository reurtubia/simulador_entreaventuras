import json
import os

import numpy as np
import pandas as pd

from engine.game.characters import Character
from engine.game.objects import Dice

class Adventure:

    ### Initializer ###
    def __init__(self):
        self.__adventurePath = os.path.join(os.path.dirname(__file__), '..', 'data', 'adventures')
        self.__characterPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'characters')

    ### Métodos de la Clase ###
    # Carga la aventura desde un json
    def loadAdventure(self, name, actor, **kwargs):
        path = os.path.join(self.__adventurePath, name)
        with open(path, 'r', encoding = 'utf8') as fcc_file:
            data = json.load(fcc_file)
            type = data['type']
            actions = dict()
            for step in data['steps']:
                if step['id'] == 'expenditure':
                    actions['cost'] = step
                elif step['id'] in ['challenge' , 'cheat']:
                    if not 'rolls' in actions:
                        actions['rolls'] = list()
                    actions['rolls'].append(step)
                elif step['id'] == 'reward':
                    actions['prize'] = step
            
            if type == 'money':
                cookedAdventure = dict()
                cookedAdventure['name'] = data['name']
                cost = actions['cost']
                rolls = actions['rolls']
                prize = actions['prize']
                replacements = data.get('replacements')
                uniqueBonus = data.get('uniqueBonus')

                # Prepara los resultados
                earningsTable = dict()
                if prize['multiplicator'] == 'day':
                    for key, value in prize['difficultyClass'].items():
                        earningsTable[int(key)] = value*cost['days'] - cost['gold']
                elif prize['multiplicator'] == 'input':
                    for key, value in prize['difficultyClass'].items():
                        earningsTable[int(key)] = value*kwargs.get('apuesta', 0) - cost['gold']
                elif prize['multiplicator'] == 'global':
                    for key, value in prize['difficultyClass'].items():
                        earningsTable[int(key)] = value - cost['gold']
                cookedAdventure['prizes'] = earningsTable
                
                # Prepara las tiradas enfrentadas
                if prize['type']['gauge'] == 'success':
                    cookedAdventure['comparison'] = {
                        'rollsDice': True,
                        'dice': Dice(prize['type']['dice']),
                        'ammount': prize['type']['ammount'],
                        'days': cost['days']
                    }
                elif prize['type']['gauge'] == 'maxValue':
                    cookedAdventure['comparison'] = {
                        'rollsDice': False,
                        'ammount': prize['type']['ammount'],
                        'days': cost['days']
                    }

                # Cada roll es una tirada enfrentada
                bestRolls = list()
                for roll in rolls:
                    skillBehavior = roll['id']
                    cheatTiming = roll.get('time')
                    goodBackgrounds = roll.get('advantage')
                    advantage = False
                    if not goodBackgrounds:
                        pass
                    elif actor.background in goodBackgrounds:
                        advantage = True
                    else:
                        for background in goodBackgrounds:
                            if background in actor.background:
                                advantage = True

                    # Escoges la mejor skill que te ofrezca el roll
                    avgRolls = list()
                    for skill in roll['skillCheck']:
                        avgRoll = dict()
                        avgRoll['actorName'] = actor.name
                        avgRoll['skillName'] = skill
                        avgRoll['behavior'] = skillBehavior
                        avgRoll['timing'] = cheatTiming
                        avgRoll['advantage'] = advantage
                        avgRoll['skill'] = actor.skills(skill)
                        bonuses = roll.get('bonus')
                        avgRoll['bonus'] = list()
                        if bonuses:
                            for bonus in bonuses:
                                if bonus == 'maxHitDie':
                                    avgRoll['bonus'].append(actor.getMaxHitDie())
                                elif False: # Aquí añadir nuevos posibles bonus
                                    pass
                        avgRoll['average'] = avgRoll['skill'].avgRoll(advantage=avgRoll['advantage'],
                                                                    extraBonuses=avgRoll['bonus'])
                        avgRolls.append(avgRoll)
                    df_avgRolls = pd.DataFrame(avgRolls)
                    df_avgRolls.sort_values(by=['average'], ascending=False, inplace=True)
                    bestRoll = df_avgRolls.iloc[[0]].to_dict('records') # El valor mayor
                    bestRolls += bestRoll

                # Añade bonos que se puedan aplicar a solamente una habilidad
                df_bestRolls = pd.DataFrame(bestRolls)
                if uniqueBonus:
                    df_bestRolls = df_bestRolls.sort_values(by=['average'], ascending=False)
                    if uniqueBonus['requires'] == 'gamingSet':
                        if actor.skills('gamingSet').isProficient():
                            bonuses = []
                            for bonus in uniqueBonus['bonus']:
                                if bonus == 'proficiency':
                                    bonuses.append(actor.proficiency)
                            if not df_bestRolls.loc[df_bestRolls.behavior == 'cheat'].empty:
                                df_bestRolls.loc[df_bestRolls.behavior == 'cheat'].iloc[0].bonus += (bonuses)
                            else:
                                df_bestRolls.iloc[-1].bonus += (bonuses)
                    elif False: # Aquí poner futuros bonos
                        pass

                # Divide los rolls según su comportamiento
                df_beforeCheats = df_bestRolls.loc[(df_bestRolls['behavior'] == 'cheat') & (df_bestRolls['timing'] == 'before')]
                df_afterCheats = df_bestRolls.loc[(df_bestRolls['behavior'] == 'cheat') & (df_bestRolls['timing'] == 'after')]
                df_selectedRolls = df_bestRolls.loc[df_bestRolls['behavior'] == 'challenge']

                # Se queda con posibles cambios a hacer después de lanzar los dados
                if not df_afterCheats.empty: # TODO: Priorizar qué dados quedarse. Dados que se lanzan después son más útiles que los que se lanzan antes, pero cuánta debería ser la diferencia estimada a la que son similares
                    df_afterCheats = df_afterCheats.sort_values(by=['average'], ascending=False)
                    df_afterCheats = df_afterCheats.reset_index(drop=True)
                    if len(df_afterCheats) > replacements:
                        df_afterCheats = df_afterCheats.iloc[0:replacements]
                        replacements -= replacements
                    else:
                        replacements -= len(df_afterCheats)

                # Detecta si puede hacer algún cambio antes de lanzar los dados, si es que le quedan opciones
                if not df_beforeCheats.empty and replacements > 0:
                    df_selectedRolls = df_selectedRolls.sort_values(by=['average'], ascending=True)
                    df_selectedRolls = df_selectedRolls.reset_index(drop=True)
                    df_beforeCheats = df_beforeCheats.sort_values(by=['average'], ascending=False)
                    df_beforeCheats = df_beforeCheats.reset_index(drop=True)
                    while df_selectedRolls.iloc[0].average < df_beforeCheats.iloc[0].average and replacements > 0:
                        df_selectedRolls.drop(0, inplace=True)
                        df_selectedRolls = pd.concat([df_selectedRolls, df_beforeCheats.iloc[[0]]])
                        df_beforeCheats.drop(0, inplace=True)
                        replacements -= 1
                        df_selectedRolls = df_selectedRolls.reset_index(drop=True)
                        df_beforeCheats = df_beforeCheats.reset_index(drop=True)
                        if df_beforeCheats.empty:
                            break

                cookedAdventure['rolls'] = df_selectedRolls
                cookedAdventure['jokers'] = df_afterCheats
                return cookedAdventure

    # Carga el personaje desde un json
    def loadCharacter(self, name):
        for filename in os.listdir(self.__characterPath):
            if name == filename:
                path = os.path.join(self.__characterPath, filename)
                character = Character(path)   
                return character
        return None # TODO: raise error

    # Ejecuta una aventura de dinero un número arbitrario de veces
    def executeMoneyAdventure(self, cookedAdventure, cycles):
        #np.random.seed(33)
        df_detail = pd.DataFrame()
        rows_summary = list()
        # Cada ciclo es una aventura
        for i in range(cycles):
            df_rolls = cookedAdventure['rolls']
            df_rolls['cooked'] = [list(x) for x in zip(df_rolls['advantage'], df_rolls['bonus'], df_rolls['skill'])]
            df_rolls['roll'] = np.where(
                True, 
                df_rolls.cooked.map(lambda x: x[2].check(
                        advantage=x[0],
                        extraBonuses=x[1])).values,
                None
            )

            df_jokers = cookedAdventure['jokers']
            df_jokers['cooked'] = [list(x) for x in zip(df_jokers['advantage'], df_jokers['bonus'], df_jokers['skill'])]
            df_jokers['roll'] = np.where(
                True, 
                df_jokers.cooked.map(lambda x: x[2].check(
                        advantage=x[0],
                        extraBonuses=x[1])).values,
                None
            )

            df_adventure = pd.concat([df_rolls, df_jokers])
            df_adventure.sort_values(by=['roll'], ascending=False, inplace=True)
            df_adventure = df_adventure[['actorName', 'skillName', 'bonus', 'advantage', 'roll']]
            
            # Se toman los mejores dados
            size = cookedAdventure['comparison']['ammount']
            df_adventure = df_adventure.iloc[0:size]
            if cookedAdventure['comparison']['rollsDice']:
                df_adventure['difficulty'] = cookedAdventure['comparison']['dice']
                df_adventure['DC'] = np.where(
                    True, 
                    df_adventure.difficulty.map(lambda x: x.roll()),
                    None
                )
                df_adventure.drop(axis=1, columns=['difficulty'], inplace=True)
                df_adventure['success'] = np.where(
                    df_adventure['roll'].values >= df_adventure['DC'].values,
                    True,
                    False
                )
                successes = len(df_adventure.loc[df_adventure['success']])
                money = cookedAdventure['prizes'][successes]

                df_detail = pd.concat([df_detail, df_adventure])
                rows_summary.append({'successes': successes, 'money': money, 'days': cookedAdventure['comparison']['days']})
            else:
                sum = df_adventure['roll'].sum()
                money = 0
                for DC, gold in cookedAdventure['prizes'].items():
                    if sum >= DC and gold > money:
                        money = gold

                df_detail = pd.concat([df_detail, df_adventure])
                rows_summary.append({'roll': sum, 'money': money, 'days': cookedAdventure['comparison']['days']})
        
        df_detail = df_detail.reset_index(drop=True)
        df_summary = pd.DataFrame(rows_summary)
        return df_summary, df_detail