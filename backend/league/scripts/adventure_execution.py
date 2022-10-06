from django.db import IntegrityError

from engine.game import environment
from league.models import *
from game.models import *


def run():
    player = 'Zamanama'

    adventureManager= environment.Adventure()
    character = adventureManager.loadCharacter('fvtt-Actor-zgrak.json')
    adventure = adventureManager.loadAdventure('street_fighting.json', character)
    data = adventureManager.executeMoneyAdventure(adventure, 1000)

    characterName = character.name
    objCharacter, _ = Character.objects.get_or_create(
        name=characterName,
        player=player
    )

    level = 0
    subclasses = dict()
    classes = dict()
    for subclass, info in character.subclasses.items():
        level += info['level']
        subclasses[subclass] = info['level']
        classes[subclass] = info['class']
        objClass, _ = DnDClass.objects.get_or_create(name=info['class'])
        objSubclass, _ = DnDSubclass.objects.get_or_create(
            name=subclass,
            dndclass=objClass
        )

    objProgression, _ = CharacterProgression.objects.get_or_create(
        character=objCharacter,
        level=level
    )

    for subclass in subclasses:
        dndclass = classes[subclass]
        objClass = DnDClass.objects.get(name=dndclass)
        objSubclass = DnDSubclass.objects.get(
            name=subclass,
            dndclass=objClass
        )
        objMulticlass, _ = Multiclass.objects.get_or_create(
            characterprogression=objProgression,
            dndsubclass=objSubclass,
            level=subclasses[subclass]
        )

    objAdventure, _ = Adventure.objects.get_or_create(name=adventure['name'])

    df_detail = data[1]
    progress = 0
    for skill, DC, roll, success in zip(df_detail.skillName.values,
                            df_detail.DC.values,
                            df_detail.roll.values,
                            df_detail.success.values):
        progress += 1
        if progress%10 == 0:
            print(progress)
        objSkill, _ = Skill.objects.get_or_create(name=skill)
        objLog = AdventureLog(
            adventure=objAdventure,
            characterprogression=objProgression,
            skill=objSkill,
            difficultyclass=DC,
            roll=roll,
            success=success
        )
        objLog.save()