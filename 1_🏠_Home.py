import streamlit as st

st.set_page_config(page_title="KAIROS V2 | Home", layout="wide")

# CSS para manter o estilo Dark/Gold
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; text-align: center; }
    h1 { color: #FACC15; font-size: 4rem; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ KAIROS V2")
st.subheader("Sistema de Inteligência e Análise Pedagógica")

st.markdown("---")
st.write("### Bem-vindo, Professora!")
st.write("Selecione uma ferramenta na barra lateral para começar:")

col1, col2 = st.columns(2)
with col1:
    st.info("📂 **Módulo Análise TRI**: Processe novos CSVs e gere relatórios de TRI.")
with col2:
    st.info("📈 **Módulo Comparativo**: Analise o histórico e a evolução das turmas.")
