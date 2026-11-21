import streamlit as st
import pandas as pd
from datetime import date
from database import obter_cliente_supabase

st.set_page_config(page_title="Gestão de Contratos de IA", layout="wide")
cliente = obter_cliente_supabase()
if 'usuario_existente' not in st.session_state or st.session_state['usuario_existente'] is None:
    st.warning("⚠️ Faça login na página principal para ter acesso a esta seção.")
    st.stop()

email_atual = st.session_state['usuario_existente']

st.title("📝 Gestão de Contratos e Especificação de Agentes")



tab1, tab2, tab3= st.tabs(['Registrar contratos', 'Editar contratos' , 'Editar Escopo de Agentes'])
with tab1:
    st.subheader("🔔 Alertas de Vencimentos Próximos")
    
    resposta_contratos = cliente.table("contratos").select("*, clientes(razao_social)").execute()
    
    if resposta_contratos.data:
        df_contratos = pd.DataFrame(resposta_contratos.data)
    
        df_contratos['data_fim'] = pd.to_datetime(df_contratos['data_fim'], errors='coerce').dt.date
        df_contratos = df_contratos.dropna(subset=['data_fim'])
    
        hoje = date.today()
        df_contratos['dias_restantes'] = (pd.to_datetime(df_contratos['data_fim']) - pd.to_datetime(hoje)).dt.days
    
        vencidos = df_contratos[df_contratos['dias_restantes'] < 0]
        criticos = df_contratos[(df_contratos['dias_restantes'] >= 0) & (df_contratos['dias_restantes'] <= 7)]
        atencao = df_contratos[(df_contratos['dias_restantes'] > 7) & (df_contratos['dias_restantes'] <= 30)]
    
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            if not vencidos.empty:
                st.error(f"⚠️ **{len(vencidos)}** contrato(s) já vencidos!")
            else:
                st.success("Sem contratos vencidos.")
        with col_a2:
            if not criticos.empty:
                st.warning(f"🔔 **{len(criticos)}** vencem nos próximos **7 dias**!")
            else:
                st.info("Sem urgências de 7 dias.")
        with col_a3:
            if not atencao.empty:
                st.info(f"ℹ️ **{len(atencao)}** vencem entre **15 e 30 dias**.")
            else:
                st.info("Sem alertas para 30 dias.")
    else:
        st.info("Sem dados de contratos registados para a sua conta.")
    
    st.markdown("---")

    st.subheader("Novo Contrato & Parâmetros do Agente de IA")

    resposta_clientes = cliente.table("clientes").select("id, razao_social").execute()
    clientes_dict = {c['razao_social']: c['id'] for c in resposta_clientes.data} if resposta_clientes.data else {}

    with st.form("form_contrato_escopo"):
        st.markdown("#### Dados do Contrato")
        c1, c2 = st.columns(2)
        with c1:
            cliente_selecionado = st.selectbox("Cliente", options=list(clientes_dict.keys())  if clientes_dict else ["Registre um cliente primeiro"])
            titulo_projeto = st.text_input("Título do Projeto")
            status = st.selectbox("Status do Contrato", options=["Ativo", "Renovação Pendente", "Cancelado","em implantçáo"])
        with c2:
            valor_mensal = st.number_input("Valor Mensal (MRR R$)", min_value=0.0, format="%.2f")
            data_inicio = st.date_input("Data de Início", value=date.today())
            data_fim = st.date_input("Data de Término / Vigência", value=date.today())
            custo_setup = st.number_input("Custo de Setup")

        st.markdown("---")
        st.markdown("#### Especificação do Escopo do Agente (Parâmetros Técnicos)")
        e1, e2 = st.columns(2)
        with e1:
            tipo_arquitetura = st.selectbox("Tipo de Arquitetura", options=["RAG com LLM", "Agente Autónomo", "Fine-Tuning Especializado", "Automação de Processos"])
            limite_requisicoes = st.number_input("Limite de Requisições / Limite de Tokens")
            limite_tokens = st.number_input("Limite de Tokens por Operação:")
        with e2:
            horas_manutencao = st.number_input("Horas de Suporte / Manutenção", min_value=1, value=5)
            modelos_permitidos = st.text_input("Modelos Permitidos (ex: GPT-4o, Claude 3.5 Sonnet)", value="GPT-4o")
            sla_horas = st.number_input("SLA de Resposta em Horas", min_value=1, value=24)

        btn_guardar_tudo = st.form_submit_button("Guardar meu Contrato e Escopo")
        campo_obg =[
            titulo_projeto,
            custo_setup,
            modelos_permitidos,
            limite_tokens
        ]
        if btn_guardar_tudo:
            if not all(campo_obg):
                st.warning("Preencha os campos obrigatórios ou selecione um cliente válido.")
            elif valor_mensal < 1000: 
                st.error("O valor do MRR deve ser maior que 1000 R$.") 
            else:
                cliente_id = clientes_dict[cliente_selecionado]
                novo_contrato = {
                    "cliente_id": cliente_id,
                    "titulo_projeto": titulo_projeto,
                    "status": status,
                    "valor_mensal": valor_mensal,
                    "data_inicio": str(data_inicio),
                    "data_fim": str(data_fim),
                    "custo_setup": custo_setup
                }
                try:
                    st.title("Detalhes do Escopo de Agentes")
                    res_contrato = cliente.table("contratos").insert(novo_contrato).execute()
                    st.write("1) contrato:", res_contrato.data)

                    if not res_contrato.data:
                        st.error("O contrato não retornou dados (provável RLS bloqueando INSERT/SELECT em 'contratos').")
                        st.stop()

                    contrato_criado_id = res_contrato.data[0]['id']

                    novo_escopo = {
                        "contrato_id": contrato_criado_id,
                        "tipo_arquitetura": tipo_arquitetura,
                        "limite_requisicoes": int(limite_requisicoes),
                        "horas_manutencao": int(horas_manutencao),
                        "modelos_permitidos": [m.strip() for m in modelos_permitidos.split(",")],
                        "limite_tokens": int(limite_tokens),
                        "sla_horas": int(sla_horas),
                    }
                    st.write("2) enviando escopo:", novo_escopo)

                    res_escopo = cliente.table("escopo_agentes").insert(novo_escopo).execute()
                    st.write("3) escopo:", res_escopo.data)

                    if not res_escopo.data:
                        st.error("O escopo não foi gravado (verifique RLS de INSERT em 'escopo_agentes').")
                        st.stop()

                    st.success("Contrato e especificações do agente guardados com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao registar contrato: {e}")
