# Generated by Django 4.2.10 on 2024-06-26 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_alter_clientes_direccion_alter_pedido_direccion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='consecutivo',
            field=models.CharField(max_length=500, null=True, unique=True),
        ),
    ]
