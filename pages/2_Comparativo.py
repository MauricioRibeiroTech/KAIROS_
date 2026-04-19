import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
import base64

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
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

def classificar_nivel_saeb(nota):
    if nota < 175: return "Muito Baixo"
    elif nota < 225: return "Básico"
    elif nota < 275: return "Adequado"
    else: return "Avançado"

# --- GERADOR DE RELATÓRIO HTML CONSOLIDADO ---
def gerar_relatorio_html_geral(df_evolucao, media_mat, media_port, media_geral, data_ref):
    # Cores para o HTML
    color_mat = "#FACC15"
    color_port = "#38BDF8"
    
    # Gerar linhas da tabela de histórico
    tabela_html = df_evolucao.sort_values('Data', ascending=False).to_html(index=False, classes='table')
    
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; color: #333; padding: 40px; }}
            .container {{ background-color: #fff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 1000px; margin: auto; }}
            .header {{ border-bottom: 3px solid #1E3A8A; padding-bottom: 20px; margin-bottom: 30px; text-align: center; }}
            .header h1 {{ color: #1E3A8A; margin: 0; font-size: 28px; }}
            .header p {{ color: #666; margin: 5px 0 0 0; }}
            .grid {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ flex: 1; padding: 20px; border-radius: 10px; text-align: center; color: white; }}
            .card.mat {{ background-color: #b8960d; }} /* Amarelo Escuro para leitura */
            .card.port {{ background-color: #0369a1; }}
            .card.geral {{ background-color: #1e3a8a; }}
            .card h3 {{ margin: 0; font-size: 14px; text-transform: uppercase; opacity: 0.9; }}
            .card .value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
            .card .level {{ font-size: 12px; background: rgba(255,255,255,0.2); padding: 5px; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #f8fafc; color: #475569; padding: 12px; text-align: left; border-bottom: 2px solid #e2e8f0; }}
            td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
            .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #94a3b8; }}
            .signature {{ margin-top: 40px; text-align: center; font-style: italic; color: #475569; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>KAIROS V2 | Relatório de Desempenho Unificado</h1>
                <p>Referência Técnica: Escala SAEB | Data da Extração: {data_ref}</p>
            </div>

            <div class="grid">
                <div class="card mat">
                    <h3>Matemática</h3>
                    <div class="value">{media_mat:.2f}</div>
                    <div class="level">{classificar_nivel_saeb(media_mat)}</div>
                </div>
                <div class="card geral">
                    <h3>Média SAEB Geral</h3>
                    <div class="value">{media_geral:.2f}</div>
                    <div class="level">{classificar_nivel_saeb(media_geral)}</div>
                </div>
                <div class="card port">
                    <h3>Língua Portuguesa</h3>
                    <div class="value">{media_port:.2f}</div>
                    <div class="level">{classificar_nivel_saeb(media_port)}</div>
                </div>
            </div>

            <h2>📋 Histórico de Evolução Pedagógica</h2>
            <p>Os dados abaixo corroboram a trajetória da turma entre as avaliações diagnósticas realizadas:</p>
            {tabela_html}

            <div class="signature">
                <br><br>
                ____________________________________________________<br>
                Prof. Maurício Aparecido Ribeiro<br>
                Análise de Dados Educacionais
            </div>

            <div class="footer">
                Relatório gerado automaticamente pelo sistema KAIROS V2 - Data Intelligence.
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

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
    data_ref_str = ultima_data.strftime('%d/%m/%Y')
    dados_atuais = df_f[df_f['Data'] == ultima_data]

    # --- LÓGICA DOS CARDS TRI TRIPLO ---
    st.subheader(f"📍 Situação Atual - {data_ref_str}")
    col_mat, col_media, col_port = st.columns(3)

    # Matemática
    df_mat = dados_atuais[dados_atuais['Disciplina'].str.contains('Matematica|Matemática', case=False)]
    val_mat = df_mat['media_saeb'].iloc[0] if not df_mat.empty else 0.0

    with col_mat:
        st.metric("📊 Matemática", f"{val_mat:.2f}" if val_mat > 0 else "N/A")
        if val_mat > 0: st.caption(f"Nível: {classificar_nivel_saeb(val_mat)}")

    # Média Geral
    media_global = dados_atuais['media_saeb'].mean()
    with col_media:
        st.metric("🏆 MÉDIA SAEB (Geral)", f"{media_global:.2f}")
        st.write(f"**Status:** {classificar_nivel_saeb(media_global)}")

    # Português
    df_port = dados_atuais[dados_atuais['Disciplina'].str.contains('Portugues|Português|Lingua', case=False)]
    val_port = df_port['media_saeb'].iloc[0] if not df_port.empty else 0.0

    with col_port:
        st.metric("📚 Língua Portuguesa", f"{val_port:.2f}" if val_port > 0 else "N/A")
        if val_port > 0: st.caption(f"Nível: {classificar_nivel_saeb(val_port)}")

    st.divider()

    # --- GRÁFICO DE EVOLUÇÃO ---
    st.subheader("📈 Evolução das Proficiências")
    fig = px.line(df_f, x='Data', y='media_saeb', color='Disciplina', markers=True,
                  color_discrete_map={'Matematica': '#FACC15', 'Portugues': '#38BDF8'},
                  template="plotly_dark")
    fig.update_layout(yaxis_title="Escala SAEB", xaxis_title="Avaliações")
    st.plotly_chart(fig, use_container_width=True)

    # --- BOTÃO DE DOWNLOAD DO RELATÓRIO CONSOLIDADO ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Relatório Final")
    
    df_historico = df_f.copy()
    df_historico['Data'] = df_historico['Data'].dt.strftime('%d/%m/%Y')
    
    report_html = gerar_relatorio_html_geral(df_historico, val_mat, val_port, media_global, data_ref_str)
    
    st.sidebar.download_button(
        label="📥 Baixar Relatório Unificado (.HTML)",
        data=report_html,
        file_name=f"Relatorio_Consolidado_SAEB_{ultima_data.strftime('%Y%m%d')}.html",
        mime="text/html"
    )

    # --- TABELA DE HISTÓRICO NA TELA ---
    st.subheader("📋 Histórico de Dados")
    st.dataframe(df_historico, use_container_width=True, hide_index=True)

else:
    st.info("💡 Carregue os arquivos JSON de Matemática e Português para ativar o painel comparativo.")
