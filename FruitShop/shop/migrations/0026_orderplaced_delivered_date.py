# Generated by Django 4.2.6 on 2023-12-22 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0025_remove_orderplaced_product_orderplaced_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderplaced',
            name='delivered_date',
            field=models.DateField(null=True),
        ),
    ]
