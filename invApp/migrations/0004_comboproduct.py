# Generated by Django 5.0.4 on 2024-10-19 05:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invApp', '0003_alter_product_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComboProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combo_name', models.CharField(max_length=255)),
                ('combo_sku', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product1_combo', to='invApp.product')),
                ('product2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product2_combo', to='invApp.product')),
            ],
        ),
    ]
