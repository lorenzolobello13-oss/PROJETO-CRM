import re
import streamlit as st
from database import login_user, obter_cliente_supabase
st.set_page_config(page_title="CRM - Login", layout="centered")

cliente = obter_cliente_supabase()

if ('usuario_existente' in st.session_state and st.session_state['usuario_existente'] is not None):
    st.title('Bem-vindo ao CRM!')
    st.write(f"Sessão iniciada como: **{st.session_state['usuario_existente']}**")

    if st.session_state.get('is_admin', False):
        st.info('Perfil: **Administrador**')
        st.info('Todas as permissões foram concedidas!')
    else:
        st.info('Perfil: **Usuário Comum**')

    if st.button('Terminar Sessão'):
        st.session_state['usuario_existente'] = None
        st.session_state['is_admin'] = False
        st.rerun()

else:
    st.title('CRM Login')
    st.markdown('Por favor, adicione as suas credenciais para ter acesso ao sistema.')

    email = st.text_input('E-mail:')
    senha = st.text_input('Senha:', type='password')
    st.info('-**-Sua senha deve conter caracteres especiais e números, com no mínimo 6 dígitos.**')
    btn_login = st.button('Entrar')

    if btn_login:
        if not email or not senha:
            st.warning('Preencha o e-mail e a senha.')
        else:
            try:
                usuario = login_user(email, senha)
                if usuario:
                    st.session_state['usuario_existente'] = usuario.email

                    user_metadata = getattr(usuario, 'user_metadata', {})
                    st.session_state['is_admin'] = user_metadata.get('is_admin', False)

                    st.success('Login efetuado com sucesso!')
                    st.rerun()
                else:
                    st.error('E-mail ou senha incorretos.')
            except Exception as e:
                st.error(f'E-mail ou senha incorretos: {e}.')

    with st.expander("Esqueceu a sua senha?"):
        if "email_rec_enviado" not in st.session_state:
            st.session_state["email_rec_enviado"] = False

        email_rec = st.text_input("E-mail da conta", key="email_rec_input")

        if st.button("Enviar e-mail de recuperação"):
            if not email_rec.strip():
                st.warning("Digite seu e-mail.")
            else:
                try:
                    cliente.auth.reset_password_email(email_rec.strip())
                    st.session_state["email_rec"] = email_rec.strip()
                    st.session_state["email_rec_enviado"] = True
                    st.success("Solicitação de recuperação enviada. Confira seu e-mail.")
                except Exception as e:
                    st.error(f"Erro ao enviar o e-mail de recuperação: {e}")

        if st.session_state["email_rec_enviado"]:
            st.info("Insira o código recebido e sua nova senha abaixo.")

            codigo_rec = st.text_input("Código recebido por e-mail", key="rec_codigo")
            nova_senha_rec = st.text_input("Digite a nova senha", type="password", key="rec_senha")
            nova_senha_rec_conf = st.text_input("Confirme a nova senha", type="password", key="rec_senha_conf")

            if st.button("Redefinir senha definitivamente"):
                if not codigo_rec or not nova_senha_rec or not nova_senha_rec_conf:
                    st.error("Preencha Todos os Campos.")
                    st.stop()

                if len(nova_senha_rec) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                    st.stop()

                if not re.search(r"[0-9]", nova_senha_rec):
                    st.error("A senha deve conter pelo menos um número.")
                    st.stop()

                if not re.search(r"[!@#$%¨&*(),.:{}<>]", nova_senha_rec):
                    st.error("A senha deve conter pelo menos um caractere especial.")
                    st.stop()

                if nova_senha_rec != nova_senha_rec_conf:
                    st.warning("As senhas não coincidem.")
                    st.stop()

                try:
                    cliente.auth.verify_otp({
                        "email": st.session_state["email_rec"],
                        "token": codigo_rec.strip(),
                        "type": "recovery",
                    })

                    cliente.auth.update_user({"password": nova_senha_rec})

                    st.session_state["email_rec_enviado"] = False
                    st.rerun()
                    st.success("Senha redefinida com sucesso!")

                except Exception as e:
                    st.error(f"Erro ao verificar o código ou atualizar a senha: {e}")


