# Generated by Django 4.2.10 on 2024-06-25 17:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_pedido_check_bodega_pedido_urgente'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='checkeado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkeado_por', to=settings.AUTH_USER_MODEL),
        ),
    ]
