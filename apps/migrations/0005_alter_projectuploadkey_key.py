# Generated by Django 4.1.7 on 2023-03-07 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_coveragesummary_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectuploadkey',
            name='key',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
