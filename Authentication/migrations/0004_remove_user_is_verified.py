# Generated by Django 5.0.6 on 2024-07-06 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0003_user_is_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_verified',
        ),
    ]