from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE

# Create your models here.
class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name='transactions', on_delete=models.CASCADE)
    recipient_account_no = models.CharField(max_length=100, null=True, blank=True)
    sender = models.ForeignKey(UserBankAccount, related_name='transfer_sender', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approval = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        
        
class Bank(models.Model):
    isBankrupt = models.BooleanField(default=False)
    
    def __str__(self):
        return "Bank Status"