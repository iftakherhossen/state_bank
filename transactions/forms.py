from django import forms
from .models import Transaction
from django.contrib.auth.models import User
from accounts.models import UserBankAccount
from .models import Bank


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
        bank = Bank.objects.first()
        if bank and bank.isBankrupt:
            raise forms.ValidationError("The Bank is Bankrupt!")
            
        account = self.account
        min_withdrawal_amount = 500
        max_withdrawal_amount = 1000000
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
        fields = ['recipient_account_no', 'amount', 'transaction_type']
       
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        bank = Bank.objects.first()
        if bank and bank.isBankrupt:
            self.add_error(None, "The Bank is Bankrupt")
        
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
class TransferMoneyForm(TransferTransactionForm):
    def clean_amount(self):
        account = self.account
        min_transfer_amount = 500
        max_transfer_amount = 1000000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        bank = Bank.objects.first()
        
        if bank and bank.isBankrupt:
            raise forms.ValidationError("The Bank is Bankrupt!")        
        if amount > balance:
            raise forms.ValidationError(
                f"You have insufficient balance!"
            )
        if amount < min_transfer_amount:
            raise forms.ValidationError(
                f"You have to transfer at least $ {min_transfer_amount}"
            )
        if amount > max_transfer_amount:
            raise forms.ValidationError(
                f"You can transfer at most $ {max_transfer_amount}"
            )        
        return amount
    
    def clean_recipient_account(self):
        recipient_account_no = self.cleaned_data.get('recipient_account_no')
        
        if len(str(recipient_account_no)) != 10:
            raise forms.ValidationError(
                "The account number must be exactly 10 digits."
            )
        if not UserBankAccount.objects.filter(account_no=recipient_account_no).exists():
            raise forms.ValidationError(
                f"There is no account with the account no {recipient_account_no}!"
            )
        return recipient_account_no
              