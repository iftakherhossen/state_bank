# Generated by Django 5.0.6 on 2024-06-11 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbankaccount',
            name='account_type',
            field=models.CharField(choices=[('Savings', 'Savings'), ('Student', 'Student'), ('Current', 'Current')], max_length=10),
        ),
    ]