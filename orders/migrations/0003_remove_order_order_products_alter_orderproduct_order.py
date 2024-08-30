# Generated by Django 5.0.7 on 2024-08-12 16:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_order_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_products',
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='orders.order'),
        ),
    ]
