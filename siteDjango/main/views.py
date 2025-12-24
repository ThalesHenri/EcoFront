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
        print(payload)
        return payload.get('user_id')  # ou o nome do campo no seu token
    except jwt.DecodeError:
        return None

def get_vendedor_id_from_token(token):
    try:
        # Decodifica o token sem verificar assinatura
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get('real_id')  # ou o nome do campo no seu token
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
    if request.method != 'POST':
        return render(request, 'main/login.html')

    email = request.POST.get('email')
    password = request.POST.get('password')

    url = API_ENDPOINT + 'token/'
    data = {'email': email, 'password': password}

    try:
        r = requests.post(url=url, data=data)
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Erro de conexão com a API: {e}")
        return render(request, 'main/login.html')

    if r.status_code != 200:
        messages.error(request, 'E-mail ou senha inválidos.')
        return render(request, 'main/login.html')

    try:
        tokens = r.json()
    except ValueError:
        messages.error(request, 'Resposta inválida da API.')
        return render(request, 'main/login.html')

    request.session.flush()  # Limpa sessão anterior
    access_token = tokens.get('access')
    refresh_token = tokens.get('refresh')

    if not access_token:
        messages.error(request, 'Token de autenticação não encontrado.')
        return render(request, 'main/login.html')

    # Salva tokens na sessão
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    request.session.set_expiry(3600)

    # Descobre tipo e id do usuário
    user_tipo = get_user_type_from_token(access_token)
    user_id = get_user_id_from_token(access_token)

    if not user_tipo or not user_id:
        messages.error(request, 'Token inválido ou corrompido.')
        return render(request, 'main/login.html')

    headers = {'Authorization': f'Bearer {access_token}'}

    if user_tipo == 'comprador':
        response = requests.get(
            API_ENDPOINT + f'compradores/?user={user_id}/',
            headers=headers
        )

        if response.status_code == 200:
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('dashboard_comprador')

        messages.error(request, 'Perfil de comprador não encontrado.')
        return render(request, 'main/login.html')

    if user_tipo == 'vendedor':
        response = requests.get(
            API_ENDPOINT + f'vendedores/?user={user_id}/',
            headers=headers
        )

        if response.status_code == 200:
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('dashboard_vendedor')

        messages.error(request, 'Perfil de vendedor não encontrado.')
        return render(request, 'main/login.html')

    messages.error(request, 'Tipo de usuário não reconhecido pelo sistema.')
    return render(request, 'main/login.html')

        
        
        

def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect('home')

def register_comprador(request):
    if request.method != 'POST':
        return render(request, 'main/register_comprador.html')

    nome = request.POST.get('nome')
    username = request.POST.get('username')
    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

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
        r = requests.post(
            API_ENDPOINT + 'registerComprador/',
            data=data,
            timeout=10
        )

    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar à API.')
        return render(request, 'main/register_comprador.html')

    except requests.exceptions.Timeout:
        messages.error(request, 'A API demorou para responder.')
        return render(request, 'main/register_comprador.html')

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro inesperado na comunicação com a API: {e}')
        return render(request, 'main/register_comprador.html')

    # --- Resposta da API ---
    if r.status_code == 201:
        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('login')

    if r.status_code == 400:
        messages.error(request, 'Dados inválidos. Verifique os campos.')
        return render(request, 'main/register_comprador.html')

    if r.status_code == 500:
        messages.error(
            request,
            'Erro interno no servidor. Contate o administrador.'
        )
        return render(request, 'main/register_comprador.html')

    # 🔴 fallback explícito
    messages.error(
        request,
        f'Erro ao criar conta ({r.status_code}): {r.text}'
    )
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
    total_gasto = sum(float(p.get('preco_total', 0)) for p in pedidos)
    pedidos_recentes = sorted(pedidos, key=lambda x: x.get('data_pedido', ''), reverse=True)[:5]

    # Avaliações feitas pelo comprador
    aval_resp = requests.get(API_ENDPOINT + f'avaliacoes/?comprador={comprador["id"]}', headers=headers)
    avaliacoes_feitas = len(aval_resp.json()) if aval_resp.status_code == 200 else 0
   
    r = requests.get(API_ENDPOINT + 'vendedores/',headers=headers)
    if r.status_code == 200:
        estabelecimentos = r.json()
    else:
        estabelecimentos = []
    
    
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
    print(pedidos)
    return render(request, 'main/dashboard_comprador.html', context)


