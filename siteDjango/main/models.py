from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    TIPO_USUARIO_ESCOLHAS = [
        ('Comprador', 'Comprador'),
        ('Vendedor', 'Vendedor'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO_ESCOLHAS, default='Comprador')
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS = ['username','tipo']
    
    def __str__(self):
        return f"{self.username} >> {self.tipo}"
    

class Comprador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='comprador',default=None)
    nome = models.CharField(max_length=100,default='Sem Nome')
    telefone = models.CharField(max_length=15,default='Sem Telefone')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} (Comprador)"

class Vendedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendedor',default=None)
    nome_empresa = models.CharField(max_length=100)
    representante = models.CharField(max_length=100,default='Sem representante')
    telefone = models.CharField(max_length=15,default='Sem Telefone')
    cnpj = models.CharField(max_length=20, unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_empresa

class Pacote(models.Model):
    CATEGORIA_CHOICES = [
        ('Salgada', 'Salgada'),
        ('Mista', 'Mista'),
        ('Doce', 'Doce'),
    ]
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    nome_pacote = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    descricao = models.TextField()
    quant_disponivel = models.IntegerField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    def __str__(self):
        return self.nome_pacote

class Pedido(models.Model):
    STATUS_PAGAMENTO_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Aprovado', 'Aprovado'),
        ('Cancelado', 'Cancelado'),
        ('Entregue', 'Entregue'),
    ]
    STATUS_PEDIDO_CHOICES = [
        ('Em andamento', 'Em andamento'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado'),
    ]
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE)
    pacote = models.ForeignKey(Pacote, on_delete=models.CASCADE)
    status_pagamento = models.CharField(choices= STATUS_PAGAMENTO_CHOICES,max_length=20, default='Pendente')
    preco_total = models.DecimalField(max_digits=8, decimal_places=2)
    status_pedido = models.CharField(choices=STATUS_PEDIDO_CHOICES, max_length=20, default='Em andamento')
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.pk}"

class Pagamento(models.Model):
    PAGAMENTO_CHOICES = [('Cartão de Crédito', 'Cartão de Crédito'),
                         ('Boleto', 'Boleto'),
                         ('Pix', 'Pix')]
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(Comprador, on_delete=models.CASCADE)
    status_pagamento = models.CharField(max_length=50)
    data_compra = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=50,choices=PAGAMENTO_CHOICES)

    def __str__(self):
        return f"Pagamento #{self.pk} - Pedido #{self.pedido.pk}"

class Avaliacao(models.Model):
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    avaliacao = models.PositiveSmallIntegerField()  # 1 a 10
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.vendedor} por {self.comprador}"