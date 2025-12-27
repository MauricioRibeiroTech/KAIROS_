import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import zipfile
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Análise de Avaliações Educacionais",
    page_icon="📊",
    layout="wide"
)

# Estilo CSS personalizado - CORES AJUSTADAS PARA MELHOR LEGIBILIDADE
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2D3748;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-card h3 {
        color: white;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .metric-card h2 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .info-box {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin: 1rem 0;
        color: #2D3748;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-box h3 {
        color: #1E3A8A;
        margin-top: 0;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .info-box ol, .info-box p {
        color: #4A5568;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .info-box strong {
        color: #2D3748;
        font-weight: 700;
    }
    .export-button {
        background-color: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        margin: 0.2rem;
    }
    .export-button:hover {
        background-color: #0da271;
    }
    /* Estilo para texto geral */
    .stMarkdown, .stText, .stInfo, .stWarning {
        color: #2D3748 !important;
    }
    /* Melhorar legibilidade das tabelas */
    .stDataFrame {
        color: #2D3748;
    }
    /* Corrigir cores dos selects */
    .stSelectbox label {
        color: #2D3748 !important;
        font-weight: 500;
    }
    .stSelectbox div[data-baseweb="select"] {
        color: #2D3748 !important;
    }
    /* Corrigir cores dos botões */
    .stButton button {
        color: white !important;
    }
    /* Estilo para o rodapé */
    .footer {
        text-align: center;
        color: #718096;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">📈 Dashboard de Análise de Avaliações Educacionais</h1>', unsafe_allow_html=True)

# Upload de múltiplos arquivos
st.sidebar.header("📂 Upload de Arquivos")
uploaded_files = st.sidebar.file_uploader(
    "Selecione os arquivos JSON de avaliação",
    type=['json'],
    accept_multiple_files=True,
    help="Selecione um ou mais arquivos JSON gerados pelo sistema de avaliação"
)

@st.cache_data
def carregar_arquivos(uploaded_files):
    """Carrega e processa os arquivos JSON."""
    dados = {}
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                content = json.loads(uploaded_file.getvalue().decode())
                nome_avaliacao = uploaded_file.name.replace('.json', '')
                dados[nome_avaliacao] = content
            except Exception as e:
                st.error(f"Erro ao carregar {uploaded_file.name}: {e}")
    
    return dados

# Carregar dados
dados = carregar_arquivos(uploaded_files)

if not dados:
    st.warning("📁 Nenhum arquivo JSON carregado.")
    
    st.markdown("""
    <div class="info-box">
    <h3>📋 Como usar:</h3>
    <ol>
        <li>No menu lateral à esquerda, clique em <strong>"Browse files"</strong></li>
        <li>Selecione um ou mais arquivos JSON das avaliações</li>
        <li>Os dados serão automaticamente carregados e analisados</li>
        <li>Explore as diferentes visualizações abaixo</li>
    </ol>
    <p><strong>Nota:</strong> Os arquivos devem estar no formato JSON gerado pelo sistema de avaliação.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Exemplo da estrutura esperada
    with st.expander("📄 Exemplo da estrutura do arquivo JSON esperada"):
        st.json({
            "metadata": {
                "data_analise": "2025-12-26T22:32:13.514421",
                "total_alunos": 5,
                "total_questoes": 4,
                "proficiencia_media": 0.8738110418683684,
                "desvio_padrao_proficiencia": 0.588300615910456,
                "taxa_acerto_media": 85.0,
                "confiabilidade": 0.7621947100625063
            },
            "gabarito": {"Q1": "A", "Q2": "B", "Q3": "C", "Q4": "C"},
            "resumo_alunos": [
                {
                    "Aluno": "Aluno 1",
                    "Proficiencia (θ)": 1.2815515655446004,
                    "Pontuacao Total": 4,
                    "Percentual de Acerto": 100.0,
                    "Z-Score": 0.7748891497507717
                }
            ]
        })
    st.stop()

# Exibir estatísticas básicas
st.markdown('<h2 class="sub-header">📋 Resumo das Avaliações</h2>', unsafe_allow_html=True)

# Criar DataFrames para análise
avaliacoes_info = []
alunos_data = []
questoes_data = []
tutores_data = []

for avaliacao_nome, conteudo in dados.items():
    # Metadata
    meta = conteudo['metadata']
    avaliacoes_info.append({
        'Avaliação': avaliacao_nome,
        'Data Análise': meta['data_analise'],
        'Total Alunos': meta['total_alunos'],
        'Total Questões': meta['total_questoes'],
        'Proficiência Média': meta['proficiencia_media'],
        'Desvio Padrão': meta['desvio_padrao_proficiencia'],
        'Taxa Acerto Média': meta['taxa_acerto_media'],
        'Confiabilidade': meta['confiabilidade']
    })
    
    # Alunos
    for aluno in conteudo['resumo_alunos']:
        alunos_data.append({
            'Avaliação': avaliacao_nome,
            'Aluno': aluno['Aluno'],
            'Proficiência': aluno['Proficiencia (θ)'],
            'Pontuação Total': aluno['Pontuacao Total'],
            '% Acerto': aluno['Percentual de Acerto'],
            'Z-Score': aluno['Z-Score']
        })
    
    # Questões
    for questao in conteudo['resumo_questoes']:
        questoes_data.append({
            'Avaliação': avaliacao_nome,
            'Questão': questao['Questao'],
            'Dificuldade': questao['Dificuldade (b)'],
            'Discriminação': questao['Discriminacao (a)'],
            '% Acerto': questao['% Acerto'],
            'Correlação Bisserial': questao.get('Correlacao Bisserial', np.nan)
        })
    
    # Tutores
    if 'top_tutores' in conteudo:
        for tutor in conteudo['top_tutores']:
            tutores_data.append({
                'Avaliação': avaliacao_nome,
                'Aluno': tutor['Aluno'],
                'Proficiência': tutor['Proficiencia (θ)'],
                'Pontuação Total': tutor['Pontuacao Total'],
                '% Acerto': tutor['Percentual de Acerto'],
                'Score_Tutor': tutor['Score_Tutor'],
                'Posição': tutor['Posicao']
            })

# Criar DataFrames
df_avaliacoes = pd.DataFrame(avaliacoes_info)
df_alunos = pd.DataFrame(alunos_data)
df_questoes = pd.DataFrame(questoes_data)
df_tutores = pd.DataFrame(tutores_data) if tutores_data else None

# Layout de métricas
st.markdown('<h2 class="sub-header">📊 Métricas Gerais</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📚 Avaliações</h3>
        <h2>{len(dados)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    alunos_unicos = df_alunos['Aluno'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <h3>👥 Alunos Únicos</h3>
        <h2>{alunos_unicos}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    proficiencia_media = df_avaliacoes['Proficiência Média'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 Proficiência Média</h3>
        <h2>{proficiencia_media:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    taxa_acerto_media = df_avaliacoes['Taxa Acerto Média'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>✅ Taxa de Acerto</h3>
        <h2>{taxa_acerto_media:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

# Tabela de avaliações
st.markdown('<h2 class="sub-header">📋 Tabela de Avaliações</h2>', unsafe_allow_html=True)
st.dataframe(df_avaliacoes.style.format({
    'Proficiência Média': '{:.3f}',
    'Desvio Padrão': '{:.3f}',
    'Taxa Acerto Média': '{:.1f}%',
    'Confiabilidade': '{:.3f}'
}), use_container_width=True)

# Gráfico 1: Comparação entre avaliações COM BARRAS SEPARADAS
st.markdown('<h2 class="sub-header">📈 Comparação entre Avaliações</h2>', unsafe_allow_html=True)

# Criar gráficos separados para melhor controle das barras
col1, col2 = st.columns(2)

with col1:
    # Gráfico de Proficiência Média
    fig_proficiencia = go.Figure()
    
    fig_proficiencia.add_trace(go.Bar(
        x=df_avaliacoes['Avaliação'],
        y=df_avaliacoes['Proficiência Média'],
        name='Proficiência Média',
        marker_color='#3b82f6',
        text=df_avaliacoes['Proficiência Média'].round(3),
        textposition='outside',
        textfont=dict(color='#2D3748', size=12),
        width=0.6,
        marker=dict(
            line=dict(width=2, color='darkblue')
        )
    ))
    
    fig_proficiencia.update_layout(
        title=dict(
            text='Proficiência Média por Avaliação',
            font=dict(color='#2D3748', size=18)
        ),
        xaxis_title='Avaliação',
        yaxis_title='Proficiência (θ)',
        height=400,
        showlegend=False,
        bargap=0.4,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=0,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        font=dict(color='#2D3748')
    )
    st.plotly_chart(fig_proficiencia, use_container_width=True)

with col2:
    # Gráfico de Taxa de Acerto Média
    fig_acerto = go.Figure()
    
    fig_acerto.add_trace(go.Bar(
        x=df_avaliacoes['Avaliação'],
        y=df_avaliacoes['Taxa Acerto Média'],
        name='Taxa de Acerto Média',
        marker_color='#10b981',
        text=df_avaliacoes['Taxa Acerto Média'].round(1).astype(str) + '%',
        textposition='outside',
        textfont=dict(color='#2D3748', size=12),
        width=0.6,
        marker=dict(
            line=dict(width=2, color='darkgreen')
        )
    ))
    
    fig_acerto.update_layout(
        title=dict(
            text='Taxa de Acerto Média por Avaliação',
            font=dict(color='#2D3748', size=18)
        ),
        xaxis_title='Avaliação',
        yaxis_title='% de Acerto',
        height=400,
        showlegend=False,
        bargap=0.4,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=0,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748'),
            range=[0, 105]
        ),
        font=dict(color='#2D3748')
    )
    st.plotly_chart(fig_acerto, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # Gráfico de Desvio Padrão
    fig_desvio = go.Figure()
    
    fig_desvio.add_trace(go.Bar(
        x=df_avaliacoes['Avaliação'],
        y=df_avaliacoes['Desvio Padrão'],
        name='Desvio Padrão',
        marker_color='#f59e0b',
        text=df_avaliacoes['Desvio Padrão'].round(3),
        textposition='outside',
        textfont=dict(color='#2D3748', size=12),
        width=0.6,
        marker=dict(
            line=dict(width=2, color='darkorange')
        )
    ))
    
    fig_desvio.update_layout(
        title=dict(
            text='Desvio Padrão da Proficiência por Avaliação',
            font=dict(color='#2D3748', size=18)
        ),
        xaxis_title='Avaliação',
        yaxis_title='Desvio Padrão',
        height=400,
        showlegend=False,
        bargap=0.4,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=0,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        font=dict(color='#2D3748')
    )
    st.plotly_chart(fig_desvio, use_container_width=True)

with col4:
    # Gráfico de Confiabilidade
    fig_confiabilidade = go.Figure()
    
    fig_confiabilidade.add_trace(go.Bar(
        x=df_avaliacoes['Avaliação'],
        y=df_avaliacoes['Confiabilidade'],
        name='Confiabilidade',
        marker_color='#8b5cf6',
        text=df_avaliacoes['Confiabilidade'].round(3),
        textposition='outside',
        textfont=dict(color='#2D3748', size=12),
        width=0.6,
        marker=dict(
            line=dict(width=2, color='darkviolet')
        )
    ))
    
    fig_confiabilidade.update_layout(
        title=dict(
            text='Confiabilidade por Avaliação',
            font=dict(color='#2D3748', size=18)
        ),
        xaxis_title='Avaliação',
        yaxis_title='Confiabilidade',
        height=400,
        showlegend=False,
        bargap=0.4,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=0,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748'),
            range=[0, 1.1]
        ),
        font=dict(color='#2D3748')
    )
    st.plotly_chart(fig_confiabilidade, use_container_width=True)

# Gráfico 2: Desempenho dos Alunos
st.markdown('<h2 class="sub-header">📊 Desempenho dos Alunos</h2>', unsafe_allow_html=True)

# Selecionar avaliação para análise detalhada
avaliacao_selecionada = st.selectbox(
    "Selecione uma avaliação para análise detalhada:",
    options=list(dados.keys()),
    key="select_avaliacao"
)

if avaliacao_selecionada:
    # Filtrar dados da avaliação selecionada
    alunos_avaliacao = df_alunos[df_alunos['Avaliação'] == avaliacao_selecionada]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribuição de proficiência
        fig2 = go.Figure()
        
        fig2.add_trace(go.Histogram(
            x=alunos_avaliacao['Proficiência'],
            nbinsx=10,
            name='Proficiência',
            marker_color='#3b82f6',
            opacity=0.7,
            marker=dict(
                line=dict(width=1, color='darkblue')
            )
        ))
        
        # Adicionar linha da média
        media_proficiencia = alunos_avaliacao['Proficiência'].mean()
        fig2.add_vline(
            x=media_proficiencia,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Média: {media_proficiencia:.2f}",
            annotation_position="top right"
        )
        
        fig2.update_layout(
            title=dict(
                text=f'Distribuição de Proficiência - {avaliacao_selecionada}',
                font=dict(color='#2D3748', size=18)
            ),
            xaxis_title='Proficiência (θ)',
            yaxis_title='Número de Alunos',
            height=400,
            bargap=0.1,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            font=dict(color='#2D3748')
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Gráfico de relação entre proficiência e % de acerto
        fig3 = px.scatter(
            alunos_avaliacao,
            x='Proficiência',
            y='% Acerto',
            hover_data=['Aluno', 'Pontuação Total'],
            title=f'Relação Proficiência vs % Acerto - {avaliacao_selecionada}',
            color='Pontuação Total',
            size='Pontuação Total',
            color_continuous_scale='Viridis',
            height=400
        )
        
        fig3.update_traces(
            marker=dict(
                line=dict(width=1, color='DarkSlateGrey'),
                size=12
            )
        )
        
        fig3.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            title_font=dict(color='#2D3748', size=18),
            font=dict(color='#2D3748')
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # Ranking de alunos
    st.markdown(f"<h3 class='sub-header'>🏆 Ranking de Alunos - {avaliacao_selecionada}</h3>", unsafe_allow_html=True)
    
    # Ordenar por proficiência
    ranking_alunos = alunos_avaliacao.sort_values('Proficiência', ascending=False)
    
    # Criar gráfico de ranking
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        y=ranking_alunos['Aluno'],
        x=ranking_alunos['Proficiência'],
        orientation='h',
        marker_color='#3b82f6',
        text=ranking_alunos['Proficiência'].round(3),
        textposition='outside',
        textfont=dict(color='#2D3748', size=11),
        marker=dict(
            line=dict(width=1, color='darkblue')
        )
    ))
    
    fig4.update_layout(
        title=dict(
            text=f'Ranking por Proficiência - {avaliacao_selecionada}',
            font=dict(color='#2D3748', size=18)
        ),
        xaxis_title='Proficiência (θ)',
        yaxis=dict(autorange="reversed"),
        height=max(400, len(ranking_alunos) * 40),
        bargap=0.3,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        ),
        yaxis_title='Aluno',
        font=dict(color='#2D3748')
    )
    
    st.plotly_chart(fig4, use_container_width=True)

# Gráfico 3: Análise de Questões
st.markdown('<h2 class="sub-header">❓ Análise de Questões</h2>', unsafe_allow_html=True)

if not df_questoes.empty:
    # Filtrar questões da avaliação selecionada
    questoes_avaliacao = df_questoes[df_questoes['Avaliação'] == avaliacao_selecionada]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de dificuldade vs discriminação
        fig5 = px.scatter(
            questoes_avaliacao,
            x='Dificuldade',
            y='Discriminação',
            size='% Acerto',
            color='% Acerto',
            hover_name='Questão',
            title=f'Dificuldade vs Discriminação - {avaliacao_selecionada}',
            labels={'Dificuldade': 'Dificuldade (b)', 'Discriminação': 'Discriminação (a)'},
            color_continuous_scale='RdYlGn_r',
            size_max=40,
            height=400
        )
        
        # Adicionar quadrantes
        fig5.add_hline(y=1, line_dash="dash", line_color="gray")
        fig5.add_vline(x=0, line_dash="dash", line_color="gray")
        
        # Anotar quadrantes
        fig5.add_annotation(x=2, y=2, text="Boa questão", showarrow=False, font=dict(color='#2D3748'))
        fig5.add_annotation(x=2, y=0.5, text="Fácil e pouco discriminativa", showarrow=False, font=dict(color='#2D3748'))
        fig5.add_annotation(x=-2, y=2, text="Difícil e muito discriminativa", showarrow=False, font=dict(color='#2D3748'))
        fig5.add_annotation(x=-2, y=0.5, text="Questão problemática", showarrow=False, font=dict(color='#2D3748'))
        
        fig5.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            title_font=dict(color='#2D3748', size=18),
            font=dict(color='#2D3748')
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Gráfico de taxa de acerto por questão
        fig6 = go.Figure()
        
        fig6.add_trace(go.Bar(
            x=questoes_avaliacao['Questão'],
            y=questoes_avaliacao['% Acerto'],
            text=questoes_avaliacao['% Acerto'].round(1).astype(str) + '%',
            textposition='outside',
            textfont=dict(color='#2D3748', size=12),
            marker_color='#10b981',
            marker=dict(
                line=dict(width=1, color='darkgreen')
            ),
            width=0.6
        ))
        
        fig6.update_layout(
            title=dict(
                text=f'Taxa de Acerto por Questão - {avaliacao_selecionada}',
                font=dict(color='#2D3748', size=18)
            ),
            xaxis_title='Questão',
            yaxis_title='% de Acerto',
            yaxis_range=[0, 105],
            height=400,
            bargap=0.4,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                tickfont=dict(color='#2D3748')
            ),
            font=dict(color='#2D3748')
        )
        
        # Adicionar linha da média
        media_acerto = questoes_avaliacao['% Acerto'].mean()
        fig6.add_hline(
            y=media_acerto,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Média: {media_acerto:.1f}%",
            annotation_position="top right"
        )
        
        st.plotly_chart(fig6, use_container_width=True)

# Análise de Tutores
if df_tutores is not None and not df_tutores.empty:
    st.markdown('<h2 class="sub-header">👨‍🏫 Análise de Tutores</h2>', unsafe_allow_html=True)
    
    # Filtrar tutores da avaliação selecionada
    tutores_avaliacao = df_tutores[df_tutores['Avaliação'] == avaliacao_selecionada]
    
    if not tutores_avaliacao.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏅 Top Tutores")
            st.dataframe(
                tutores_avaliacao[['Posição', 'Aluno', 'Proficiência', 'Pontuação Total', 'Score_Tutor']]
                .sort_values('Posição')
                .style.format({
                    'Proficiência': '{:.3f}',
                    'Score_Tutor': '{:.3f}'
                }),
                use_container_width=True
            )
        
        with col2:
            # Gráfico de score dos tutores
            fig7 = go.Figure()
            
            fig7.add_trace(go.Bar(
                x=tutores_avaliacao['Aluno'],
                y=tutores_avaliacao['Score_Tutor'],
                text=tutores_avaliacao['Score_Tutor'].round(3),
                textposition='outside',
                textfont=dict(color='#2D3748', size=12),
                marker_color='#8b5cf6',
                marker=dict(
                    line=dict(width=1, color='darkviolet')
                ),
                width=0.6
            ))
            
            fig7.update_layout(
                title=dict(
                    text=f'Score dos Tutores - {avaliacao_selecionada}',
                    font=dict(color='#2D3748', size=18)
                ),
                xaxis_title='Aluno',
                yaxis_title='Score Tutor',
                yaxis_range=[0, 1],
                height=400,
                bargap=0.4,
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    tickfont=dict(color='#2D3748')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    tickfont=dict(color='#2D3748')
                ),
                font=dict(color='#2D3748')
            )
            
            st.plotly_chart(fig7, use_container_width=True)

# Análise longitudinal (se houver múltiplas avaliações)
if len(dados) > 1:
    st.markdown('<h2 class="sub-header">📈 Análise Longitudinal</h2>', unsafe_allow_html=True)
    
    # Selecionar aluno para análise longitudinal
    aluno_selecionado = st.selectbox(
        "Selecione um aluno para análise longitudinal:",
        options=df_alunos['Aluno'].unique(),
        key="select_aluno"
    )
    
    if aluno_selecionado:
        # Filtrar dados do aluno
        dados_aluno = df_alunos[df_alunos['Aluno'] == aluno_selecionado]
        
        fig8 = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Evolução da Proficiência', 'Evolução do % de Acerto'),
            shared_xaxes=True
        )
        
        # Gráfico de evolução da proficiência
        fig8.add_trace(
            go.Scatter(
                x=dados_aluno['Avaliação'],
                y=dados_aluno['Proficiência'],
                mode='lines+markers+text',
                name='Proficiência',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=10),
                text=dados_aluno['Proficiência'].round(3),
                textposition='top center'
            ),
            row=1, col=1
        )
        
        # Gráfico de evolução do % de acerto
        fig8.add_trace(
            go.Scatter(
                x=dados_aluno['Avaliação'],
                y=dados_aluno['% Acerto'],
                mode='lines+markers+text',
                name='% Acerto',
                line=dict(color='#10b981', width=3),
                marker=dict(size=10),
                text=dados_aluno['% Acerto'].round(1).astype(str) + '%',
                textposition='top center'
            ),
            row=1, col=2
        )
        
        fig8.update_layout(
            height=400,
            title_text=f'Evolução do Desempenho - {aluno_selecionado}',
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font=dict(color='#2D3748', size=18),
            font=dict(color='#2D3748')
        )
        
        fig8.update_yaxes(
            title_text="Proficiência (θ)", 
            row=1, col=1, 
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        )
        fig8.update_yaxes(
            title_text="% de Acerto", 
            row=1, col=2, 
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            tickfont=dict(color='#2D3748')
        )
        fig8.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray', 
            row=1, col=1,
            tickfont=dict(color='#2D3748')
        )
        fig8.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray', 
            row=1, col=2,
            tickfont=dict(color='#2D3748')
        )
        
        st.plotly_chart(fig8, use_container_width=True)

# Informações adicionais
st.markdown("---")
expander = st.expander("📚 Informações sobre as Métricas")
with expander:
    st.markdown("""
    ### 📊 Glossário de Métricas
    
    **Proficiência (θ):**
    - Mede a habilidade do aluno na escala do TRI
    - Valores típicos entre -3 e +3
    - Média = 0, Desvio Padrão = 1
    
    **Dificuldade (b):**
    - Mede o quão difícil é uma questão
    - Valores negativos = mais fáceis
    - Valores positivos = mais difíceis
    
    **Discriminação (a):**
    - Mede o quanto a questão diferencia alunos bons e ruins
    - Valores > 1 = boa discriminação
    - Valores < 0.5 = pouca discriminação
    
    **Correlação Bisserial:**
    - Mede a relação entre acerto na questão e proficiência total
    - Valores próximos de 1 = questão bem discriminativa
    
    **Confiabilidade:**
    - Mede a consistência interna da avaliação
    - Valores > 0.7 = aceitável
    - Valores > 0.8 = bom
    - Valores > 0.9 = excelente
    
    **Z-Score:**
    - Mede quantos desvios padrão um aluno está acima/abaixo da média
    - Z-Score positivo = acima da média
    - Z-Score negativo = abaixo da média
    """)

# Seção de exportação de relatórios
st.markdown("---")
st.markdown('<h2 class="sub-header">📥 Exportação de Relatórios</h2>', unsafe_allow_html=True)

col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    if st.button("📊 Exportar Relatório JSON", use_container_width=True):
        # Criar relatório consolidado JSON
        relatorio = {
            "data_geracao": datetime.now().isoformat(),
            "total_avaliacoes": len(dados),
            "total_alunos_unicos": df_alunos['Aluno'].nunique(),
            "metricas_gerais": {
                "proficiencia_media_geral": float(df_avaliacoes['Proficiência Média'].mean()),
                "taxa_acerto_media_geral": float(df_avaliacoes['Taxa Acerto Média'].mean()),
                "confiabilidade_media": float(df_avaliacoes['Confiabilidade'].mean())
            },
            "melhores_alunos": df_alunos.groupby('Aluno')['Proficiência'].mean().nlargest(5).to_dict(),
            "avaliacoes_detalhadas": avaliacoes_info
        }
        
        # Converter para JSON
        json_relatorio = json.dumps(relatorio, indent=2, ensure_ascii=False)
        
        # Disponibilizar para download
        st.download_button(
            label="📥 Baixar JSON",
            data=json_relatorio,
            file_name=f"relatorio_avaliacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

with col_export2:
    if st.button("📈 Exportar Relatório CSV", use_container_width=True):
        # Criar múltiplos DataFrames para CSV
        csv_data = {
            "avaliacoes.csv": df_avaliacoes.to_csv(index=False),
            "alunos.csv": df_alunos.to_csv(index=False),
            "questoes.csv": df_questoes.to_csv(index=False)
        }
        
        if df_tutores is not None and not df_tutores.empty:
            csv_data["tutores.csv"] = df_tutores.to_csv(index=False)
        
        # Criar um arquivo ZIP com todos os CSVs
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, csv_content in csv_data.items():
                zip_file.writestr(filename, csv_content)
        
        zip_buffer.seek(0)
        
        st.download_button(
            label="📥 Baixar ZIP com CSVs",
            data=zip_buffer,
            file_name=f"relatorio_avaliacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )

with col_export3:
    if st.button("📝 Exportar Relatório TXT", use_container_width=True):
        # Criar relatório em formato texto
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        txt_content = f"""
{'='*60}
RELATÓRIO DE ANÁLISE DE AVALIAÇÕES
Data de geração: {timestamp}
{'='*60}

RESUMO GERAL:
-------------
• Total de Avaliações: {len(dados)}
• Total de Alunos Únicos: {df_alunos['Aluno'].nunique()}
• Proficiência Média Geral: {df_avaliacoes['Proficiência Média'].mean():.3f}
• Taxa de Acerto Média: {df_avaliacoes['Taxa Acerto Média'].mean():.1f}%
• Confiabilidade Média: {df_avaliacoes['Confiabilidade'].mean():.3f}

DETALHES DAS AVALIAÇÕES:
------------------------
"""
        
        for idx, avaliacao in enumerate(avaliacoes_info, 1):
            txt_content += f"""
{idx}. {avaliacao['Avaliação']}:
    • Data da Análise: {avaliacao['Data Análise']}
    • Total de Alunos: {avaliacao['Total Alunos']}
    • Total de Questões: {avaliacao['Total Questões']}
    • Proficiência Média: {avaliacao['Proficiência Média']:.3f}
    • Taxa de Acerto Média: {avaliacao['Taxa Acerto Média']:.1f}%
    • Desvio Padrão: {avaliacao['Desvio Padrão']:.3f}
    • Confiabilidade: {avaliacao['Confiabilidade']:.3f}
"""
        
        # Adicionar ranking dos melhores alunos
        txt_content += f"""

TOP 5 ALUNOS (PROFICIÊNCIA MÉDIA):
---------------------------------
"""
        top_alunos = df_alunos.groupby('Aluno')['Proficiência'].mean().nlargest(5)
        for i, (aluno, proficiencia) in enumerate(top_alunos.items(), 1):
            txt_content += f"{i}. {aluno}: {proficiencia:.3f}\n"
        
        # Adicionar estatísticas das questões
        if not df_questoes.empty:
            txt_content += f"""

ESTATÍSTICAS DAS QUESTÕES:
-------------------------
• Questão mais fácil: {df_questoes.loc[df_questoes['% Acerto'].idxmax(), 'Questão']} ({df_questoes['% Acerto'].max():.1f}%)
• Questão mais difícil: {df_questoes.loc[df_questoes['% Acerto'].idxmin(), 'Questão']} ({df_questoes['% Acerto'].min():.1f}%)
• Média de discriminação: {df_questoes['Discriminação'].mean():.3f}
• Média de dificuldade: {df_questoes['Dificuldade'].mean():.3f}
"""
        
        # Adicionar análise de tutores se disponível
        if df_tutores is not None and not df_tutores.empty:
            txt_content += f"""

ANÁLISE DE TUTORES:
------------------
• Total de tutores identificados: {df_tutores['Aluno'].nunique()}
• Score médio dos tutores: {df_tutores['Score_Tutor'].mean():.3f}
"""
        
        txt_content += f"""

{'='*60}
Relatório gerado automaticamente pelo Dashboard de Análise
{'='*60}
"""
        
        st.download_button(
            label="📥 Baixar TXT",
            data=txt_content,
            file_name=f"relatorio_avaliacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Exportação individual de DataFrames
st.markdown("### 📋 Exportar DataFrames Individuais")

col_df1, col_df2, col_df3, col_df4 = st.columns(4)

with col_df1:
    # Exportar DataFrame de avaliações
    csv_avaliacoes = df_avaliacoes.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Avaliações (CSV)",
        data=csv_avaliacoes,
        file_name="avaliacoes.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_df2:
    # Exportar DataFrame de alunos
    csv_alunos = df_alunos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="👥 Alunos (CSV)",
        data=csv_alunos,
        file_name="alunos.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_df3:
    # Exportar DataFrame de questões
    csv_questoes = df_questoes.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="❓ Questões (CSV)",
        data=csv_questoes,
        file_name="questoes.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_df4:
    # Exportar DataFrame de tutores (se existir)
    if df_tutores is not None and not df_tutores.empty:
        csv_tutores = df_tutores.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="👨‍🏫 Tutores (CSV)",
            data=csv_tutores,
            file_name="tutores.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Sem dados de tutores")

# Rodapé
st.markdown("---")
st.markdown(
    "<div class='footer'>"
    "📊 Dashboard de Análise de Avaliações | Desenvolvido com Streamlit "
    "</div>",
    unsafe_allow_html=True
)