def dashboard_vendedor(request):
    tipo = request.session.get('user_tipo')
    user_id = get_vendedor_id_from_token(request.session.get('access_token'))
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')
    r = requests.get(API_ENDPOINT + f'vendedores/{user_id}', headers=headers)
    print(f"o user id é {user_id}")
    if r.status_code == 200:
        vendedor = r.json()
    elif r.status_code == 404:
        messages.error(request, 'Vendedor não encontrado.')
        return redirect('login')
    print(vendedor["id"])
    # Estatísticas
    pacotes_request = requests.get(API_ENDPOINT + f'pacotes/?vendedor={user_id}', headers=headers)
    if pacotes_request.status_code == 200:
        pacotes = pacotes_request.json()
        total_pacotes = len(pacotes)
    
    pedidos_request = requests.get(API_ENDPOINT + f'pedidos/?vendedor={user_id}', headers=headers)
    if pedidos_request.status_code == 200:
        pedidos = pedidos_request.json()
        pedidos_recebidos = len(pedidos)
    
    total_vendas = 0 # por enquanto
    avaliacoes_request = requests.get(API_ENDPOINT + f'avaliacoes/?vendedor={user_id}', headers=headers)
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
    tipo = get_user_type_from_token(request.session.get('access_token'))
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    if tipo != 'comprador':
        return redirect('dashboard_vendedor')  
    r = requests.get(API_ENDPOINT + 'pacotes/', headers=headers)
    if r.status_code == 200:
        pacotes = r.json()
    else:
        pacotes = []
        messages.error(request, 'Erro ao carregar os pacotes.')

    context = {
        'pacotes': pacotes,
    }
   
    return render(request, 'main/pacotes_list.html', context=context)



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
           
    else:
            messages.error(request, 'Erro ao carregar os pacotes.')
            return redirect('dashboard_comprador')
    context = {
        'vendedor': vendedor,
        'pacotes': pacotes
    }
    print(vendedor)
    return render(request, 'main/estabelecimento.html', context=context)


def meus_pedidos(request):
    access_token = request.session.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    tipo = get_user_type_from_token(access_token)
    user_id = get_user_id_from_token(access_token)
    if tipo != 'comprador':
        return redirect('dashboard_vendedor')
    pedidos_request = requests.get(API_ENDPOINT + f'pedidos/?comprador__user={user_id}', headers=headers)
    if pedidos_request.status_code == 200:
        pedidos = pedidos_request.json()
    else:
        pedidos = []
        messages.error(request, 'Erro ao carregar os pedidos.')
    context = {
        'pedidos':pedidos
    }
    return render(request, 'main/meus_pedidos.html', context=context)


def fazer_pedido(request, pacote_id):
    access_token = request.session.get('access_token')
    tipo = get_user_type_from_token(access_token)
    user_id = get_user_id_from_token(access_token)
    headers = {'Authorization': f'Bearer {access_token}'}
    quantidade = request.POST.get('quantidade')
    if tipo != 'comprador':
        return redirect('dashboard_vendedor')
    
    if request.method == 'POST':
        comprador_request  = requests.get(API_ENDPOINT + f'compradores/{user_id}', headers=headers)
        if comprador_request.status_code == 200:
            comprador = comprador_request.json()
        else:
            messages.error(request, 'Erro ao carregar o comprador.')
            print('erro ao carregar o comprador')
            return redirect('pacotes_list')
        pacote_request = requests.get(API_ENDPOINT + f'pacotes/{pacote_id}', headers=headers)
        if pacote_request.status_code == 200:
            pacote = pacote_request.json()
        else:
            messages.error(request, 'Erro ao carregar o pacote.')
            return redirect('pacotes_list')
        if pacote['quant_disponivel'] > 0:
            # Criar pedido
            data = {
                'comprador': comprador['id'],
                'pacote': pacote['id'],
                'preco_total': pacote['preco'],
                'quantidade': quantidade,
                'status_pagamento': 'Pendente',
                'status_pedido': 'Em andamento'  # Inicialmente vazio
            }
            print(data)
            r = requests.post(API_ENDPOINT + 'pedidos/', data=data, headers=headers)
            print(headers)
            if r.status_code != 201:
                messages.error(request, f'Erro ao fazer pedido: {r.text}')
                return redirect('pacotes_list')
            elif r.status_code == 201:
                r.response = r.json()
                print("Pedido criado com sucesso!")
                # capta o initiation point
                initiation_point = r.response.get('init_point')
                print(initiation_point,"INICIATION POINT AQUI")
                return redirect(initiation_point)
            
            # Reduzir quantidade disponível
            pacote['quant_disponivel'] -= 1
            r = requests.patch(API_ENDPOINT + f'pacotes/{pacote_id}/', data=pacote, headers=headers)
            if r.status_code != 200:
                messages.error(request, f'Erro ao atualizar o pacote: {r.text}')
                return redirect('pacotes_list')
            elif r.status_code == 200:
                print("Pedido foi feito")
                
            
            messages.success(request, 'Pedido realizado com sucesso!')
            return redirect('meus_pedidos')
        else:
            messages.error(request, 'Pacote não disponível.')
    
    return redirect('pacotes_list')



