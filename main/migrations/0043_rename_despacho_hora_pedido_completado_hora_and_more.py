# Generated by Django 4.2.10 on 2024-07-14 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_remove_pedido_completado_hora_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pedido',
            old_name='despacho_hora',
            new_name='completado_hora',
        ),
        migrations.RenameField(
            model_name='pedido',
            old_name='despachador_reparto',
            new_name='completado_por',
        ),
    ]
