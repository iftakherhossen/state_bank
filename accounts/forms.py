from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .constants import ACCOUNT_TYPE, GENDER
from .models import UserBankAccount, UserAddress

class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER)
    street_address = forms.CharField(max_length=100)    
    city = forms.CharField(max_length=100) 
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'account_type', 'street_address', 'city', 'postal_code', 'country', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit == True:
            user.save()
            birthday = self.cleaned_data.get('birthday')
            gender = self.cleaned_data.get('gender')
            account_type = self.cleaned_data.get('account_type')
            street_address = self.cleaned_data.get('street_address')
            city = self.cleaned_data.get('city')
            postal_code = self.cleaned_data.get('postal_code')            
            country = self.cleaned_data.get('country')
            
            UserBankAccount.objects.create(
                user = user,
                birthday = birthday,
                gender = gender,
                account_type = account_type,
                account_no = 2024100000 + user.id
            )
            
            UserAddress.objects.create(
                user = user,
                street_address = street_address,
                city = city,
                postal_code = postal_code,
                country = country
            )
            
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500 mt-2 '
                )
            })
            
class UpdateUserProfileForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER)
    street_address = forms.CharField(max_length=100)    
    city = forms.CharField(max_length=100) 
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none text-black '
                    'focus:bg-white focus:border-gray-500 mt-2 '
                )
            })
            
            if self.instance:
                try:
                    user_account = self.instance.account
                    user_address = self.instance.address
                except UserBankAccount.DoesNotExist:
                    user_account = None
                    user_address = None
                    
                if user_account:
                    self.fields['account_type'].initial = user_account.account_type
                    self.fields['birthday'].initial = user_account.birthday
                    self.fields['gender'].initial = user_account.gender
                    self.fields['street_address'].initial = user_address.street_address
                    self.fields['city'].initial = user_address.city
                    self.fields['postal_code'].initial = user_address.postal_code
                    self.fields['country'].initial = user_address.country
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserBankAccount.objects.get_or_create(user=user)
            user_address, created = UserAddress.objects.get_or_create(user=user) 

            user_account.account_type = self.cleaned_data['account_type']            
            user_account.birthday = self.cleaned_data['birthday']
            user_account.gender = self.cleaned_data['gender']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user