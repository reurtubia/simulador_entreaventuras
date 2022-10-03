from django.db import models

from game.models import Auditable, CharacterProgression, Skill

# Nombres de las aventuras
class Adventure(Auditable):
    name = models.CharField(max_length=30, null=False, blank=False, unique=True)

# Historial de las aventuras
class AdventureLog(Auditable):
    adventure = models.ForeignKey(Adventure, blank=False, null=False, on_delete=models.CASCADE)
    characterprogression = models.ForeignKey(CharacterProgression, blank=False, null=False, on_delete=models.CASCADE)
    skillname = models.ForeignKey(Skill, blank=False, null=False, on_delete=models.CASCADE)
    difficultyclass = models.IntegerField(null=True, blank=True)
    roll = models.IntegerField(null=False, blank=False)