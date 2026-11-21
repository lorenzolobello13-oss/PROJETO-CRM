import streamlit as st 
import re
from database import obter_cliente_supabase

st.set_page_config(page_title="CRM - Configurações", layout="centered")

if not st.session_state.get('usuario_existente'):
    st.warning("**Atenção:** Você precisa de um e-mail para ter acesso a esta página.")
    st.stop()

usuario_atual = st.session_state['usuario_existente']
is_admin = st.session_state.get('is_admin', False)

cliente = obter_cliente_supabase()
st.title("Configurações do Sistema")

if is_admin:
    st.markdown("Gerencie os membros da equipe e as configurações de segurança.")

    tab1, tab2 = st.tabs(['Cadastrar novo utilizador','Cadastrar Novo Administrador'])

    with tab1:
        st.subheader("Adicionar Novo Utilizador") 
        with st.form("form_auth", clear_on_submit=True):
            novo_email = st.text_input("Novo E-mail:")
            nova_senha = st.text_input('Nova senha:', type='password')
            senha_confirmar = st.text_input("Confirmar senha", type='password')
            btn_cadastrar = st.form_submit_button("Criar Conta")
            
            if btn_cadastrar: 
                if '@' not in novo_email or '.' not in novo_email:
                    st.error("ERRO: O e-mail deve conter (@) e um domínio válido.")
                elif nova_senha != senha_confirmar:
                    st.warning("ERRO: As senhas estão diferentes!")
                elif not re.search(r'[!@#$%¨&*(),.:{}\<>]', nova_senha) or not re.search(r'[0-9]', nova_senha):
                    st.error("Erro! A senha deve conter caracteres especiais e números.")
                elif len(nova_senha) < 6:
                    st.error("Erro: A senha deve conter pelo menos 6 dígitos.")
                else:
                    try:
                        resp = cliente.auth.sign_up({"email": novo_email, "password": nova_senha})  
                        st.success("Conta criada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao Registrar Nova Conta: {e}")
        
    with tab2:
        st.subheader('**CADASTRAR NOVO ADMINISTRADOR**')
        st.info('**Atenção:** Contas administradoras tem acesso total a todo o sistema.')
        
        with st.form("form_novo_admin", clear_on_submit=True):
            novo_adm = st.text_input("Novo E-mail (Admin):")
            nova_senha_adm = st.text_input('Nova senha (Admin):', type='password')
            senha_confirmar_adm = st.text_input("Confirmar senha (Admin)", type='password')
            btn_cadastrar_adm = st.form_submit_button("Criar Administrador")
            
            if btn_cadastrar_adm:
                if not novo_adm or not nova_senha_adm or not senha_confirmar_adm:
                    st.error("ERRO: Todos os campos devem ser preenchidos!")
                elif '@' not in novo_adm or '.' not in novo_adm:
                    st.error("ERRO: O e-mail deve conter (@) e um domínio válido.")
                elif nova_senha_adm != senha_confirmar_adm:
                    st.warning("ERRO: As senhas estão diferentes!")
                elif not re.search(r'[!@#$%¨&*(),.:{}\<>]', nova_senha_adm) or not re.search(r'[0-9]', nova_senha_adm):
                    st.error("Erro! A senha deve conter caracteres especiais e números.")
                elif len(nova_senha_adm) < 6:
                    st.error("Erro: A senha deve conter pelo menos 6 dígitos.")
                else:
                    try:
                        resp = cliente.auth.sign_up({"email": novo_adm, "password": nova_senha_adm, "options": {"data": {"is_admin": True}}})  
                        st.success("Administrador criado com sucesso!")
                    except Exception as e:
                        st.error(f'Erro ao registrar administrador: {e}')

else:
    st.markdown("Gerencie as definições da sua conta.")
    st.subheader('Alteração de senha da sua conta')
    st.info(f'Sessão ativa para: **{usuario_atual}**')

    
