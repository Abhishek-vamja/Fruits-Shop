# Generated by Django 4.2.6 on 2023-12-22 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0029_alter_orderplaced_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderplaced',
            name='delivered_date',
            field=models.DateField(default='', null=True),
        ),
    ]
