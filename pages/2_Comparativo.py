import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="KAIROS V2 | Comparativo SAEB", layout="wide")

# --- CSS DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #12161D !important; border-right: 2px solid #FACC15; }
    [data-testid="stMetric"] { 
        background-color: #161B22 !important; 
        border: 1px solid #30363D !important;
        border-radius: 10px; 
    }
    /* Estilização específica para os cards de disciplina */
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

def classificar_nivel_saeb(nota):
    if nota < 175: return "Muito Baixo"
    elif nota < 225: return "Básico"
    elif nota < 275: return "Adequado"
    else: return "Avançado"

# --- INTERFACE ---
st.title("🔄 KAIROS V2 | Painel Comparativo de Disciplinas")

with st.sidebar:
    st.markdown("### 📂 Upload de Dados")
    uploaded_files = st.file_uploader("Carregar JSONs (Matemática e Português)", type=["json"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        content = json.load(file)
        meta = content['metadata']
        all_data.append({
            "Data": datetime.strptime(meta['data'], "%d-%m-%Y"),
            "Disciplina": meta['disciplina'],
            "media_saeb": meta['media_saeb']
        })
    
    df_f = pd.DataFrame(all_data).sort_values('Data')
    
    # Identificar a data mais recente
    ultima_data = df_f['Data'].max()
    dados_atuais = df_f[df_f['Data'] == ultima_data]

    # --- LÓGICA DOS CARDS TRI TRIPLO ---
    st.subheader(f"📍 Situação Atual - {ultima_data.strftime('%d/%m/%Y')}")
    col_mat, col_media, col_port = st.columns(3)

    # Matemática
    val_mat = dados_atuais[dados_atuais['Disciplina'].str.contains('Matematica|Matemática', case=False)]['media_saeb']
    with col_mat:
        if not val_mat.empty:
            st.metric("📊 Matemática", f"{val_mat.iloc[0]:.2f}", help="Média SAEB em Matemática")
            st.caption(f"Nível: {classificar_nivel_saeb(val_mat.iloc[0])}")
        else:
            st.metric("📊 Matemática", "N/A")

    # Média Geral
    media_global = dados_atuais['media_saeb'].mean()
    with col_media:
        st.markdown("""
            <style>
            [data-css-1px866v] { border-top: 4px solid #FACC15 !important; } 
            </style>
        """, unsafe_allow_html=True)
        st.metric("🏆 MÉDIA SAEB (Geral)", f"{media_global:.2f}", delta=None)
        st.write(f"**Status:** {classificar_nivel_saeb(media_global)}")

    # Português
    val_port = dados_atuais[dados_atuais['Disciplina'].str.contains('Portugues|Português|Lingua', case=False)]['media_saeb']
    with col_port:
        if not val_port.empty:
            st.metric("📚 Língua Portuguesa", f"{val_port.iloc[0]:.2f}", help="Média SAEB em Português")
            st.caption(f"Nível: {classificar_nivel_saeb(val_port.iloc[0])}")
        else:
            st.metric("📚 Língua Portuguesa", "N/A")

    st.divider()

    # --- GRÁFICO DE EVOLUÇÃO ---
    st.subheader("📈 Evolução das Proficiências")
    fig = px.line(df_f, x='Data', y='media_saeb', color='Disciplina', markers=True,
                  color_discrete_map={'Matematica': '#FACC15', 'Portugues': '#38BDF8'},
                  template="plotly_dark")
    fig.update_layout(yaxis_title="Escala SAEB", xaxis_title="Avaliações")
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE HISTÓRICO ---
    st.subheader("📋 Histórico de Dados")
    df_exibir = df_f.copy()
    df_exibir['Data'] = df_exibir['Data'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_exibir, use_container_width=True, hide_index=True)

else:
    st.info("💡 Carregue os arquivos JSON de Matemática e Português para ativar o painel comparativo.")
