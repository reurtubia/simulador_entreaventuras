from django.db import models

class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        managed = True

# Nombres de los personajes
class Character(Auditable):
    name = models.CharField(max_length=30, null=False, blank=False)
    player = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'player')

    def __str__(self):
        return f'{self.name} @ {self.player}'

# Nombres de las clases
class DnDClass(Auditable):
    name = models.CharField(max_length=10, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name

# Nombres de las subclases
class DnDSubclass(Auditable):
    name = models.CharField(max_length=30, null=False, blank=False)
    dndclass = models.ForeignKey(DnDClass, blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'dndclass')

    def __str__(self):
        return self.name

# Historial del progreso del personaje a través de los niveles
class CharacterProgression(Auditable):
    character = models.ForeignKey(Character, blank=False, null=False, on_delete=models.CASCADE)
    level = models.IntegerField(null=False, blank=False)

    class Meta:
        unique_together = ('character', 'level')

    def __str__(self):
        return f'{self.character} @ {self.level}'

# Conecta las subclases con los personajes
class Multiclass(Auditable):
    characterprogression = models.ForeignKey(CharacterProgression, blank=False, null=False, on_delete=models.CASCADE)
    dndsubclass = models.ForeignKey(DnDSubclass, blank=False, null=False, on_delete=models.CASCADE)
    level = models.IntegerField(null=False, blank=False)

    class Meta:
        unique_together = ('characterprogression', 'level')

# Nombres de las habilidades
class Skill(Auditable):
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name