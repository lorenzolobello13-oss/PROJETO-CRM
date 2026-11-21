import streamlit as st
import pandas as pd
from database import obter_cliente_supabase

st.set_page_config(page_title="Gestão de Clientes", layout="wide")

st.title("Gestão de Clientes")

if 'usuario_existente' not in st.session_state or st.session_state['usuario_existente'] is None:
    st.warning("⚠️ Faça login na página principal para ter acesso a esta seção.")
    st.stop()
    
cliente = obter_cliente_supabase()

email_atual = st.session_state['usuario_existente']
st.info(f'Login Atual: ** {email_atual} **')

@st.cache_data(ttl=5)
def carregar_clientes():
    cliente_db = obter_cliente_supabase()
    resposta = cliente_db.table("clientes").select("*").execute()
    return resposta.data if resposta.data else []

tab1, tab2 = st.tabs(["📋 Adicionar Cliente", "✏️ Editar Cliente Existente"])

with tab1:
    with st.form("form_cliente"):
        razao_social = st.text_input("Razão Social").strip().lower()
        cnpj = st.text_input("CNPJ (Apenas números):").strip().lower()
        email = st.text_input("E-mail:").strip().lower()
        telefone = st.text_input("Telefone:").strip().lower()
        contato_nome = st.text_input("Nome para contato:").strip().lower()
        btn_guardar = st.form_submit_button("Guardar Cliente")
        
        caracteres_especiais = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "=", "[", "]", "{", "}", "|", ";", ":", "'", "\"", ",", ".", "/", "<", ">"]

        if btn_guardar:
            if cnpj and any(char in caracteres_especiais for char in cnpj):
                st.warning("⚠️ O CNPJ deve conter apenas números, sem letras ou carateres especiais.")
            elif not razao_social or not email or not contato_nome or not telefone or not cnpj:
                st.warning("Todos os campos são obrigatórios.")
            elif len(cnpj) != 14:
                st.warning("O CNPJ deve conter 14 números.")
            elif len(telefone) != 11:
                st.warning("O Telefone deve conter 11 números.")
            elif not '@gmail.com' in email and not '@outlook.com' in email and not '@yahoo.com' in email:
                st.error("ERRO: por favor digite seu e-mail novamente")
            else:
                cnpj_limpo = "".join(filter(str.isdigit, cnpj)) if cnpj else ""

                novo_cliente = {
                    "razao_social": razao_social,
                    "cnpj": cnpj,
                    "email": email,
                    "telefone": telefone,
                    "contato_nome": contato_nome,
                    "ativo": True,
                }
                
                try:
                    cliente.table("clientes").insert(novo_cliente).execute()
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar cliente: {e}")

    st.markdown("---")
    st.subheader("Lista de Clientes e Gestão de Estado")

    try:
        resposta = cliente.table("clientes").select("*").execute()
        if resposta.data:
            df_clientes = pd.DataFrame(resposta.data)
            
            for index, row in df_clientes.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{row['razao_social']}** (CNPJ: {row.get('cnpj', '-')})")
                with col2:
                    ativo_atual = row.get('ativo', True)
                    estado_str = "Ativo 🟢" if ativo_atual else "Inativo 🔴"
                    st.write(f"Estado: {estado_str}")
               
                with col3:
                    if ativo_atual:
                        if st.button("Desativar", key=f"desat_{row['id']}"):
                            cliente.table("clientes").update({"ativo": False}).eq("id", row['id']).execute()
                            st.success("Cliente desativado!")
                            st.rerun()
                    else:
                        if st.button("Ativar", key=f"ativ_{row['id']}"):
                            cliente.table("clientes").update({"ativo": True}).eq("id", row['id']).execute()
                            st.success("Cliente ativado!")
                            st.rerun()
        else:
            st.info("Nenhum cliente registado para a sua conta.")
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")
with tab2:
    st.subheader("Editar Clientes Existentes")
    meus_clientes = cliente.table("clientes").select("*").execute()
    existente = meus_clientes.data

    if not existente:
        st.info("Ainda não existem clientes registados para a sua conta.")
    else:
        clientes_dict = {f"{c.get('razao_social', '')} ({c.get('cnpj', '')})": c  for c in existente}

        termo_busca = st.text_input("🔍 Buscar Meus Clientes Pela Razão social ou cnpj").strip().lower()

        opcoes_filtradas = [
            rotulo for rotulo in clientes_dict.keys()
            if termo_busca in rotulo.lower()
        ]

        if not opcoes_filtradas:
            st.warning("Nenhum cliente encontrado com esse filtro.")
        else:
            with st.form("form_editar_cliente"):
                cliente_selecionado = st.selectbox(
                    "Clientes encontrados",
                    options=opcoes_filtradas)
                dados_atuais = clientes_dict[cliente_selecionado]

                novo_razao = st.text_input( "Razão Social",value=dados_atuais.get("razao_social", "")).strip().lower()
                novo_cnpj = st.text_input("CNPJ (Apenas números):",value=dados_atuais.get("cnpj", "")).strip().lower()
                novo_email = st.text_input("E-mail:",value=dados_atuais.get("email", "")).strip().lower()
                novo_telefone = st.text_input("Telefone:",value=dados_atuais.get("telefone", "")).strip().lower()
                novo_contato = st.text_input("Nome para contato:",value=dados_atuais.get("contato_nome", "")).strip().lower()
                ativo_atual = bool(dados_atuais.get("ativo", True))
                novo_ativo = st.checkbox("Cliente Ativo", value=ativo_atual)

                atualizar_clientes = st.form_submit_button("Atualizar Cliente")

                if atualizar_clientes:
                    if novo_cnpj and any(char in caracteres_especiais for char in novo_cnpj):
                        st.warning("⚠️ O CNPJ deve conter apenas números, sem letras ou carateres especiais.")
                    if novo_telefone and any(char in caracteres_especiais for char in telefone):
                        st.warning("Digite Apenas Números em Telefone")
    
                    elif not novo_razao or not novo_email or not novo_contato or not novo_telefone or not novo_cnpj:
                        st.warning("Todos os campos são obrigatórios.")
                    elif len(novo_cnpj) != 14:
                        st.warning("O CNPJ deve conter 14 números.")
                    elif len(novo_telefone) != 11:
                        st.warning("O Telefone deve conter 11 números.")
                    elif (
                        "@gmail.com" not in novo_email
                        and "@outlook.com" not in novo_email
                        and "@yahoo.com" not in novo_email
                    ):
                        st.error("ERRO: por favor digite seu e-mail novamente")
                    else:
                        novo_cnpj_limpo = "".join(filter(str.isdigit, novo_cnpj)) if novo_cnpj else ""

                        edit_client = {
                            "razao_social": novo_razao,
                            "cnpj": novo_cnpj_limpo,
                            "email": novo_email,
                            "telefone": novo_telefone,
                            "contato_nome": novo_contato,
                            "ativo": novo_ativo,
                        }
                        try:
                            cliente.table("clientes").update(edit_client).eq("id", dados_atuais["id"]).execute()
                            st.success("Cliente atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar cliente: {e}")
                
        

        
