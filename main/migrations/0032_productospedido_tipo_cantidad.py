# Generated by Django 4.2.10 on 2024-06-04 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_tipocantidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='productospedido',
            name='tipo_cantidad',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.tipocantidad'),
        ),
    ]
