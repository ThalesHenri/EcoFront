from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
import requests
from django.contrib import messages
from django.db.models import Sum, Avg
from .models import User, Comprador, Vendedor, Pacote, Pedido, Pagamento, Avaliacao
import jwt



API_ENDPOINT = 'http://localhost:8080/api/'  # Substitua pelo endpoint real da API

def home(request):
    return render(request, 'main/index.html')


def get_user_id_from_token(token):
    try:
        # Decodifica o token sem verificar assinatura
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get('user_id')  # ou o nome do campo no seu token
    except jwt.DecodeError:
        return None


def get_user_type_from_token(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        tipo = payload.get('tipo')
        return tipo  # ou o nome do campo no seu token
    except jwt.DecodeError:
        return None
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        url = API_ENDPOINT + 'token/'
        data = {'email': email, 'password': password}

        try:
            r = requests.post(url=url, data=data)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Erro de conexão com a API: {e}")
            return render(request, 'main/login.html')

        if r.status_code == 200:
            try:
                tokens = r.json() # salva a resposta JSON
            except ValueError:
                messages.error(request, 'Resposta da API não é um JSON válido.')
                return render(request, 'main/login.html')

            # Extrai os tokens
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')

            if access_token:
                 # Descobre o tipo do usuário pelo token
                user_tipo = get_user_type_from_token(access_token)
                
                # Salva os tokens na sessão
                request.session['access_token'] = access_token
                request.session['refresh_token'] = refresh_token
                request.session.set_expiry(3600)  # expira em 1 hora
                request.session['user_tipo'] = user_tipo
               
                
                # Verifica o tipo de usuário
                if user_tipo == 'comprador':
                    user_id = get_user_id_from_token(access_token)
                    headers = {'Authorization': f'Bearer {access_token}'}
                    comprador_request = requests.get(API_ENDPOINT + f'compradores/?user={user_id}/', headers=headers)
                    if comprador_request.status_code == 200:
                        messages.success(request, 'Login realizado com sucesso!')
                        return redirect('dashboard_comprador')
                    
                    messages.error(request, 'Usuário não encontrado ou tipo inválido.')
                    return render(request, 'main/login.html')
                
                elif user_tipo == 'vendedor':
                    user_id = get_user_id_from_token(access_token)
                    print(user_id)
                    headers = {'Authorization': f'Bearer {access_token}'}
                    vendedor_request = requests.get(API_ENDPOINT + f'vendedores/?user={user_id}/', headers=headers)
                    if vendedor_request.status_code == 200:
                        print("passou aqui")
                        messages.success(request, 'Login realizado com sucesso!')
                        return redirect('dashboard_vendedor')
                
                messages.error(request, 'Usuário não encontrado ou tipo inválido.')
                return render(request, 'main/login.html')
                
                
            else:
                messages.error(request, 'Token JWT não encontrado na resposta.')
                return render(request, 'main/login.html')
        else:
            messages.error(request, f'Erro ao fazer login: {r.text}')
            return render(request, 'main/login.html')

    return render(request, 'main/login.html')

        
        
        

def logout_view(request):
    auth_logout(request)
    return redirect('home')


def register_comprador(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        username = request.POST['username']
        email = request.POST['email']
        telefone = request.POST['telefone']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'main/register_comprador.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'main/register_comprador.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return render(request, 'main/register_comprador.html')
        data = {
                'nome': nome,
                'telefone': telefone,
                'username': username,
                'email': email,
                'password': password,
                'tipo': 'Comprador'
            }
        try:
            # Criar usuário
            r = requests.post(API_ENDPOINT + 'registerComprador/', data=data)
            if r.status_code != 201:
                messages.error(request, f'Erro ao criar conta: {r.text}')
                return render(request, 'main/register_comprador.html')
            elif r.status_code == 201:
                messages.success(request, 'Cadastro realizado com sucesso!')
                return redirect('login')   
            
        except Exception as e:
            messages.error(request, 'Erro ao criar conta. Tente novamente.')
    
    return render(request, 'main/register_comprador.html')

def register_vendedor(request):
    if request.method == 'POST':
        nome_empresa = request.POST['nome_empresa']
        representante = request.POST['representante']
        username = request.POST['username']
        cnpj = request.POST['cnpj']
        email = request.POST['email']
        telefone = request.POST['telefone']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'main/register_vendedor.html')
        
        try:
            # Criar usuário
            data = {
                'nome_empresa': nome_empresa,
                'representante': representante,
                'cnpj': cnpj,
                'telefone': telefone,
                'username': username,
                'email': email,
                'password': password,
                'tipo': 'Vendedor'
            }
            r = requests.post(API_ENDPOINT + 'registerVendedor/', data=data)
            if r.status_code != 201:
                messages.error(request, f'Erro ao criar conta: {r.text}')
                return render(request, 'main/register_vendedor.html')   
            elif r.status_code == 201:
                messages.success(request, 'Cadastro realizado com sucesso!')
                return redirect('login')
            
        except Exception as e:
            messages.error(request, 'Erro ao criar conta. Tente novamente.')
    
    return render(request, 'main/register_vendedor.html')

def dashboard_comprador(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')

    # Pega o user_id do token
    user_id = get_user_id_from_token(access_token)
    headers = {'Authorization': f'Bearer {access_token}'}

    # Busca o comprador relacionado ao user_id
    compr_resp = requests.get(API_ENDPOINT + f'compradores/?user={user_id}', headers=headers)
    compradores = compr_resp.json() if compr_resp.status_code == 200 else []

    if not compradores:
        return redirect('login')  # ou mostrar mensagem de erro

    comprador = compradores[0]  # Pega o único comprador

    # Pedidos do comprador
    pedidos_resp = requests.get(API_ENDPOINT + f'pedidos/?comprador={comprador["id"]}', headers=headers)
    pedidos = pedidos_resp.json() if pedidos_resp.status_code == 200 else []

    total_pedidos = len(pedidos)
    pedidos_pendentes = len([p for p in pedidos if p.get('status_pedido') == 'Em andamento'])
    total_gasto = sum(p.get('preco_total', 0) for p in pedidos)
    pedidos_recentes = sorted(pedidos, key=lambda x: x.get('data_pedido', ''), reverse=True)[:5]

    # Avaliações feitas pelo comprador
    aval_resp = requests.get(API_ENDPOINT + f'avaliacoes/?comprador={comprador["id"]}', headers=headers)
    avaliacoes_feitas = len(aval_resp.json()) if aval_resp.status_code == 200 else 0
   
    r = requests.get(API_ENDPOINT + 'vendedores/',headers=headers)
    if r.status_code == 200:
        estabelecimentos = r.json()
    
    
    #formatação de dados
    
    compradorNome = comprador['user']['username']
    context = {
        'comprador': comprador,
        'estabelecimentos': estabelecimentos,
        'compradorNome': compradorNome,
        'total_pedidos': total_pedidos,
        'pedidos_pendentes': pedidos_pendentes,
        'total_gasto': total_gasto,
        'avaliacoes_feitas': avaliacoes_feitas,
        'pedidos_recentes': pedidos_recentes,
    }

    return render(request, 'main/dashboard_comprador.html', context)


def dashboard_vendedor(request):
    tipo = request.session.get('user_tipo')
    print('Chegou aqui',tipo)
    user_id = get_user_id_from_token(request.session.get('access_token'))
    print(user_id)
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')
    r = requests.get(API_ENDPOINT + f'vendedores/{user_id}', headers=headers)
    if r.status_code == 200:
        vendedor = r.json()
    elif r.status_code == 404:
        messages.error(request, 'Vendedor não encontrado.')
        return redirect('login')
    
    # Estatísticas
    pacotes_request = requests.get(API_ENDPOINT + f'pacotes/?vendedor={vendedor["id"]}', headers=headers)
    if pacotes_request.status_code == 200:
        pacotes = pacotes_request.json()
    total_pacotes = pacotes.count(pacotes)
    
    pedidos_request = requests.get(API_ENDPOINT + f'pedidos/?vendedor={vendedor["id"]}', headers=headers)
    if pedidos_request.status_code == 200:
        pedidos = pedidos_request.json()
    pedidos_recebidos = pedidos.count(pedidos)
    
    total_vendas = 0 # por enquanto
    avaliacoes_request = requests.get(API_ENDPOINT + f'avaliacoes/?vendedor={vendedor["id"]}', headers=headers)
    if avaliacoes_request.status_code == 200:
        avaliacoes = avaliacoes_request.json()
    media_avaliacoes = 0 # por enquanto
    # Pedidos recentes
    pedidos_recentes = 0 # por enquanto
    
    context = {
        'vendedor': vendedor,
        'total_pacotes': total_pacotes,
        'pedidos_recebidos': pedidos_recebidos,
        'total_vendas': total_vendas,
        'media_avaliacoes': media_avaliacoes,
        'pedidos_recentes': pedidos_recentes,
    }
    
    return render(request, 'main/dashboard_vendedor.html', context)



def pacotes_list(request):
    
    # if request.user.tipo != 'Comprador':
    #     return redirect('dashboard_vendedor')
    
    pacotes = Pacote.objects.filter(quant_disponivel__gt=0).order_by('-id')
    
    return render(request, 'main/pacotes_list.html', {'pacotes': pacotes})



def estabelescimento(request,vendedor_id):
    r = requests.get(API_ENDPOINT + f'vendedores/{vendedor_id}/')
    if r.status_code == 200:
            vendedor = r.json()
    else:
            messages.error(request, 'Erro ao carregar o estabelecimento.')
            return redirect('dashboard_comprador')
    r = requests.get(API_ENDPOINT + f'pacotes/?vendedor={vendedor_id}')
    if r.status_code == 200:
            pacotes = r.json()
            print(pacotes)
    else:
            messages.error(request, 'Erro ao carregar os pacotes.')
            return redirect('dashboard_comprador')
    context = {
        'vendedor': vendedor,
        'pacotes': pacotes
    }
    return render(request, 'main/estabelecimento.html', context=context)


def meus_pedidos(request):
    if request.user.tipo != 'Comprador':
        return redirect('dashboard_vendedor')
    
    comprador = get_object_or_404(Comprador, user=request.user)
    pedidos = Pedido.objects.filter(comprador=comprador).order_by('-data_pedido')
    
    return render(request, 'main/meus_pedidos.html', {'pedidos': pedidos})

@login_required
def fazer_pedido(request, pacote_id):
    if request.user.tipo != 'Comprador':
        return redirect('dashboard_vendedor')
    
    if request.method == 'POST':
        comprador = get_object_or_404(Comprador, user=request.user)
        pacote = get_object_or_404(Pacote, id=pacote_id)
        
        if pacote.quant_disponivel > 0:
            # Criar pedido
            pedido = Pedido.objects.create(
                comprador=comprador,
                pacote=pacote,
                preco_total=pacote.preco,
                status_pedido='Em andamento',
                status_pagamento='Pendente'
            )
            
            # Reduzir quantidade disponível
            pacote.quant_disponivel -= 1
            pacote.save()
            
            messages.success(request, 'Pedido realizado com sucesso!')
            return redirect('meus_pedidos')
        else:
            messages.error(request, 'Pacote não disponível.')
    
    return redirect('pacotes_list')


def cadastrar_pacote(request):
    user_id = get_user_id_from_token(request.session.get('access_token'))
    tipo = request.session.get('user_tipo')
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')  
          
    if request.method == 'POST':
        nome_pacote = request.POST['nome_pacote']
        categoria = request.POST['categoria']
        preco = request.POST['preco']
        quant_disponivel = request.POST['quant_disponivel']
        descricao = request.POST['descricao']
        vendedor = user_id
        print(vendedor,'olha aqui o vendedor')
        data = {
        'nome_pacote': nome_pacote,
        'categoria': categoria,
        'preco': preco,
        'quant_disponivel': quant_disponivel,
        'descricao': descricao,
        'vendedor_id': vendedor
        }
        r = requests.post(API_ENDPOINT + 'pacotes/', data=data, headers=headers)
        print(headers)
        if r.status_code == 201:
            messages.success(request, 'Pacote cadastrado com sucesso!')
            print("pacotes cadastrados com sucesso!")
            return redirect('meus_pacotes')
        elif r.status_code == 400:
            errors = r.json()
            for field, msgs in errors.items():
                for msg in msgs:
                    messages.error(request, f"{field}: {msg}")
        elif r.status_code == 403:
            messages.error(request, 'Você não tem permissão para realizar esta ação.')            
    elif request.method == 'GET':
        pass
    else:
        messages.error(request, 'Método inválido.')
        return redirect('login')
    return render(request, 'main/cadastrar_pacote.html')


def meus_pacotes(request):
    tipo = get_user_type_from_token(request.session.get('access_token'))
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')  
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    user_id = get_user_id_from_token(request.session.get('access_token'))    
    pacotes_request = requests.get(API_ENDPOINT + f'pacotes/?vendedor={user_id}',headers=headers)
    if pacotes_request.status_code == 200:
        pacotes = pacotes_request.json()
    else:
        pacotes = []
        messages.error(request, 'Erro ao carregar os pacotes.')
    context = {
        'pacotes': pacotes
    }
    
    return render(request, 'main/meus_pacotes.html', context = context)

@login_required
def pedidos_recebidos(request):
    if request.user.tipo != 'Vendedor':
        return redirect('dashboard_comprador')
    
    vendedor = get_object_or_404(Vendedor, user=request.user)
    pedidos = Pedido.objects.filter(pacote__vendedor=vendedor).order_by('-data_pedido')
    
    return render(request, 'main/pedidos_recebidos.html', {'pedidos': pedidos})

@login_required
def atualizar_pedido(request, pedido_id):
    if request.user.tipo != 'Vendedor':
        return redirect('dashboard_comprador')
    
    if request.method == 'POST':
        vendedor = get_object_or_404(Vendedor, user=request.user)
        pedido = get_object_or_404(Pedido, id=pedido_id, pacote__vendedor=vendedor)
        
        status = request.POST.get('status')
        if status in ['Finalizado', 'Cancelado']:
            pedido.status_pedido = status
            if status == 'Finalizado':
                pedido.status_pagamento = 'Aprovado'
            pedido.save()
            
            messages.success(request, f'Pedido {status.lower()} com sucesso!')
    
    return redirect('pedidos_recebidos')

# Views antigas mantidas para compatibilidade
def login(request):
    return login_view(request)

def registerComprador(request):
    return register_comprador(request)