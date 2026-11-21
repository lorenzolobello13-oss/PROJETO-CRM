<div align="center">

# 📊 CRM & Gestão de Contratos

Sistema multi-página de gestão de clientes, contratos,perfis e métricas financeiras (MRR), construído com foco em segurança de dados, controle de acesso e visualização analítica.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Brevo](https://img.shields.io/badge/Brevo-0B996E?style=for-the-badge&logo=brevo&logoColor=white)

</div>

---

## 🎯 Sobre o Projeto

Este CRM foi desenvolvido para centralizar o ciclo de vida de clientes, contratos recorrentes e acompanhamento de escopos técnicos. A aplicação une uma interface interativa em **Streamlit** com um backend gerenciado no **Supabase**,
garantindo isolamento de dados por usuário através de políticas de **Row-Level Security (RLS)** e UUID.

---

## ✨ Funcionalidades

- **Autenticação & Controle de Acesso:** Login e recuperação de senha e separação de permissões entre administradores e usuários padrão via Supabase Auth.
- **Gestão de Clientes e Contratos:** Cadastro, edição, listagem e busca dinâmica em tempo real com filtragem instantânea.
- **Dashboard de MRR:** Visualização interativa da receita recorrente mensal e indicadores de desempenho construídos com Plotly e Pandas.
- **Gestão de Escopos:** Controle dedicado de escopos de projetos/agentes vinculados a cada contrato de forma isolada para cada cliente.
- **Isolamento de Dados (RLS):** Políticas baseadas em `owner_id` (UUID) assegurando que cada usuário acesse apenas os registros autorizados.
- **Recuperar Senha:** Enviamos um E-mail com a utilização do brevo, com um código para confirmação de usuário.
- **Admnistração:** Apenas outros administradores podem criar outros utilizadores. 

---

## 🏗️ Arquitetura e Segurança

```text
├── app.py                  # Ponto de entrada e roteamento principal
├── pages/                  # Páginas da aplicação (Dashboard, Clientes, Contratos, Escopos)
├── services/               # Conexão com Supabase e regras de negócio
├── utils/                  # Validações de entrada, formatação e helpers
├── assets/                 # Capturas de tela e recursos visuais do README
├── .env.example            # Modelo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados no versionamento
└── requirements.txt        # Dependências do projeto
```

---

##📦 Como executar / Clonar repositório

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/lorenzolobello13-oss/PROJETO-CRM.git
   cd PROJETO-CRM
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   Copie o `.env.example` para `.env` e preencha as credenciais do Supabase e do Brevo:
   ```bash
   cp .env.example .env
   ```

5. **Execute a aplicação:**
   ```bash
   streamlit run app.py
   ```
