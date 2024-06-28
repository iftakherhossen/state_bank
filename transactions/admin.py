from typing import Any
from django.contrib import admin
from .models import Transaction, Bank
from .views import SendTransactionEmail

# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approval']
    
    def save_model(self, request, obj, form, change):
        if obj.loan_approval == True:
            obj.account.balance += obj.amount
            obj.balance_after_transaction = obj.account.balance
            obj.account.save()
            SendTransactionEmail(obj.account.user, obj.amount,'Loan Approval')
        super().save_model(request, obj, form, change)
        
admin.site.register(Bank)