import os 
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
def obter_cliente_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    cliente = create_client(url, key)
    
    if 'access_token' in st.session_state and st.session_state['access_token']:
        try:
            access_token = st.session_state['access_token']
            refresh_token = st.session_state.get('refresh_token')
            if access_token and refresh_token:
                # Define a sessão na autenticação
                cliente.auth.set_session(access_token, refresh_token)
                
                cliente.postgrest.auth(access_token)
                
        except Exception:
            st.session_state['access_token'] = None
            st.session_state['refresh_token'] = None
            st.session_state['usuario_existente'] = None
            
    return cliente
def login_user(email: str, password: str):
    try:
        cliente = obter_cliente_supabase()
        res = cliente.auth.sign_in_with_password({
            "email": email.strip().lower(),
            "password": password.strip()
        })
        
        if res.user:
            st.session_state['usuario_existente'] = res.user.email
            st.session_state['access_token'] = res.session.access_token
            st.session_state['refresh_token'] = res.session.refresh_token
            return res.user
      
            
    except Exception as e:
        st.error(f"Erro técnico detalhado: {str(e)}")
        return None



def saida_user():
    try:
        cliente = obter_cliente_supabase()
        cliente.auth.sign_out()
    except Exception:
        pass
    
    st.session_state['access_token'] = None
    st.session_state['refresh_token'] = None
    st.session_state['usuario_existente'] = None
    st.session_state['is_admin'] = False







    