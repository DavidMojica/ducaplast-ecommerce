# Generated by Django 4.2.10 on 2024-07-15 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_pedido_check_factura_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='check_factura',
            field=models.BooleanField(default=False),
        ),
    ]
