# Generated by Django 4.2.10 on 2024-02-29 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_usuarios_documento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producto',
            old_name='nombre',
            new_name='referencia_fabrica',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='codigo',
        ),
    ]