# Generated by Django 4.2.10 on 2024-02-22 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='estados',
            old_name='desc',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='tipousuario',
            old_name='desc',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='tipousuario',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
