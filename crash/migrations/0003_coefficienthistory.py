# Generated by Django 5.1.5 on 2025-02-27 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0002_balance_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoefficientHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.IntegerField()),
                ('multiplier', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
