# Generated by Django 3.2.9 on 2021-11-22 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainfeature', '0004_alter_timetable_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
