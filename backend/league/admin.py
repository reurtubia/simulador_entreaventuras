from django.contrib import admin
from django.apps import apps

tables_db = apps.all_models['league']

# Mostrar todas las tablas del game en el panel de administración.
for _, table in tables_db.items():
    admin.site.register(table)