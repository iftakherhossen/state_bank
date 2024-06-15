from django import forms
from .models import Transaction
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
        
class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 500
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"You need to deposit at least $ {min_deposit_amount}"
            )
        return amount
    
class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdrawal_amount = 500
        max_withdrawal_amount = 100000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if amount > balance:
            raise forms.ValidationError(
                f"You have insufficient balance!"
            )
        if amount < min_withdrawal_amount:
            raise forms.ValidationError(
                f"You can withdraw at least $ {min_withdrawal_amount}"
            )
        if amount > max_withdrawal_amount:
            raise forms.ValidationError(
                f"You can withdraw at most $ {max_withdrawal_amount}"
            )
        return amount
    
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount
    
class TransferTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['recipient_username', 'recipient_account_no', 'amount', 'transaction_type']
       
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
class TransferMoneyForm(TransferTransactionForm):
    def clean_amount(self):
        account = self.account
        min_transfer_amount = 500
        max_transfer_amount = 100000
        balance = account.balance
        recipient_account_no = self.cleaned_data.get('recipient_account_no')
        recipient_account = User.objects.get(account_no=recipient_account_no)
        print(recipient_account)
        amount = self.cleaned_data.get('amount')
        
        if amount > balance:
            raise forms.ValidationError(
                f"You have insufficient balance!"
            )
        if recipient_account:
            print(recipient_account)      
        return amount
            