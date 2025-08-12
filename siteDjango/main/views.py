from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'main/index.html')


def login(request):
    # Placeholder for login logic
    
    return render(request, 'main/login.html')


def registerComprador(request):
    # Placeholder for registering a buyer
    return render(request, 'main/registerComprador.html')


def registerVendedor(request):
    # Placeholder for registering a seller
    return render(request, 'main/registerVendedor.html')