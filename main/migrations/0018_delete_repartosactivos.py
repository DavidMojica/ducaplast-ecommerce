# Generated by Django 4.2.10 on 2024-03-15 21:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_remove_pedido_repartido_hora'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RepartosActivos',
        ),
    ]