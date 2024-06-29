from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth import login, logout 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .forms import UserRegistrationForm, UpdateUserProfileForm

# Create your views here.
def SendAccountEmail(user, key):
    mail_subject = key + ' Confirmation'        
    template = 'accounts/email_template.html'
    message = render_to_string(template, {
        'user': user,
        'key': key,
    })
    send_email = EmailMultiAlternatives(mail_subject, '', to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account Created Successfully!')
        SendAccountEmail(self.request.user, 'User Registration')
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        messages.success(self.request, 'Logged in Successfully!')
        return reverse_lazy('home')
    
class UserLogOutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
            messages.success(self.request, 'Logged Out Successfully!')
        return reverse_lazy('home')

class UserBankAccountView(View):
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        form = UpdateUserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

class UserBankAccountUpdateView(View):
    template_name = 'accounts/edit_profile.html'    

    def get(self, request):
        form = UpdateUserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UpdateUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'User Profile Updated Successfully!')
            SendAccountEmail(self.request.user, 'User Profile Updated')
            return redirect('profile')        
        return render(request, self.template_name, {'form': form})  
    
class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Password Updated Successfully!')
        SendAccountEmail(self.request.user, 'Password Updated')
        return super().form_valid(form)