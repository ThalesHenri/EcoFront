# Frontend Django (HTML + CSS)

Este projeto é um **frontend** desenvolvido em **Django**, utilizando apenas **HTML** e **CSS puro** para estilização, sem uso de frameworks como Bootstrap ou Tailwind.

## 📌 Requisitos

- Python 3.10+
- Django 4+
- Pip (gerenciador de pacotes)

## 🚀 Como executar o projeto

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo

    Crie e ative um ambiente virtual

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

Instale as dependências

pip install -r requirements.txt

Execute as migrações

python manage.py migrate

Inicie o servidor

python manage.py runserver

Acesse no navegador

    http://127.0.0.1:8000/

📂 Estrutura de pastas

.
├── app/                # Aplicação Django principal
│   ├── templates/      # Arquivos HTML
│   └── static/         # Arquivos CSS, imagens e JS (se necessário)
├── manage.py
├── requirements.txt
└── README.md

🎨 Estilo

    HTML: Estrutura semântica e responsiva.

    CSS puro: Organização em múltiplos arquivos quando necessário.

    Boas práticas: Classes reutilizáveis, comentários e indentação padronizada.

📜 Licença

Este projeto está licenciado sob a licença MIT
