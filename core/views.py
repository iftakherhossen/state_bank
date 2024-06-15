from django.shortcuts import render
from django.views.generic import TemplateView
from .constants import FEATURES

# Create your views here.
class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = FEATURES
        return context    