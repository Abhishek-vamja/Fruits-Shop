# Generated by Django 4.2.6 on 2023-11-06 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='otp_attempt',
            field=models.CharField(default=3, max_length=255),
        ),
    ]
