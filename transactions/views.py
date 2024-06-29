from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm, TransferMoneyForm
from .constants import DEPOSIT, WITHDRAW, TRANSFER1, TRANSFER2, LOAN_REQUEST, LOAN_REPAY
from accounts.models import UserBankAccount

# Create your views here.
def SendTransactionEmail(user, amount, key, sender=None):
    if key == 'Loan':
        mail_subject = key + ' Request Confirmation'
    else:
        mail_subject = key + ' Confirmation'
        
    template = 'transactions/email_template.html'
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
        'balance': user.account.balance,
        'key': key,
        'sender': sender
    })
    send_email = EmailMultiAlternatives(mail_subject, '', to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    key = ''
    success_url = reverse_lazy('statements')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'key': self.key
        })
        return context
    
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Money'
    key = 'Deposit'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    def form_valid(self, form):  
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"${'{:,.2f}'.format(float(amount))} deposited successfully!")
        SendTransactionEmail(self.request.user, amount, 'Deposit')
        return super().form_valid(form)
    
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'
    key = 'Withdraw'
    
    def get_initial(self):
        initial = {'transaction_type': WITHDRAW}
        return initial
    
    def form_valid(self, form):        
        account = self.request.user.account
        amount = form.cleaned_data.get('amount')
        account.balance -= amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"${'{:,.2f}'.format(float(amount))}  withdrawn successfully!")
        SendTransactionEmail(self.request.user, amount, 'Withdrawal')
        return super().form_valid(form)
    
class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Apply for a Loan'
    key = 'Loan'
    
    def get_initial(self):
        initial = {'transaction_type': LOAN_REQUEST}
        return initial
    
    def form_valid(self, form):        
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type = LOAN_REQUEST, loan_approval = True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have exceeded your loan limit!")
        messages.success(self.request, f"You Loan application has been submitted! Your Requested Loan Amount is ${'{:,.2f}'.format(float(amount))}")
        SendTransactionEmail(self.request.user, amount, 'Loan')
        return super().form_valid(form)
    
class TransactionStatementView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_statements.html'
    model = Transaction
    balance = 0
    
    def get_queryset(self):
        queryset= super().get_queryset().filter(
            account = self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
            
        queryset = queryset.order_by('-timestamp')
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })
        return context
    
class LoanRepaymentView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approval():
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -=loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_REPAY
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request, f"You have insufficient balance to Loan Repayment!")
                SendTransactionEmail(self.request.user, loan.amount, 'Loan Repayment')
                return redirect('loan_list')
            
class LoanListView(LoginRequiredMixin, ListView):
    template_name = 'transactions/loan_list.html'
    model = Transaction
    context_object_name = 'loans'
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type=LOAN_REQUEST)
        return queryset

class TransferMoneyView(TransactionCreateMixin):
    form_class = TransferMoneyForm
    title = 'Transfer Money'
    key = 'Transfer'
    
    def get_initial(self):
        initial = {'transaction_type': TRANSFER1}
        return initial
    
    def form_valid(self, form):        
        user_account = self.request.user.account
        recipient_account_no = form.cleaned_data.get('recipient_account_no')
        amount = form.cleaned_data.get('amount')        
        
        try:
            recipient = UserBankAccount.objects.get(account_no=recipient_account_no)
        except UserBankAccount.DoesNotExist:
            form.add_error('recipient_account_no', f"There is no account with the account number {recipient_account_no}.")
            return self.form_invalid(form)
            
        user_account.balance -= amount
        recipient.balance += amount
        
        user_account.save(
            update_fields = ['balance']
        )
        recipient.save(
            update_fields = ['balance']
        )        
        Transaction.objects.create(
            account=recipient,
            sender=user_account,
            amount=amount,
            balance_after_transaction=recipient.balance,
            transaction_type=TRANSFER2 
        )
        messages.success(self.request, f"${amount} transferred to account successfully!")
        SendTransactionEmail(self.request.user, amount, 'Transfer')
        SendTransactionEmail(recipient.user, amount, 'Transferred Money Received', self.request.user)
        return super().form_valid(form)
                
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))   