# Generated by Django 4.2.10 on 2024-06-04 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_pedido_credito_hora_pedido_credito_por'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoCantidad',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=25)),
            ],
        ),
    ]