def pagamentoSucesso(request):
    return render(request, 'main/pagamento_sucesso.html')

def pagamentoFalha(request):
    return render(request, 'main/pagamento_falha.html')

def pagamentoPendente(request):
    return render(request, 'main/pagamento_pendente.html')

def cadastrar_pacote(request):
    access_token = request.session.get('access_token')
    user_id = get_vendedor_id_from_token(access_token)
    tipo = request.session.get('user_tipo')
    headers = {'Authorization': f'Bearer {access_token}'}
    
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')  
    vendedor_request = requests.get(API_ENDPOINT + f'vendedores/{user_id}/', headers=headers).json()     
    if request.method == 'POST':
        nome_pacote = request.POST['nome_pacote']
        categoria = request.POST['categoria']
        preco = request.POST['preco']
        quant_disponivel = request.POST['quant_disponivel']
        descricao = request.POST['descricao']
        
        data = {
        'nome_pacote': nome_pacote,
        'categoria': categoria,
        'preco': preco,
        'quant_disponivel': quant_disponivel,
        'descricao': descricao,
        'vendedor_id': vendedor_request['id'],
        
        }
        imagem = request.FILES.get('imagem')
        files = {}
        if imagem:
            files['imagem'] = (imagem.name, imagem.read(), imagem.content_type)
        r = requests.post(API_ENDPOINT + 'pacotes/', data=data,files=files, headers=headers)
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
    user_id = get_vendedor_id_from_token(request.session.get('access_token'))    
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


def editar_pacote(request, pacote_id):
    tipo = get_user_type_from_token(request.session.get('access_token'))
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')  
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    if request.method == 'POST':
        nome_pacote = request.POST['nome_pacote']
        categoria = request.POST['categoria']
        preco = request.POST['preco']
        quant_disponivel = request.POST['quant_disponivel']
        descricao = request.POST['descricao']
        
        data = {
        'nome_pacote': nome_pacote,
        'categoria': categoria,
        'preco': preco,
        'quant_disponivel': quant_disponivel,
        'descricao': descricao,
        }
        imagem = request.FILES.get('imagem')
        files = {}
        if imagem:
            files['imagem'] = (imagem.name, imagem.read(), imagem.content_type)
        r = requests.patch(API_ENDPOINT + f'pacotes/{pacote_id}/', data=data,files=files, headers=headers)
        print(headers)
        if r.status_code == 200:
            messages.success(request, 'Pacote atualizado com sucesso!')
            print("pacotes atualizados com sucesso!")
            return redirect('meus_pacotes')
        else:
            messages.error(request, f'Erro ao atualizar o pacote: {r.text}')
            return redirect('meus_pacotes')
    elif request.method == 'GET':
        pacote_request = requests.get(API_ENDPOINT + f'pacotes/{pacote_id}/', headers=headers)
        if pacote_request.status_code == 200:
            pacote = pacote_request.json()
            return render(request, 'main/editar_pacotes.html', {'pacote': pacote})
        else:
            messages.error(request, 'Erro ao carregar o pacote.')
            return redirect('meus_pacotes')


def excluir_pacote(request, pacote_id):
    tipo = get_user_type_from_token(request.session.get('access_token'))
    if tipo != 'vendedor':
        return redirect('dashboard_comprador')  
    headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
    r = requests.delete(API_ENDPOINT + f'pacotes/{pacote_id}/', headers=headers)
    if r.status_code == 204:
        messages.success(request, 'Pacote excluído com sucesso!')
    else:
        messages.error(request, f'Erro ao excluir o pacote: {r.text}')
    return redirect('meus_pacotes')


def pedidos_recebidos(request):
    # Verificar se o usuário é um vendedor
    access_token = request.session.get('access_token')
    tipo = get_user_type_from_token(access_token)
    if tipo != 'vendedor':
        messages.error(request, 'Acesso negado. Você não é um vendedor.')
    # Verificar o Id do usuario
    vendedor_id = get_vendedor_id_from_token(access_token)
    headers = {'Authorization': f'Bearer {access_token}'}
    # Busca os pedidos baseados no id do vendedor
    pedidos_request = requests.get(API_ENDPOINT + f'pedidos/vendedor/{vendedor_id}/', headers=headers)
    if pedidos_request.status_code == 200:
        pedidos = pedidos_request.json()
    else:
        pedidos = []
        messages.error(request, 'Erro ao carregar os pedidos.')
    # Renderiza o template e passa os pedidos como contexto
    context = {
        'pedidos': pedidos
    }
    print(pedidos)
    return render(request, 'main/pedidos_recebidos.html', context=context)



