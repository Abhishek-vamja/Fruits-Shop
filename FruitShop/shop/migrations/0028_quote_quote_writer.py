# Generated by Django 4.2.6 on 2023-12-22 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0027_quote'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='quote_writer',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
