import streamlit as st
import pandas as pd
import plotly.express as px
from database import obter_cliente_supabase

st.set_page_config(page_title="Dashboard - CRM", layout="wide")

if 'usuario_existente' not in st.session_state or st.session_state['usuario_existente'] is None:
    st.warning("⚠️ faça login na página principal para ter acesso a esta seção.")
    st.stop()
supabase = obter_cliente_supabase()

st.title("📊 Dashboard Executivo (MRR e Contratos)")
st.write(f"Bem-vindo, **{st.session_state['usuario_existente']}**")
st.markdown("---")

@st.cache_data(ttl=6)
def carregar_dados_dashboard():
    resposta = supabase.table("contratos").select("status, valor_mensal, titulo_projeto, data_fim, clientes(razao_social)").execute()
    
    return resposta.data if resposta.data else []

try:
    dados = carregar_dados_dashboard()
    
    if dados:
        df = pd.DataFrame(dados)
    
        if 'clientes' in df.columns:
            df['empresa'] = df['clientes'].apply(lambda x: x.get('razao_social', 'Desconhecido') if isinstance(x, dict) else 'Desconhecido')
        else:
            df['empresa'] = 'Desconhecido'

        df['valor_mensal'] = pd.to_numeric(df['valor_mensal'], errors='coerce').fillna(0.0)
        df['status_limpo'] = df['status'].astype(str).str.strip()
    
        total_contratos = len(df)
        mrr_total = df[df['status_limpo'].str.lower() == 'ativo']['valor_mensal'].sum()
        
        ativos = len(df[df['status_limpo'].str.lower() == 'ativo'])
        implantacao = len(df[df['status_limpo'].str.contains('implantação|implantacao', case=False, na=False)])
        pendentes = len(df[df['status_limpo'].str.contains('pendente', case=False, na=False)])
        cancelados = len(df[df['status_limpo'].str.contains('cancelado|encerrado', case=False, na=False)])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Contratos Totais", total_contratos)
        c2.metric("MRR Ativo (Mensal)", f"{mrr_total:,.2f} R$")
        c3.metric("Ativos 🟢", ativos)
        c4.metric("Outros / Em Curso", implantacao + pendentes)

        st.markdown("---")
    
        st.subheader("💼 Receita por Empresa e Contrato")
        
        if not df.empty:
            fig = px.bar(
                df,
                x='titulo_projeto',
                y='valor_mensal',
                color='status',
                text='valor_mensal',
                barmode='group',
                labels={'valor_mensal': 'Lucro / Valor Mensal (R$)', 'titulo_projeto': 'Projeto', 'status': 'Status'}
            )
            
            fig.update_traces(texttemplate='%{text:,.2f} R$', textposition='outside')
            fig.update_layout(
                xaxis_title="Projeto",
                yaxis_title="Valor Mensal (R$)",
                template="plotly_dark",
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width='stretch')

        st.markdown("---")
    
        st.subheader("🏢 Detalhe das Empresas e Valores por Estado")
        col_d1, col_d2, col_d3 = st.columns(3)

        with col_d1:
            st.markdown("### 🟢 Ativos")
            df_atv = df[df['status_limpo'].str.lower() == 'ativo']
            if not df_atv.empty:
                st.caption(f"Subtotal: **{df_atv['valor_mensal'].sum():,.2f} R$**")
                for _, row in df_atv.iterrows():
                    st.info(f"**{row['empresa']}**\n\n*Projeto:* {row['titulo_projeto']}\n\n*MRR:* **{row['valor_mensal']:,.2f} R$**")
            else:
                st.write("Nenhum contrato ativo.")

        with col_d2:
            st.markdown("### 🔵 Em Implantação / Pendentes")
            df_outros = df[df['status_limpo'].str.contains('implantação|implantacao|pendente', case=False, na=False)]
            if not df_outros.empty:
                st.caption(f"Subtotal: **{df_outros['valor_mensal'].sum():,.2f} R$**")
                for _, row in df_outros.iterrows():
                    st.warning(f"**{row['empresa']}**\n\n*Projeto:* {row['titulo_projeto']} (*{row['status']}*)\n\n*MRR:* **{row['valor_mensal']:,.2f} R$**")
            else:
                st.write("Nenhum em implantação ou pendente.")

        with col_d3:
            st.markdown("### 🔴 Cancelados / Encerrados")
            df_canc = df[df['status_limpo'].str.contains('cancelado|encerrado', case=False, na=False)]
            if not df_canc.empty:
                st.caption(f"Subtotal: **{df_canc['valor_mensal'].sum():,.2f} R$**")
                for _, row in df_canc.iterrows():
                    st.error(f"**{row['empresa']}**\n\n*Projeto:* {row['titulo_projeto']}\n\n*MRR:* **{row['valor_mensal']:,.2f} R$**")
            else:
                st.write("Nenhum cancelado ou encerrado.")

    else:
        st.info(f"Ainda não existem contratos registados para a sua conta para gerar métricas. ")

except Exception as e:
    st.error(f"Erro ao carregar o dashboard: {e}")