with tab2:
    st.subheader("Editar contratos existentes")

    meus_contratos = cliente.table("contratos").select("*, clientes(razao_social)").execute()
    existente = meus_contratos.data if meus_contratos.data else []
    
    if not existente:
        st.info("Ainda não existem contratos registados para a sua conta.")
    else:
        buscar_contratos = st.text_input("🔍 Pesquisar Contrato (Digite o Título do Projeto ou Razão Social do Cliente):").strip().lower()
    
        if buscar_contratos:
            contratos_filtrados = [
                c for c in existente 
                if buscar_contratos in (c.get('titulo_projeto') or '').lower() 
                or buscar_contratos in (c.get('clientes') or {}).get('razao_social', '').lower()
            ]
            st.write(f"Apenas **{len(contratos_filtrados)}** contrato(s) encontrado(s) para a pesquisa: '{buscar_contratos}'")
        else:
            contratos_filtrados = existente

        if contratos_filtrados:
            contratos_dict = {c['titulo_projeto']: c for c in contratos_filtrados}
            
            contrato_selecionado = st.selectbox("Contratos", options=list(contratos_dict.keys()))
            dados_atuais = contratos_dict.get(contrato_selecionado, {})
            
            with st.form("form_editar_contrato"):
                novo_titulo_projeto = st.text_input("Título do Projeto para Editar", value=dados_atuais.get("titulo_projeto", "")).strip()
                status_opcoes = ["Ativo", "Renovação Pendente", "Cancelado", "em implantação"]
                status_atual = dados_atuais.get("status", "Ativo")
                status_index = status_opcoes.index(status_atual) if status_atual in status_opcoes else 0
                novo_status = st.selectbox("Status do Contrato", options=status_opcoes, index=status_index)
                novo_mrr = st.number_input("Novo Valor Mensal (MRR R$)", min_value=0.0, value=float(dados_atuais.get("valor_mensal", 0.0)), format="%.2f")
                
                try:
                    data_ini_val = date.fromisoformat(dados_atuais.get("data_inicio")) if dados_atuais.get("data_inicio") else date.today()
                except:
                    data_ini_val = date.today()
                    
                try:
                    data_fim_val = date.fromisoformat(dados_atuais.get("data_fim")) if dados_atuais.get("data_fim") else date.today()
                except:
                    data_fim_val = date.today()

                nova_data_inicio = st.date_input("Nova Data de Início", value=data_ini_val)
                nova_data_fim = st.date_input("Nova Data de Término / Vigência", value=data_fim_val)
                nova_arquitetura = st.text_input("Tipo de Arquitetura", value=dados_atuais.get("tipo_arquitetura", "")).strip()
                novo_custo = st.number_input("Digite o custo de Setup", value=float(dados_atuais.get("custo-setup", 0.0)))
                
                atualizar_contrato = st.form_submit_button("Atualizar Contrato")
                
                if atualizar_contrato:
                    campos_obg = [novo_titulo_projeto, novo_mrr, nova_arquitetura, novo_custo]
                    
                    if not all(campos_obg):
                        st.error("Campos Obrigatórios Estão Faltando!")
                    else:
                        edit_contrato = {
                            "cliente_id": dados_atuais.get("cliente_id"),
                            "titulo_projeto": novo_titulo_projeto,
                            "status": novo_status,
                            "data_inicio": str(nova_data_inicio),
                            "data_fim": str(nova_data_fim),
                            "valor_mensal": novo_mrr,
                            "custo_setup": novo_custo
                        }
                        try:
                            cliente.table("contratos").update(edit_contrato).eq("id", dados_atuais["id"]).execute()
                            st.success("Contrato Atualizado Com Sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Não foi possível atualizar o contrato: {e}")

