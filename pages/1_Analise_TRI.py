import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="KAIROS V2 | Inteligência Pedagógica", layout="wide")

# --- CSS DARK MODE TOTAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;900&display=swap');
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #12161D !important; border-right: 2px solid #FACC15; }
    .sidebar-title { color: #FACC15; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 20px 0; border-bottom: 2px solid #FACC15; }
    [data-testid="stMetric"] { background-color: #161B22 !important; border: 1px solid #30363D !important; border-top: 4px solid #FACC15 !important; border-radius: 12px !important; }
    [data-testid="stMetricValue"] { color: #FACC15 !important; font-size: 3rem !important; }
    .stButton button { background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%) !important; color: white !important; font-weight: bold !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def converter_para_saeb(theta):
    return (theta * 50) + 250

def classificar_proficiencia(nota_saeb):
    if nota_saeb < 175: return "Nível 0/1 (Muito Baixo)"
    elif nota_saeb < 225: return "Nível 2 (Básico)"
    elif nota_saeb < 275: return "Nível 3/4 (Adequado)"
    else: return "Nível 5+ (Avançado)"

def colorir_tabela(val):
    if "Avançado" in val or "Adequado" in val: color = '#15803d'
    elif "Básico" in val: color = '#a16207'
    else: color = '#b91c1c'
    return f'background-color: {color}; color: white; font-weight: bold;'

# --- GERADOR DE RELATÓRIO HTML ---
def generate_enhanced_html(df_final, disciplina, data, kpis, df_erros_freq):
    rows_alunos = ""
    for _, row in df_final.iterrows():
        prof = row['Nível']
        style = "background-color: #b91c1c; color: white;"
        if "Avançado" in prof or "Adequado" in prof: style = "background-color: #15803d; color: white;"
        elif "Básico" in prof: style = "background-color: #a16207; color: white;"
        rows_alunos += f"<tr><td>{row['NOME']}</td><td>{row['Acertos']}</td><td>{row['Nota SAEB']:.2f}</td><td style='{style}'>{row['Nível']}</td><td>{row['Dificuldades']}</td></tr>"

    rows_erros = ""
    for _, row in df_erros_freq.iterrows():
        rows_erros += f"<tr><td>{row['Questão']}</td><td>{int(row['Alunos com Erro'])}</td></tr>"

    html_content = f"""
    <html>
    <head><meta charset="UTF-8"><style>
        body {{ font-family: sans-serif; background: #0d1117; color: #fff; padding: 30px; }}
        .header {{ border-bottom: 2px solid #facc15; padding-bottom: 10px; }}
        .kpi-box {{ background: #161b22; padding: 20px; border: 1px solid #30363d; border-radius: 8px; margin: 20px 0; display: flex; gap: 40px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 40px; }}
        th {{ background: #1e3a8a; padding: 12px; text-align: left; border: 1px solid #333; }}
        td {{ padding: 10px; border: 1px solid #333; }}
    </style></head>
    <body>
        <h1 class="header">KAIROS V2 - {disciplina} | Relatório Pedagógico</h1>
        <div class="kpi-box">
            <div><b>Média SAEB:</b> {kpis['media_saeb']:.2f}</div>
            <div><b>Média Acertos:</b> {kpis['media_geral']:.2f}</div>
            <div><b>Total Alunos:</b> {kpis['total_alunos']}</div>
        </div>
        <h3>📋 Desempenho Individual</h3>
        <table>
            <thead><tr><th>NOME</th><th>ACERTOS</th><th>NOTA SAEB</th><th>NÍVEL</th><th>DIFICULDADES</th></tr></thead>
            <tbody>{rows_alunos}</tbody>
        </table>
        <h3>⚠️ Diagnóstico de Itens (Frequência de Erro)</h3>
        <table style="width: 40%;">
            <thead><tr><th>Questão</th><th>Alunos com Erro</th></tr></thead>
            <tbody>{rows_erros}</tbody>
        </table>
    </body></html>
    """
    return html_content

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">KAIROS V2</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📂 Arquivo (.csv)", type=["csv"])
    if uploaded_file:
        # CAPTURA DO NOME DO ARQUIVO PARA A DISCIPLINA
        nome_arquivo_bruto = uploaded_file.name
        nome_disc = nome_arquivo_bruto.split('.')[0].replace('_', ' ').capitalize()
        
        data_str = datetime.now().strftime("%d-%m-%Y")
        df_raw = pd.read_csv(uploaded_file)
        cols_q = [c for c in df_raw.columns if c.startswith('Q')]
        gabarito_raw = st.text_input(f"Sequência ({len(cols_q)} questões)", "").upper().strip()
        gabarito = list(gabarito_raw)

# --- ENGINE ---
if uploaded_file and len(gabarito) == len(cols_q):
    total_alunos = len(df_raw)
    df_results = df_raw[['NOME']].copy()
    erros_por_questao = {col: 0 for col in cols_q}

    for idx, row in df_raw.iterrows():
        erros_aluno = []
        acertos_count = 0
        for i, col in enumerate(cols_q):
            if str(row[col]).upper() == gabarito[i]:
                acertos_count += 1
            else:
                erros_aluno.append(col)
                erros_por_questao[col] += 1
        df_results.at[idx, 'Acertos'] = int(acertos_count)
        df_results.at[idx, 'Dificuldades'] = ", ".join(erros_aluno)

    # Tabela de Frequência de Erros
    dados_erros = [{"Questão": q, "Alunos com Erro": int(count)} for q, count in erros_por_questao.items()]
    df_erros_freq = pd.DataFrame(dados_erros)

    # TRI e SAEB
    p_acerto = (df_results['Acertos'] / len(cols_q)).clip(0.01, 0.99)
    df_results['Theta'] = np.log(p_acerto / (1 - p_acerto))
    df_results['Nota SAEB'] = df_results['Theta'].apply(converter_para_saeb)
    df_results['Nível'] = df_results['Nota SAEB'].apply(classificar_proficiencia)
    
    df_view = df_results[['NOME', 'Acertos', 'Nota SAEB', 'Nível', 'Dificuldades', 'Theta']].sort_values('Nota SAEB', ascending=False)

    # --- DASHBOARD STREAMLIT ---
    st.title(f"📊 Análise Diagnóstica: {nome_disc}")
    kpis = {
        "media_geral": df_results['Acertos'].mean(), 
        "media_saeb": df_results['Nota SAEB'].mean(), 
        "total_alunos": total_alunos,
        "disciplina": nome_disc, # NOME DA DISCIPLINA INSERIDO AQUI
        "data": data_str
    }
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Média Acertos", f"{kpis['media_geral']:.2f}")
    c2.metric("Média SAEB", f"{kpis['media_saeb']:.2f}")
    c3.metric("Total Alunos", total_alunos)

    st.subheader("📋 Tabela de Proficiência")
    st.dataframe(
        df_view[['NOME', 'Acertos', 'Nota SAEB', 'Nível', 'Dificuldades']].style.format({"Nota SAEB": "{:.2f}"}).map(colorir_tabela, subset=['Nível']), 
        use_container_width=True, hide_index=True
    )

    st.subheader("⚠️ Número de Alunos com Erro por Questão")
    st.table(df_erros_freq)

    st.divider()
    html_report = generate_enhanced_html(df_view, nome_disc, data_str, kpis, df_erros_freq)
    st.download_button("📄 Baixar Relatório Pedagógico (.HTML)", html_report, f"Relatorio_SAEB_{nome_disc}.html", "text/html")

    # JSON AGORA INCLUI O NOME DA DISCIPLINA NO METADATA
    json_data = {"metadata": kpis, "data": df_view.to_dict(orient='records')}
    st.download_button("📦 Baixar JSON para Comparativo", json.dumps(json_data, indent=4), f"{nome_disc}_{data_str}.json", "application/json")

elif uploaded_file:
    st.warning("Insira o gabarito na barra lateral.")
else:
    st.info("KAIROS V2: Aguardando CSV para análise TRI e SAEB...")
