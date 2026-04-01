from django import forms
from .models import Book, Address

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'image_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'postal_code', 'country']
        widgets = {
            'street': forms.TextInput(attrs={'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State / Province'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Postal code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        }
