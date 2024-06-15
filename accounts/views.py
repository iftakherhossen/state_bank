from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout 
from django.urls import reverse_lazy
from django.views import View
from .forms import UserRegistrationForm, UpdateUserProfileForm

# Create your views here.
class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')
    
class UserLogOutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
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
            return redirect('profile')
        return render(request, self.template_name, {'form': form})