from django.urls import path
from .views import DepositMoneyView, WithdrawMoneyView, TransactionStatementView, TransferMoneyView, LoanRequestView, LoanListView, LoanRepaymentView

urlpatterns = [
    path('deposit/', DepositMoneyView.as_view(), name='deposit'),
    path('withdraw/', WithdrawMoneyView.as_view(), name='withdraw'),
    path('statements/', TransactionStatementView.as_view(), name='statements'),
    path('transfer/', TransferMoneyView.as_view(), name='transfer'),
    path('loan-request/', LoanRequestView.as_view(), name='loan_request'),
    path('loans/', LoanListView.as_view(), name='loan_list'),    
    path('loan-repay/<int:loan_id>/', LoanRepaymentView.as_view(), name='loan_repay'),
]