from django import forms
from .models import Produto,Usuario
from django.core.exceptions import ValidationError
import re

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'dataValid', 'marca', 'peso', 'quantidade', 'frete', 'preco', 'imagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'dataValid': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Validade'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade'}),
            'frete': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frete'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }
        
def validate_cnpj(value):
    if not re.match(r'^\d+$', value):
        raise ValidationError('CNPJ must be numeric.')

class LoginForm(forms.Form):
    cnpj = forms.CharField(
        label='CNPJ',
        max_length=100,
        validators=[validate_cnpj]
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput
    )

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome','cnpj','responsavel','cpfResponsavel','password']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Responsável'}),
            'cpfResponsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF do Responsável'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'}),
        }
    
    
