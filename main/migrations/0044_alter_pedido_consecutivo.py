# Generated by Django 4.2.10 on 2024-07-14 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_rename_despacho_hora_pedido_completado_hora_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='consecutivo',
            field=models.CharField(max_length=500, null=True),
        ),
    ]