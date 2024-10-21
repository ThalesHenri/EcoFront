from django.shortcuts import render,redirect
import requests, json
from .forms import ProdutoForm,LoginForm,UsuarioForm
#from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse,JsonResponse
from urllib.parse import urlencode

# Create your views here.


def homepage(response):
    return render(response,'homepage.html')


def mostrarProdutos(response):

    # Token authorization with error handling
    try:
        access = response.session['access']
    except KeyError:
        # If 'access' is not in session, redirect to an error page
        return render(response, 'erroToken.html') 

    headers = {'Authorization': f'Bearer {access}'}
    
    try:
        resposta = requests.get(url='http://127.0.0.1:8081/api/produto/', headers=headers)
        resposta.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        produtos = resposta.json()
    except requests.exceptions.HTTPError:
        produtos = []
    except requests.exceptions.RequestException:
        # Handle any other exceptions from the requests library
        return render(response, 'erroRequest.html') 

    imageBaseUrl = 'http://127.0.0.1:8081'
    context = {
        'produtos': produtos,
        'is_empty': not produtos,  # Check if the product list is empty
        'imageUrl': imageBaseUrl
    }
    
    return render(response, 'index.html', context)
    
    
def cadastrarProduto(response):
    form = ProdutoForm()
    context ={
        'form':form
    }
    return render(response,'cadastroProdutos.html',context)


def cadastrarProdutoForm(response):
    if response.method == 'POST':   
        form = ProdutoForm(response.POST, response.FILES)
        
        if form.is_valid():
            # Token authorization
            try:
                access = response.session['access'] 
            except KeyError:
                return render(response, 'erroToken.html')
            
            # Handling image upload
            imagem = response.FILES['imagem']
            data = {
                'nome': form.cleaned_data['nome'],
                'dataValid': form.cleaned_data['dataValid'].isoformat(),
                'marca': form.cleaned_data['marca'],
                'peso': float(form.cleaned_data['peso']),
                'quantidade': int(form.cleaned_data['quantidade']),
                'frete': form.cleaned_data['frete'],
                'preco': float(form.cleaned_data['preco']),
            }
            files = {
                'imagem': ('imagem.jpg', imagem.file, 'image/jpeg')  # Example filename and content type
            }
            headers = {'Authorization': f'Bearer {access}'}
            
            # Debug prints
            print("Data to send:", data)
            
            url = 'http://127.0.0.1:8081/api/produto/'
            try:
                request = requests.post(url=url, data=data, headers=headers, files=files)
                request.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
                
                if request.status_code == 201:
                    return render(response, 'sucesso.html')
                else:
                    print("Unexpected status code:", request.status_code)
                    return HttpResponse('<h1>Erro no envio para a API</h1>', status=request.status_code)
            
            except requests.exceptions.HTTPError as e:
                print("HTTPError:", e)
                return HttpResponse('<h1>Erro de HTTP na comunicação com a API</h1>', status=request.status_code)
            except requests.exceptions.RequestException as e:
                print("RequestException:", e)
                return HttpResponse('<h1>Erro de comunicação com a API</h1>', status=500)
        
        else:
            # Handle invalid form case
            return render(response, 'cadastroProdutos.html', {'form': form, 'error': 'Formulário inválido. Verifique os dados e tente novamente.'})
    
    else:
        return HttpResponse("<h1>Método de solicitação inválido</h1>", status=405)
    
    
def quemSomos(response):
    return render(response,'quemSomos.html')


def login(response):
    form = LoginForm()
    context ={
        'form':form
    }
    return render(response,'login.html',context)


def loginEvent(request):
    if request.method == 'POST':
        cnpj = request.POST['cnpj']
        password = request.POST['password']
        response = requests.post('http://127.0.0.1:8081/api/token/', data={'cnpj': cnpj, 'password': password})
        
        if response.status_code == 200:
            tokens = response.json()
            request.session['access'] = tokens['access']
            request.session['refresh'] = tokens['refresh']
            return redirect('dashboard')
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout(request):
    # Fetch the refresh token from the session (assuming it is stored there)
    refresh_token = request.session.get('refresh')  
    
    if not refresh_token:
        return redirect('login')

    API_BASE_URL = 'http://127.0.0.1:8081/api/'
    response = requests.post(
        f'{API_BASE_URL}logout/',
        json={'refresh': refresh_token},  # Send refresh token in the request body
        # Removed the Authorization header
    )

    if response.status_code == 205:
        # Clear session and redirect to login
        request.session.flush()
        return redirect('login')
    else:
        # Handle errors if logout failed
        return HttpResponse(f"Logout failed: {response.content.decode()}", status=response.status_code)
    
def dashboard(request):
    token = request.session.get('access')
    refresh_token = request.session.get('refresh')

    if not token:
        return redirect('login')

    api_url = 'http://127.0.0.1:8081/api/protected/userdetail'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        print(user_info)
        return render(request, 'userInfo.html', {'userInfo': user_info})
    elif response.status_code == 401 and refresh_token:
        # Token expired, attempt to refresh
        refresh_response = requests.post('http://127.0.0.1:8081/api/token/refresh/', data={'refresh': refresh_token})

        if refresh_response.status_code == 200:
            new_tokens = refresh_response.json()
            request.session['access'] = new_tokens['access']
            request.session['refresh'] = new_tokens['refresh']
            # Retry fetching user info after refreshing tokens
            headers['Authorization'] = f'Bearer {new_tokens["access"]}'
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                user_info = response.json()
                print(user_info)
                return render(request, 'userInfo.html', {'userInfo': user_info})
            else:
                return JsonResponse({'error': 'Failed to retrieve user info after token refresh'}, status=400)
        else:
            # Refresh token also expired or invalid
            return JsonResponse({'error': 'Token expired and refresh failed'}, status=401)
    else:
        return JsonResponse({'error': 'Failed to retrieve user info'}, status=400)

def cadastrarUsuario(response):
    form = UsuarioForm()
    context ={
        'form':form
    }
    return render(response,'cadastrarUsuario.html',context)


def cadastrarUsuarioForm(response):
    if response.method == 'POST':
        form = UsuarioForm(response.POST)
        if form.is_valid():
            
            nome = form.cleaned_data['nome']
            cnpj = form.cleaned_data['cnpj']
            responsavel = form.cleaned_data['responsavel']
            cpfResponsavel = form.cleaned_data['cpfResponsavel']
            password = form.cleaned_data['password']
            
            
            data = {
                'nome':nome,
                'cnpj':cnpj,
                'responsavel':responsavel,
                'cpfResponsavel':cpfResponsavel,
                'password':password
            }
            
            headers={}
            url = 'http://127.0.0.1:8081/api/usuario/'
            request = requests.post(data=data,headers=headers,url=url)
            print("Response status code:", request.status_code)
            if request.status_code == 201:
                return render(response,'sucesso.html')
            else:
                print(request.text, request.status_code)
                return HttpResponse('<h1>erro no envio para a API</h1>')
        else:
            # Handle invalid form case
            return render(response, 'cadastrarUsuario.html', {'form': form, 'error': 'Form data is invalid'})
    else:
        return HttpResponse("invalid request Method",status=405)
                



