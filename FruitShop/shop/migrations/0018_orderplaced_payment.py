# Generated by Django 4.2.6 on 2023-11-10 06:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_rename_payment_orderplaced_payment_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderplaced',
            name='payment',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='shop.payment'),
        ),
    ]
