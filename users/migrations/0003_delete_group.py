# Generated by Django 5.0.2 on 2024-11-20 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_group'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Group',
        ),
    ]
