# Generated by Django 4.2.10 on 2024-03-16 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_delete_repartosactivos'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='notaDespachador',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
