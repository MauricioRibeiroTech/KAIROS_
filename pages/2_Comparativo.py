import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="KAIROS V2 | Evolução de Acertos", layout="wide")

# --- CSS DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #12161D !important; border-right: 2px solid #FACC15; }
    [data-testid="stMetric"] { background-color: #161B22 !important; border-top: 4px solid #FACC15 !important; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #FACC15 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- TRANSFORMAÇÃO PARA ESCALA SAEB ---
def converter_para_saeb(logit):
    """
    Transforma o Logit (referencial 0) para a escala SAEB.
    Média 250, Desvio Padrão 50.
    """
    return (logit * 50) + 250

def calcular_nivel_saeb(nota_saeb):
    # Níveis baseados no documento Escala SAEB para Matemática
    if nota_saeb < 175: return "Nível 0/1 (Muito Baixo)"
    elif nota_saeb < 225: return "Nível 2 (Básico)"
    elif nota_saeb < 275: return "Nível 3/4 (Adequado)"
    else: return "Nível 5+ (Avançado)"

def realizar_analise_pedagogica(df):
    if len(df) < 2: return "Dados insuficientes para análise de tendência."
    df_s = df.sort_values('Data')
    diff = df_s.iloc[-1]['media_geral'] - df_s.iloc[-2]['media_geral']
    
    # Análise honesta baseada no Logit (referencial central)
    logit_atual = df_s.iloc[-1]['proficiencia_logit']
    
    if logit_atual > 0:
        status_pos = "acima da linha do equador (Positivo)"
    else:
        status_pos = "abaixo da linha do equador (Negativo)"

    if diff > 0.5:
        return f"🟢 **MELHORIA:** A média subiu. A turma está {status_pos} em relação à dificuldade da prova."
    elif diff < -0.5:
        return f"🔴 **ALERTA:** Queda detectada. A turma encontra-se {status_pos}."
    return f"🟡 **ESTABILIDADE:** Desempenho constante e {status_pos}."

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛡️ KAIROS V2")
    uploaded_files = st.file_uploader("Arraste seus JSONs datados", type=["json"], accept_multiple_files=True)

if uploaded_files:
    registros = []
    for arq in uploaded_files:
        try:
            raw = json.load(arq)
            meta = raw.get('metadata', {})
            data_corpo = raw.get('data', [])
            
            data_str = meta.get('data', arq.name.split('_')[-1].replace('.json', ''))
            data_dt = datetime.strptime(data_str, "%d-%m-%Y")
            
            thetas = [aluno.get('Theta') for aluno in data_corpo if aluno.get('Theta') is not None]
            logit_medio = sum(thetas) / len(thetas) if thetas else 0.0
            
            # Aplicação da Escala do PDF (Transformação Linear)
            nota_saeb = converter_para_saeb(logit_medio)

            registros.append({
                "Data": data_dt,
                "Disciplina": meta.get('disciplina', 'Indefinida'),
                "media_geral": float(meta.get('media_geral', 0)),
                "proficiencia_logit": logit_medio,
                "Proficiência SAEB": round(nota_saeb, 2),
                "Nível": calcular_nivel_saeb(nota_saeb),
                "Alunos": int(meta.get('total_alunos', 0))
            })
        except Exception as e:
            st.error(f"Erro ao processar {arq.name}: {e}")

    df_hist = pd.DataFrame(registros).sort_values('Data')

    if not df_hist.empty:
        st.title("📈 Analisador de Evolução (Escala SAEB)")
        
        disciplinas = st.sidebar.multiselect("Filtrar Disciplinas", df_hist['Disciplina'].unique(), default=df_hist['Disciplina'].unique())
        df_f = df_hist[df_hist['Disciplina'].isin(disciplinas)]

        c1, c2, c3 = st.columns(3)
        c1.metric("Média Geral Acertos", f"{df_f.iloc[-1]['media_geral']:.2f}")
        c2.metric("Escala SAEB Atual", f"{df_f.iloc[-1]['Proficiência SAEB']:.1f}")
        c3.metric("Status Cognitivo", df_f.iloc[-1]['Nível'])

        st.divider()

        # Gráfico de Evolução conforme pedido (Eixo Y: Média Geral Acertos)
        st.subheader("🎯 Evolução da Média Geral de Acertos")
        fig_evol = px.line(
            df_f, x='Data', y='media_geral', color='Disciplina', markers=True, 
            template="plotly_dark",
            labels={'Data': 'DATA', 'media_geral': 'Média Geral Acertos'},
            color_discrete_sequence=['#FACC15', '#38BDF8']
        )
        fig_evol.update_xaxes(dtick="d1", tickformat="%d/%m/%Y")
        st.plotly_chart(fig_evol, use_container_width=True)

        st.divider()
        col_an, col_tab = st.columns([1, 1])
        
        with col_an:
            st.subheader("🧠 Análise Pedagógica (Referencial Logit)")
            analise_txt = realizar_analise_pedagogica(df_f)
            st.info(analise_txt)

        with col_tab:
            st.subheader("📋 Histórico Consolidado")
            df_exibir = df_f.copy()
            df_exibir['Data'] = df_exibir['Data'].dt.strftime('%d/%m/%Y')
            # Exibindo a nova coluna SAEB na tabela
            st.dataframe(df_exibir[['Data', 'Disciplina', 'media_geral', 'Proficiência SAEB', 'Nível']], 
                         hide_index=True, use_container_width=True)

        st.divider()
        relatorio_html = f"""
        <html><body style="font-family:sans-serif; background:#0d1117; color:#fff; padding:30px;">
            <h1 style="color:#facc15; border-bottom:2px solid #facc15;">Relatório KAIROS V2 - Padrão SAEB</h1>
            <p><b>Diagnóstico:</b> {analise_txt}</p>
            <h3>Dados Consolidados</h3>
            {df_exibir[['Data', 'Disciplina', 'media_geral', 'Proficiência SAEB', 'Nível']].to_html(index=False)}
        </body></html>
        """
        st.download_button("📄 Baixar Relatório Final", relatorio_html, "Relatorio_SAEB.html", "text/html")

else:
    st.info("Aguardando upload dos arquivos JSON...")
