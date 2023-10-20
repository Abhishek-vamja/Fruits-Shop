# Generated by Django 4.2.6 on 2023-10-19 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_orderplaced'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='deal_of',
            field=models.CharField(choices=[('Day', 'Day'), ('Month', 'Month'), ('Year', 'Year')], default='Month', max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_time_limited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='percent_off',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
