# Generated by Django 4.2.10 on 2024-04-05 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_rolreparto_handlerreparto_rol'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='consecutivo',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
