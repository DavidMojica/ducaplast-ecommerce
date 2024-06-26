# Generated by Django 4.2.10 on 2024-04-04 19:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_tipoproducto_producto_tipo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='repartido_por',
        ),
        migrations.CreateModel(
            name='HandlerReparto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.pedido')),
                ('repartidor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
