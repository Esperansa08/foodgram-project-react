# Generated by Django 3.2 on 2023-04-24 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribe',
            options={'ordering': ['-id'], 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
