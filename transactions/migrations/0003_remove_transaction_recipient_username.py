# Generated by Django 5.0.6 on 2024-06-27 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transaction_recipient_account_no_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='recipient_username',
        ),
    ]