def detalhes_pedido(request, pedido_id):
    access_token = request.session.get('access_token')
    tipo = get_user_type_from_token(access_token)
    headers = {'Authorization': f'Bearer {access_token}'}
    if tipo == 'comprador':
        pedido_request = requests.get(API_ENDPOINT + f'pedidos/{pedido_id}/', headers=headers)
        if pedido_request.status_code == 200:
            pedido = pedido_request.json()
        else:
            messages.error(request, 'Erro ao carregar o pedido.')
            return redirect('meus_pedidos')
    elif tipo == 'vendedor':
        pedido_request = requests.get(API_ENDPOINT + f'pedidos/{pedido_id}/', headers=headers)
        if pedido_request.status_code == 200:
            pedido = pedido_request.json()
        else:
            messages.error(request, 'Erro ao carregar o pedido.')
            return redirect('pedidos_recebidos')
    else:
        return redirect('login')
    
    context = {
        'pedido': pedido
    }
    print(pedido)
    return render(request, 'main/detalhes_pedido.html', context=context)

    
    
def excluir_pedido(request, pedido_id):
    access_token = request.session.get('access_token')
    tipo = get_user_type_from_token(access_token)
    user_id = get_user_id_from_token(access_token)
    headers = {'Authorization': f'Bearer {access_token}'}
    if tipo != 'comprador':
        return redirect('dashboard_vendedor')
    pedido_request = requests.get(API_ENDPOINT + f'pedidos/{pedido_id}/', headers=headers)
    if pedido_request.status_code == 200:
        pedido = pedido_request.json()
        print(pedido)
        if int(pedido['comprador']) != int(user_id):
            messages.error(request, 'Você não tem permissão para excluir este pedido.')
            print(f"não tem permissão \n pedido id: {pedido['comprador']} \n user id: {user_id}")
            return redirect('meus_pedidos')
        if pedido['status_pedido'] == 'Cancelado':
            delete_request = requests.delete(API_ENDPOINT + f'pedidos/{pedido_id}/', headers=headers)
            if delete_request.status_code == 204:
                messages.success(request, 'Pedido excluído com sucesso.')
                print("pedido excluido com sucesso")
            else:
                messages.error(request, 'Erro ao excluir o pedido.')
                print("erro ao excluir o pedido")
        else:
            messages.error(request, 'Somente pedidos cancelados podem ser excluídos.')
            print("somente cancelados podem ser excluidos")
    else:
        messages.error(request, 'Pedido não encontrado.')
        print
    return redirect('meus_pedidos')

def cancelar_pedido(request, pedido_id):
    access_token = request.session.get('access_token')
    tipo = get_user_type_from_token(access_token)
    user_id = get_user_id_from_token(access_token)
    headers = {'Authorization': f'Bearer {access_token}'}
    if tipo != 'comprador':
        return redirect('dashboard_vendedor')
    pedido_request = requests.get(API_ENDPOINT + f'pedidos/{pedido_id}/', headers=headers)
    if pedido_request.status_code == 200:
        pedido = pedido_request.json()
        print(pedido)
        if int(pedido['comprador']) != int(user_id):
            messages.error(request, 'Você não tem permissão para cancelar este pedido.')
            print(f"não tem permissão \n pedido id: {pedido['comprador']} \n user id: {user_id}")
            return redirect('meus_pedidos')
        if pedido['status_pedido'] == 'Em andamento':
            pedido['status_pedido'] = 'Cancelado'
            pedido['status_pagamento'] = 'Cancelado'
            update_request = requests.put(API_ENDPOINT + f'pedidos/{pedido_id}/', data=pedido, headers=headers)
            if update_request.status_code == 200:
                messages.success(request, 'Pedido cancelado com sucesso.')
                print("pedido cancelado com sucesso")
            else:
                messages.error(request, 'Erro ao cancelar o pedido.')
                print("erro ao cancelar o pedido")
        else:
            messages.error(request, 'Somente pedidos em andamento podem ser cancelados.')
            print("somente em andamento podem ser cancelados")
    else:
        messages.error(request, 'Pedido não encontrado.')
        print("pedido nao encontrado")
    return redirect('meus_pedidos')
# Views antigas mantidas para compatibilidade
def login(request):
    return login_view(request)

def registerComprador(request):
    return register_comprador(request)