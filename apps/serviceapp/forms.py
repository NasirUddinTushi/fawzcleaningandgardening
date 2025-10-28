from django import forms
from django.forms import ModelForm
from .models import QuoteRequest, Application, Contact


class QuoteRequestForm(ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ['name', 'email', 'phone', 'service', 'city', 'postal_code', 'address', 'message']
        # widgets = {
        #     'message': forms.Textarea(attrs={'rows': 3}),
        # }


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'email', 'phone', 'resume', 'message']


# Contact Form
class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your first name',
                'class': 'w-full px-4 py-3 rounded-lg border border-input bg-background focus-ring transition-all duration-300',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your last name',
                'class': 'w-full px-4 py-3 rounded-lg border border-input bg-background focus-ring transition-all duration-300',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'w-full px-4 py-3 rounded-lg border border-input bg-background focus-ring transition-all duration-300',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'class': 'w-full px-4 py-3 rounded-lg border border-input bg-background focus-ring transition-all duration-300',
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Enter subject',
                'class': 'w-full px-4 py-3 rounded-lg border border-input bg-background focus-ring transition-all duration-300',
            }),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter your message',
                'class': 'w-full px-4 py-3 rounded-lg border border-input bg-background focus-ring transition-all duration-300',
            }),
        }
