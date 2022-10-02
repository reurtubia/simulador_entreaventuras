import json
import os

import pandas as pd

from characters import Character

class Adventure:

    ### Initializer ###
    def __init__(self):
        self.__dataPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'adventures')

    ### Métodos de la Clase ###
    # Carga el personaje desde un json
    def loadAdventure(self, name, actor, **kwargs):
        path = os.path.join(self.__dataPath, name)
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
                cookedAdventure['comparison'] = prize['gauge']

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
                        df_afterCheats = df_afterCheats.loc[0:replacements]
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
                
chr_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'characters', 'fvtt-Actor-edward-genkov.json')
chr = Character(chr_path)

adv = Adventure()
cuy = adv.loadAdventure("illegal_gambling.json", chr, apuesta=100)
import IPython as ipy
ipy.embed()