with tab3:
    st.subheader("Editar Escopo do Agente")

    meus_contratos_escopo = cliente.table("contratos").select("*, clientes(razao_social)").execute()
    contratos_disponiveis = meus_contratos_escopo.data if meus_contratos_escopo.data else []

    if not contratos_disponiveis:
        st.info("Ainda não existem contratos cadastrados para vincular ou editar um escopo.")
    else:
        termo_escopo = st.text_input(
            "🔍 Buscar escopo (por título do contrato, cliente, arquitetura ou ID)",
            placeholder="Ex.: Agente de Suporte, Empresa X, RAG com LLM ou ID...",
            key="busca_escopo",
        ).strip().lower()

        contratos_escopo_filtrados = []
        for c in contratos_disponiveis:
            titulo = (c.get("titulo_projeto") or "").lower()
            cliente_nome = ((c.get("clientes") or {}).get("razao_social") or "").lower()
            arq_contrato = (c.get("tipo_arquitetura") or "").lower()
            contrato_id = str(c.get("id") or "").lower()

            if (
                not termo_escopo
                or termo_escopo in titulo
                or termo_escopo in cliente_nome
                or termo_escopo in arq_contrato
                or termo_escopo in contrato_id
            ):
                contratos_escopo_filtrados.append(c)

        if not contratos_escopo_filtrados:
            st.warning("Nenhum escopo/contrato encontrado com esse termo de pesquisa.")
        else:
            st.caption(f"{len(contratos_escopo_filtrados)} opção(ões) encontrada(s).")

            escopos_dict = {
                f"{c.get('titulo_projeto', 'Sem título')} — {(c.get('clientes') or {}).get('razao_social', 'Sem cliente')} (#{c['id']})": c
                for c in contratos_escopo_filtrados
            }

            escopo_selecionado_label = st.selectbox(
                "Selecione o escopo/contrato para editar",
                options=list(escopos_dict.keys()),
                key="select_escopo",
            )
            contrato_alvo = escopos_dict[escopo_selecionado_label]
            contrato_alvo_id = contrato_alvo["id"]

            res_escopo_atual = (
                cliente.table("escopo_agentes")
                .select("*")
                .eq("contrato_id", contrato_alvo_id)
                .limit(1)
                .execute()
            )
            escopo_atual = res_escopo_atual.data[0] if res_escopo_atual.data else {}

            with st.form("form_editar_escopo"):
                opcoes_arq = [
                    "RAG com LLM",
                    "Agente Autônomo",
                    "Fine-Tuning Especializado",
                    "Automação de Processos",
                ]
                arq_atual = escopo_atual.get("tipo_arquitetura") or contrato_alvo.get("tipo_arquitetura") or "RAG com LLM"
                arq_idx = opcoes_arq.index(arq_atual) if arq_atual in opcoes_arq else 0

                nova_arquitetura = st.selectbox("Tipo de Arquitetura", options=opcoes_arq, index=arq_idx)
                novo_limite_requisicoes = st.number_input(
                    "Limite de Requisições",
                    min_value=0,
                    value=int(escopo_atual.get("limite_requisicoes") or 0),
                )
                nova_horas_manutencao = st.number_input(
                    "Horas de Manutenção",
                    min_value=0,
                    value=int(escopo_atual.get("horas_manutencao") or 0),
                )
                novo_limite_tokens = st.number_input(
                    "Limite de Tokens",
                    min_value=0,
                    value=int(escopo_atual.get("limite_tokens") or 0),
                )

                modelos_raw = escopo_atual.get("modelos_permitidos") or []
                modelos_str_inicial = (
                    ", ".join(modelos_raw) if isinstance(modelos_raw, list) else str(modelos_raw)
                )
                novo_modelo = st.text_input(
                    "Modelos Permitidos (separe por vírgulas)",
                    value=modelos_str_inicial,
                )

                sla_horas = st.number_input(
                    "SLA de Resposta (em horas)",
                    min_value=0,
                    value=int(escopo_atual.get("sla_horas") or 0),
                )

                atualizar_escopo = st.form_submit_button("Atualizar Escopo")

                if atualizar_escopo:
                    modelos_lista = [m.strip().lower() for m in novo_modelo.split(",") if m.strip()]
                    if not modelos_lista:
                        st.error("Informe ao menos um modelo permitido.")
                    if not sla_horas or not novo_modelo or novo_limite_requisicoes or novo_limite_tokens or not nova_horas_manutencao:
                        st.warning("Preencha todos os campos!")
                    else:
                        dados_atualizados = {
                            "tipo_arquitetura": nova_arquitetura,
                            "limite_requisicoes": int(novo_limite_requisicoes),
                            "horas_manutencao": int(nova_horas_manutencao),
                            "sla_horas": int(sla_horas),
                            "limite_tokens": int(novo_limite_tokens),
                            "modelos_permitidos": modelos_lista,
                        }
                        try:
                            if escopo_atual:
                                cliente.table("escopo_agentes").update(dados_atualizados).eq("contrato_id", contrato_alvo_id).execute()
                            else:
                                dados_atualizados["contrato_id"] = contrato_alvo_id
                                cliente.table("escopo_agentes").insert(dados_atualizados).execute()
                            st.success("Escopo atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar escopo: {e}")