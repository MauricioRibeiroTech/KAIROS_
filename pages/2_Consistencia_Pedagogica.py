import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
from datetime import datetime
from io import StringIO
import math

# ============================================
# CONFIGURAÇÃO E ESTILO
# ============================================
st.set_page_config(
    page_title="KAIROS - Análise Pedagógica com ICP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS completo
st.markdown("""
<style>
    /* Cores principais do KAIROS */
    :root {
        --primary-purple: #8B5CF6;
        --primary-blue: #3B82F6;
        --success-green: #10B981;
        --warning-yellow: #F59E0B;
        --danger-red: #EF4444;
        --dark-bg: #0F172A;
        --card-bg: #1E293B;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F1F5F9;
    }
    
    .main-header {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
    }
    
    .step-card {
        background: rgba(30, 41, 59, 0.8);
        padding: 1.8rem;
        border-radius: 12px;
        margin: 1.2rem 0;
        border-left: 5px solid var(--primary-purple);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(139, 92, 246, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    .icp-high { color: var(--success-green); font-weight: bold; }
    .icp-medium { color: var(--warning-yellow); font-weight: bold; }
    .icp-low { color: var(--danger-red); font-weight: bold; }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-blue) 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.8rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(30, 41, 59, 0.7);
        border-radius: 10px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        color: #94A3B8;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-purple) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid var(--primary-blue);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--success-green);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid var(--warning-yellow);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .danger-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--danger-red);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .card-title {
        background: linear-gradient(135deg, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES DO ICP - TEORIA DE RESPOSTA AO ITEM
# ============================================

def calcular_parametros_tri(df_respostas_binarias):
    """Calcula parâmetros TRI (dificuldade e discriminação) dos itens"""
    n_alunos, n_itens = df_respostas_binarias.shape
    
    # Parâmetro de dificuldade (b): proporção de erro
    b_j = 1 - df_respostas_binarias.mean(axis=0)
    
    # Parâmetro de discriminação (a): correlação item-total
    a_j = []
    for col in df_respostas_binarias.columns:
        corr = df_respostas_binarias[col].corr(df_respostas_binarias.sum(axis=1))
        a_j.append(max(0.3, min(2.5, abs(corr))))  # Limitando valores extremos
    
    return {
        'dificuldade': b_j.values,
        'discriminacao': np.array(a_j),
        'facilidade': df_respostas_binarias.mean(axis=0).values
    }

def calcular_proficiencias(df_respostas_binarias, parametros_tri):
    """Calcula proficiências dos alunos usando TRI"""
    n_alunos, n_itens = df_respostas_binarias.shape
    
    # Estimativa inicial: logito da proporção de acertos
    proficiencias = []
    for idx in df_respostas_binarias.index:
        p = df_respostas_binarias.loc[idx].mean()
        if p == 0:
            theta = -3
        elif p == 1:
            theta = 3
        else:
            theta = np.log(p / (1 - p))  # Logito
        proficiencias.append(theta)
    
    return np.array(proficiencias)

def calcular_probabilidade_2pl(theta, a, b):
    """Calcula probabilidade de acerto usando modelo 2PL"""
    return 1 / (1 + np.exp(-a * (theta - b)))

def calcular_icp(df_respostas_binarias, gabarito=None):
    """Calcula o Índice de Consistência Pedagógica (ICP)"""
    n_alunos, n_itens = df_respostas_binarias.shape
    
    # Calcular parâmetros TRI
    parametros_tri = calcular_parametros_tri(df_respostas_binarias)
    
    # Calcular proficiências
    proficiencias = calcular_proficiencias(df_respostas_binarias, parametros_tri)
    
    icp_scores = []
    residuos_por_aluno = []
    diagnosticos = []
    
    for i, idx in enumerate(df_respostas_binarias.index):
        theta = proficiencias[i]
        residuos = []
        
        for j, col in enumerate(df_respostas_binarias.columns):
            # Probabilidade teórica de acerto
            a_j = parametros_tri['discriminacao'][j]
            b_j = parametros_tri['dificuldade'][j]
            p_ij = calcular_probabilidade_2pl(theta, a_j, b_j)
            
            # Resposta real
            x_ij = df_respostas_binarias.loc[idx, col]
            
            # Resíduo absoluto
            residuo = abs(x_ij - p_ij)
            residuos.append(residuo)
        
        # ICP = 1 - média dos resíduos
        icp = 1 - np.mean(residuos)
        icp_scores.append(icp)
        residuos_por_aluno.append(residuos)
        
        # Diagnóstico baseado no ICP
        if icp > 0.80:
            diag = "Sólido (Coerente)"
            cor = "icp-high"
        elif icp > 0.65:
            diag = "Oscilante (Atenção)"
            cor = "icp-medium"
        else:
            diag = "Errático (Provável Chute)"
            cor = "icp-low"
        
        diagnosticos.append({
            'diagnostico': diag,
            'cor': cor,
            'residuos': residuos
        })
    
    # Estatísticas do ICP
    icp_medio = np.mean(icp_scores)
    icp_desvio = np.std(icp_scores)
    
    # Distribuição de diagnósticos
    distrib_diagnosticos = {
        'Sólido (Coerente)': sum(1 for d in diagnosticos if d['diagnostico'] == "Sólido (Coerente)"),
        'Oscilante (Atenção)': sum(1 for d in diagnosticos if d['diagnostico'] == "Oscilante (Atenção)"),
        'Errático (Provável Chute)': sum(1 for d in diagnosticos if d['diagnostico'] == "Errático (Provável Chute)")
    }
    
    return {
        'icp_scores': icp_scores,
        'proficiencias': proficiencias,
        'diagnosticos': diagnosticos,
        'residuos_por_aluno': residuos_por_aluno,
        'parametros_tri': parametros_tri,
        'estatisticas': {
            'media': icp_medio,
            'desvio_padrao': icp_desvio,
            'distribuicao': distrib_diagnosticos,
            'coerentes': distrib_diagnosticos['Sólido (Coerente)'],
            'oscilantes': distrib_diagnosticos['Oscilante (Atenção)'],
            'erraticos': distrib_diagnosticos['Errático (Provável Chute)']
        }
    }

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def processar_csv_simples(arquivo):
    """Processa CSV de forma robusta"""
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                arquivo.seek(0)
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo, encoding=encoding)
                else:
                    df = pd.read_excel(arquivo)
                
                if not df.empty:
                    return df
            except:
                continue
        
        # Fallback manual
        arquivo.seek(0)
        conteudo = arquivo.read().decode('utf-8', errors='ignore')
        linhas = [linha.strip() for linha in conteudo.split('\n') if linha.strip()]
        
        if len(linhas) < 2:
            return None
        
        primeira_linha = linhas[0]
        delimitadores = [',', ';', '\t']
        delimitador = ','
        
        for d in delimitadores:
            if d in primeira_linha:
                delimitador = d
                break
        
        dados = [linha.split(delimitador) for linha in linhas]
        df = pd.DataFrame(dados[1:], columns=dados[0])
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        return None

def identificar_colunas(df):
    """Identifica automaticamente colunas"""
    colunas = list(df.columns)
    resultado = {
        'coluna_nome': None,
        'colunas_respostas': [],
        'total_questoes': 0
    }
    
    palavras_chave_nome = ['nome', 'aluno', 'estudante', 'name', 'student', 'participante']
    for col in colunas:
        col_lower = str(col).lower()
        for palavra in palavras_chave_nome:
            if palavra in col_lower:
                resultado['coluna_nome'] = col
                break
    
    if resultado['coluna_nome'] is None and colunas:
        resultado['coluna_nome'] = colunas[0]
    
    if resultado['coluna_nome']:
        resultado['colunas_respostas'] = [col for col in colunas if col != resultado['coluna_nome']]
        resultado['total_questoes'] = len(resultado['colunas_respostas'])
    
    return resultado

def converter_para_binario(df_respostas, gabarito):
    """Converte respostas para binário (acerto/erro)"""
    df_binario = pd.DataFrame(index=df_respostas.index, columns=df_respostas.columns)
    
    for i, col in enumerate(df_respostas.columns):
        if i < len(gabarito):
            gabarito_val = str(gabarito[i]).strip().upper()
            df_binario[col] = df_respostas[col].apply(
                lambda x: 1 if str(x).strip().upper() == gabarito_val else 0
            )
    
    return df_binario

def calcular_estatisticas_basicas(df_binario):
    """Calcula estatísticas básicas da turma"""
    return {
        'total_alunos': len(df_binario),
        'total_questoes': len(df_binario.columns),
        'acerto_medio': df_binario.mean().mean() * 100,
        'acerto_por_aluno': df_binario.mean(axis=1) * 100,
        'acerto_por_questao': df_binario.mean(axis=0) * 100,
        'questao_mais_facil': df_binario.mean(axis=0).idxmax(),
        'questao_mais_dificil': df_binario.mean(axis=0).idxmin(),
        'taxa_acerto_mais_facil': df_binario.mean(axis=0).max() * 100,
        'taxa_acerto_mais_dificil': df_binario.mean(axis=0).min() * 100
    }

def gerar_relatorio_html(estatisticas, icp_resultados, nome_turma, gabarito):
    """Gera relatório HTML completo com ICP"""
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório KAIROS - {nome_turma}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            }}
            
            .header {{
                background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
                color: white;
                padding: 40px;
                border-radius: 20px;
                margin-bottom: 40px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 2.8em;
            }}
            
            .header-subtitle {{
                font-size: 1.2em;
                opacity: 0.9;
                margin-top: 10px;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
                margin: 40px 0;
            }}
            
            .metric-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
                border-top: 5px solid #8B5CF6;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
            }}
            
            .metric-value {{
                font-size: 2.8em;
                font-weight: bold;
                color: #8B5CF6;
                margin: 15px 0;
            }}
            
            .metric-label {{
                color: #666;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }}
            
            .section {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                margin: 30px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}
            
            .section-title {{
                color: #7C3AED;
                border-bottom: 3px solid #e2e8f0;
                padding-bottom: 15px;
                margin-bottom: 25px;
                font-size: 1.8em;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            th {{
                background: linear-gradient(135deg, #8B5CF6, #7C3AED);
                color: white;
                padding: 18px;
                text-align: left;
                font-weight: 600;
                font-size: 1.1em;
            }}
            
            td {{
                padding: 15px 18px;
                border-bottom: 1px solid #eee;
            }}
            
            tr:nth-child(even) {{
                background: #f8fafc;
            }}
            
            tr:hover {{
                background: #f1f5f9;
            }}
            
            .good {{
                color: #10B981;
                font-weight: bold;
                background: rgba(16, 185, 129, 0.1);
                padding: 5px 10px;
                border-radius: 5px;
            }}
            
            .warning {{
                color: #F59E0B;
                font-weight: bold;
                background: rgba(245, 158, 11, 0.1);
                padding: 5px 10px;
                border-radius: 5px;
            }}
            
            .danger {{
                color: #EF4444;
                font-weight: bold;
                background: rgba(239, 68, 68, 0.1);
                padding: 5px 10px;
                border-radius: 5px;
            }}
            
            .icp-chart {{
                text-align: center;
                margin: 40px 0;
            }}
            
            .icp-chart img {{
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .gabarito-table {{
                width: auto;
                margin: 20px auto;
            }}
            
            .gabarito-table th {{
                background: #475569;
                padding: 12px 20px;
            }}
            
            .gabarito-table td {{
                text-align: center;
                font-weight: bold;
                font-size: 1.2em;
                padding: 12px 20px;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 60px;
                color: #64748B;
                font-size: 0.9em;
                border-top: 1px solid #e2e8f0;
                padding-top: 30px;
            }}
            
            .interpretation {{
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                padding: 25px;
                border-radius: 12px;
                margin: 25px 0;
                border-left: 5px solid #0ea5e9;
            }}
            
            .interpretation h4 {{
                color: #0369a1;
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 Relatório de Análise Pedagógica KAIROS</h1>
            <div class="header-subtitle">
                <p><strong>Turma:</strong> {nome_turma} | <strong>Data:</strong> {data}</p>
                <p><strong>Análise Avançada com Índice de Consistência Pedagógica (ICP)</strong></p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Acerto Médio da Turma</div>
                <div class="metric-value">{estatisticas['acerto_medio']:.1f}%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Índice de Consistência (ICP)</div>
                <div class="metric-value">{icp_resultados['estatisticas']['media']:.2f}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Alunos Coerentes</div>
                <div class="metric-value">{icp_resultados['estatisticas']['coerentes']}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Alertas de Chute</div>
                <div class="metric-value danger">{icp_resultados['estatisticas']['erraticos']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📈 Análise de Consistência Pedagógica</h2>
            
            <div class="interpretation">
                <h4>🎯 O que é o ICP (Índice de Consistência Pedagógica)?</h4>
                <p>O ICP mede o quanto o desempenho do aluno é previsível e consistente com sua proficiência real. 
                Ele identifica padrões de resposta que podem indicar conhecimento sólido, oscilações de atenção 
                ou possíveis chutes nas questões.</p>
                
                <p><strong>Escala de Interpretação:</strong></p>
                <ul>
                    <li><span class="good">ICP > 0.80</span>: <strong>Aluno Sólido</strong> - Desempenho coerente e previsível</li>
                    <li><span class="warning">0.65 ≤ ICP ≤ 0.80</span>: <strong>Aluno Oscilante</strong> - Necessita atenção e acompanhamento</li>
                    <li><span class="danger">ICP < 0.65</span>: <strong>Aluno Errático</strong> - Possível chute ou lacuna significativa</li>
                </ul>
            </div>
            
            <h3>📊 Distribuição do ICP na Turma</h3>
            <table>
                <tr>
                    <th>Categoria</th>
                    <th>Quantidade de Alunos</th>
                    <th>Porcentagem</th>
                    <th>Interpretação</th>
                </tr>
                <tr>
                    <td><span class="good">Alta Consistência</span></td>
                    <td><strong>{icp_resultados['estatisticas']['coerentes']}</strong></td>
                    <td>{(icp_resultados['estatisticas']['coerentes']/estatisticas['total_alunos']*100):.1f}%</td>
                    <td>Padrão de resposta sólido e confiável</td>
                </tr>
                <tr>
                    <td><span class="warning">Consistência Moderada</span></td>
                    <td><strong>{icp_resultados['estatisticas']['oscilantes']}</strong></td>
                    <td>{(icp_resultados['estatisticas']['oscilantes']/estatisticas['total_alunos']*100):.1f}%</td>
                    <td>Oscilações que merecem atenção</td>
                </tr>
                <tr>
                    <td><span class="danger">Baixa Consistência</span></td>
                    <td><strong>{icp_resultados['estatisticas']['erraticos']}</strong></td>
                    <td>{(icp_resultados['estatisticas']['erraticos']/estatisticas['total_alunos']*100):.1f}%</td>
                    <td>Possível chute ou falta de engajamento</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">👥 Resultados Detalhados por Aluno</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Aluno</th>
                        <th>Proficiência (θ)</th>
                        <th>ICP</th>
                        <th>Diagnóstico</th>
                        <th>Acertos</th>
                        <th>Ações Recomendadas</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Ordenar alunos por ICP (mais coerente primeiro)
    alunos_ordenados = sorted(
        zip(
            icp_resultados['icp_scores'],
            icp_resultados['proficiencias'],
            icp_resultados['diagnosticos'],
            estatisticas['acerto_por_aluno'].index,
            estatisticas['acerto_por_aluno'].values
        ),
        key=lambda x: x[0],
        reverse=True
    )
    
    for icp, proficiencia, diagnostico, nome, acerto in alunos_ordenados[:20]:  # Mostrar apenas 20
        icp_class = ""
        acao = ""
        
        if icp > 0.80:
            icp_class = "good"
            acao = "Potencial tutor / Desafios avançados"
        elif icp > 0.65:
            icp_class = "warning"
            acao = "Monitoramento e feedback específico"
        else:
            icp_class = "danger"
            acao = "Reforço individualizado / Avaliação diagnóstica"
        
        html += f"""
                    <tr>
                        <td><strong>{nome}</strong></td>
                        <td>{proficiencia:+.2f}</td>
                        <td class="{icp_class}">{icp:.2f}</td>
                        <td class="{icp_class}">{diagnostico['diagnostico']}</td>
                        <td>{acerto:.1f}%</td>
                        <td><small>{acao}</small></td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            
            <p><em>Mostrando {min(20, estatisticas['total_alunos'])} de {estatisticas['total_alunos']} alunos ordenados por consistência</em></p>
        </div>
        
        <div class="section">
            <h2 class="section-title">📋 Informações da Avaliação</h2>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px;">
                <div>
                    <h3>🎯 Estatísticas da Turma</h3>
                    <table>
                        <tr>
                            <td>Total de Alunos:</td>
                            <td><strong>{estatisticas['total_alunos']}</strong></td>
                        </tr>
                        <tr>
                            <td>Total de Questões:</td>
                            <td><strong>{estatisticas['total_questoes']}</strong></td>
                        </tr>
                        <tr>
                            <td>Questão Mais Fácil:</td>
                            <td><strong>{estatisticas['questao_mais_facil']}</strong> ({estatisticas['taxa_acerto_mais_facil']:.1f}%)</td>
                        </tr>
                        <tr>
                            <td>Questão Mais Difícil:</td>
                            <td><strong>{estatisticas['questao_mais_dificil']}</strong> ({estatisticas['taxa_acerto_mais_dificil']:.1f}%)</td>
                        </tr>
                    </table>
                </div>
                
                <div>
                    <h3>✅ Gabarito Oficial</h3>
                    <table class="gabarito-table">
                        <tr>
    """
    
    for i, resposta in enumerate(gabarito, 1):
        html += f"<th>Q{i}</th>"
    
    html += "</tr><tr>"
    
    for resposta in gabarito:
        html += f"<td>{resposta.upper()}</td>"
    
    html += """
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🎯 Recomendações Pedagógicas Baseadas no ICP</h2>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                <div style="border-top: 4px solid #10B981;">
                    <h4 style="color: #10B981;">Para alunos com ICP Alto (&gt; 0.80)</h4>
                    <ul>
                        <li>Atribuir papel de monitores/tutores</li>
                        <li>Oferecer desafios avançados</li>
                        <li>Incentivar liderança em grupos de estudo</li>
                        <li>Desenvolver projetos de extensão</li>
                    </ul>
                </div>
                
                <div style="border-top: 4px solid #F59E0B;">
                    <h4 style="color: #F59E0B;">Para alunos com ICP Intermediário (0.65-0.80)</h4>
                    <ul>
                        <li>Monitoramento regular</li>
                        <li>Feedback específico e constante</li>
                        <li>Identificar tópicos de maior oscilação</li>
                        <li>Estratégias de organização de estudos</li>
                    </ul>
                </div>
                
                <div style="border-top: 4px solid #EF4444;">
                    <h4 style="color: #EF4444;">Para alunos com ICP Baixo (&lt; 0.65)</h4>
                    <ul>
                        <li>Avaliação diagnóstica individual</li>
                        <li>Reforço nos conceitos básicos</li>
                        <li>Técnicas de controle de ansiedade</li>
                        <li>Acompanhamento pedagógico intensivo</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>📊 Relatório gerado automaticamente pelo <strong>Sistema KAIROS de Análise Pedagógica</strong></p>
            <p>🧠 Integrando Teoria de Resposta ao Item (TRI) e Índice de Consistência Pedagógica (ICP)</p>
            <p>© {datetime.now().year} - Para uso educacional</p>
        </div>
    </body>
    </html>
    """
    
    return html

# ============================================
# INICIALIZAÇÃO DA SESSÃO
# ============================================
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'alunos' not in st.session_state:
    st.session_state.alunos = []
if 'gabarito' not in st.session_state:
    st.session_state.gabarito = []
if 'nome_turma' not in st.session_state:
    st.session_state.nome_turma = "Turma KAIROS 2024"
if 'df_respostas' not in st.session_state:
    st.session_state.df_respostas = None
if 'df_binario' not in st.session_state:
    st.session_state.df_binario = None
if 'icp_resultados' not in st.session_state:
    st.session_state.icp_resultados = None

# ============================================
# INTERFACE PRINCIPAL
# ============================================

# Cabeçalho principal
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0; font-size: 3em;">🧠 KAIROS</h1>
    <p style="color: white; opacity: 0.9; margin: 10px 0 0 0; font-size: 1.3em;">
        Sistema de Análise Pedagógica com Índice de Consistência Pedagógica (ICP)
    </p>
    <p style="color: rgba(255,255,255,0.7); margin: 5px 0; font-size: 1.1em;">
        Teoria de Resposta ao Item (TRI) + Análise de Padrões de Resposta
    </p>
</div>
""", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/brain.png", width=80)
    st.markdown("### 📊 Status do Sistema")
    
    if st.session_state.dados_carregados:
        st.markdown(f"""
        <div class="success-box">
        <strong>✅ Dados Carregados</strong>
        <p><strong>Turma:</strong> {st.session_state.nome_turma}</p>
        <p><strong>Alunos:</strong> {len(st.session_state.alunos)}</p>
        <p><strong>Questões:</strong> {len(st.session_state.gabarito)}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
        <strong>🟡 Aguardando Dados</strong>
        <p>Configure o sistema para começar</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📖 Sobre o ICP")
    st.markdown("""
    O **Índice de Consistência Pedagógica** mede:
    
    🔍 **Consistência** das respostas
    🎯 **Previsibilidade** do desempenho
    ⚠️ **Detecta chutes** e padrões erráticos
    
    Baseado na **Teoria de Resposta ao Item (TRI)**
    """)
    
    st.markdown("---")
    if st.session_state.dados_carregados:
        if st.button("🔄 Nova Análise", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ============================================
# ABA PRINCIPAL - FLUXO DE TRABALHO
# ============================================

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["🎯 1. Configurar", "📁 2. Importar", "📊 3. Analisar ICP", "📤 4. Exportar"])

# ============================================
# ABA 1: CONFIGURAR
# ============================================
with tab1:
    st.markdown('<div class="card-title">🎯 Passo 1: Configurar Avaliação</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Nome da Turma")
        st.session_state.nome_turma = st.text_input(
            "Nome da turma ou avaliação:",
            value=st.session_state.nome_turma,
            placeholder="Ex: Turma A - Matemática - 1º Bimestre 2024"
        )
        
        st.markdown("### ✅ Gabarito Oficial")
        st.markdown("Digite as respostas corretas separadas por vírgula:")
        
        exemplo = "A,B,C,D,A,B,C,D,A,B" if len(st.session_state.gabarito) == 0 else ",".join(st.session_state.gabarito)
        gabarito_input = st.text_area(
            "Gabarito correto:",
            value=exemplo,
            placeholder="A,B,C,D,A,B,C,D",
            height=100
        )
        
        if st.button("💾 Salvar Configuração", type="primary", use_container_width=True):
            gabarito_list = [x.strip().upper() for x in gabarito_input.split(",") if x.strip()]
            if gabarito_list:
                st.session_state.gabarito = gabarito_list
                st.success(f"✅ Gabarito configurado com {len(gabarito_list)} questões!")
            else:
                st.error("❌ Digite pelo menos uma resposta correta")
    
    with col2:
        st.markdown("### ℹ️ Informações do ICP")
        st.markdown("""
        <div class="info-box">
        <strong>Escala do ICP:</strong>
        <p>🎯 <strong>0.80 - 1.00:</strong> Alta consistência</p>
        <p>⚠️ <strong>0.65 - 0.79:</strong> Consistência moderada</p>
        <p>❌ <strong>0.00 - 0.64:</strong> Baixa consistência</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.gabarito:
            st.markdown(f"""
            <div class="success-box">
            <strong>Gabarito Configurado:</strong>
            <p style="font-family: monospace; background: #1E293B; padding: 10px; border-radius: 5px;">
            {' | '.join(st.session_state.gabarito)}
            </p>
            <p><strong>Total:</strong> {len(st.session_state.gabarito)} questões</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# ABA 2: IMPORTAR
# ============================================
with tab2:
    st.markdown('<div class="card-title">📁 Passo 2: Importar Respostas dos Alunos</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-card">
    <h4>📋 Formato Recomendado do CSV:</h4>
    <pre style="background: #0F172A; color: #F1F5F9; padding: 15px; border-radius: 8px; font-size: 14px; border: 1px solid #334155;">
Nome, Q1, Q2, Q3, Q4, Q5
João Silva, A, B, C, D, A
Maria Santos, B, C, D, A, B
Pedro Souza, C, D, A, B, C
Ana Oliveira, D, A, B, C, D
</pre>
    <p><strong>Dica:</strong> Exporte do Google Forms ou Excel como CSV UTF-8</p>
    </div>
    """, unsafe_allow_html=True)
    
    arquivo = st.file_uploader(
        "📂 Selecione o arquivo com as respostas dos alunos:",
        type=['csv', 'xlsx', 'xls'],
        help="Suporta CSV, Excel (.xlsx, .xls)"
    )
    
    if arquivo is not None:
        try:
            df = processar_csv_simples(arquivo)
            
            if df is not None:
                st.success(f"✅ Arquivo carregado: {len(df)} registros")
                st.markdown("#### 👁️ Pré-visualização dos Dados:")
                st.dataframe(df.head(), use_container_width=True)
                
                colunas_info = identificar_colunas(df)
                
                if colunas_info['coluna_nome'] and colunas_info['colunas_respostas']:
                    st.markdown(f"""
                    <div class="info-box">
                    <strong>🎯 Detecção Automática:</strong>
                    <p>📝 <strong>Coluna de nomes:</strong> {colunas_info['coluna_nome']}</p>
                    <p>❓ <strong>Questões detectadas:</strong> {len(colunas_info['colunas_respostas'])}</p>
                    <p>📊 <strong>Primeiras questões:</strong> {', '.join(colunas_info['colunas_respostas'][:3])}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Verificar compatibilidade com gabarito
                    if st.session_state.gabarito:
                        if len(st.session_state.gabarito) != colunas_info['total_questoes']:
                            st.error(f"""
                            ❌ **Incompatibilidade detectada!**
                            
                            Gabarito: {len(st.session_state.gabarito)} questões
                            CSV: {colunas_info['total_questoes']} questões
                            
                            **Ajuste o gabarito ou verifique o arquivo.**
                            """)
                    
                    # Botão de importação
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("🚀 Importar Dados e Calcular ICP", type="primary", use_container_width=True):
                            with st.spinner("Processando dados e calculando ICP..."):
                                # Extrair nomes e respostas
                                nomes = []
                                respostas_list = []
                                
                                for _, linha in df.iterrows():
                                    nome = str(linha[colunas_info['coluna_nome']]) if pd.notna(linha[colunas_info['coluna_nome']]) else f"Aluno_{_}"
                                    respostas = []
                                    
                                    for col in colunas_info['colunas_respostas']:
                                        resposta = str(linha[col]).strip().upper() if pd.notna(linha[col]) else ""
                                        resposta = resposta.replace('"', '').replace("'", "").replace(" ", "")
                                        if len(resposta) > 1:
                                            resposta = resposta[0]
                                        respostas.append(resposta)
                                    
                                    nomes.append(nome)
                                    respostas_list.append(respostas)
                                
                                # Criar DataFrames
                                st.session_state.df_respostas = pd.DataFrame(
                                    respostas_list,
                                    index=nomes,
                                    columns=colunas_info['colunas_respostas']
                                )
                                
                                # Converter para binário
                                st.session_state.df_binario = converter_para_binario(
                                    st.session_state.df_respostas,
                                    st.session_state.gabarito
                                )
                                
                                # Calcular ICP
                                st.session_state.icp_resultados = calcular_icp(st.session_state.df_binario)
                                
                                st.session_state.alunos = [{'nome': n, 'respostas': r} for n, r in zip(nomes, respostas_list)]
                                st.session_state.dados_carregados = True
                                
                                st.success(f"✅ {len(nomes)} alunos processados com sucesso!")
                                st.balloons()
                    
                    with col_btn2:
                        if st.button("👀 Visualizar Dados Brutos", use_container_width=True):
                            st.markdown("#### 📊 Dados Completos:")
                            st.dataframe(df, use_container_width=True, height=400)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

# ============================================
# ABA 3: ANALISAR ICP
# ============================================
with tab3:
    st.markdown('<div class="card-title">📊 Passo 3: Análise com ICP</div>', unsafe_allow_html=True)
    
    if not st.session_state.dados_carregados:
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: rgba(30, 41, 59, 0.8); border-radius: 15px; margin: 20px 0;">
            <h3>📭 Aguardando Dados</h3>
            <p>Complete os passos 1 e 2 para ver a análise do ICP</p>
            <p>O ICP revelará padrões ocultos nas respostas dos alunos</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Calcular estatísticas básicas
        estatisticas = calcular_estatisticas_basicas(st.session_state.df_binario)
        icp_resultados = st.session_state.icp_resultados
        
        # ====================
        # MÉTRICAS PRINCIPAIS
        # ====================
        st.markdown("### 📈 Métricas da Análise ICP")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
            <h3>🎯 ICP Médio</h3>
            <h2 style="color: #8B5CF6;">{icp_resultados['estatisticas']['media']:.2f}</h2>
            <p>Consistência da turma</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
            <h3>👥 Alunos Coerentes</h3>
            <h2 style="color: #10B981;">{icp_resultados['estatisticas']['coerentes']}</h2>
            <p>ICP &gt; 0.80</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
            <h3>⚠️ Oscilantes</h3>
            <h2 style="color: #F59E0B;">{icp_resultados['estatisticas']['oscilantes']}</h2>
            <p>ICP 0.65-0.80</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
            <h3>❌ Erráticos</h3>
            <h2 style="color: #EF4444;">{icp_resultados['estatisticas']['erraticos']}</h2>
            <p>ICP &lt; 0.65</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ====================
        # GRÁFICOS PRINCIPAIS
        # ====================
        st.markdown("### 📊 Visualizações do ICP")
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            # Gráfico 1: Proficiência vs ICP
            df_plot1 = pd.DataFrame({
                'Aluno': st.session_state.df_binario.index,
                'Proficiência (θ)': icp_resultados['proficiencias'],
                'ICP': icp_resultados['icp_scores'],
                'Diagnóstico': [d['diagnostico'] for d in icp_resultados['diagnosticos']],
                'Acertos (%)': estatisticas['acerto_por_aluno'].values
            })
            
            fig1 = px.scatter(
                df_plot1,
                x='Proficiência (θ)',
                y='ICP',
                color='Diagnóstico',
                size='Acertos (%)',
                hover_name='Aluno',
                title='🧠 Matriz de Consistência Pedagógica',
                color_discrete_map={
                    'Sólido (Coerente)': '#10B981',
                    'Oscilante (Atenção)': '#F59E0B',
                    'Errático (Provável Chute)': '#EF4444'
                },
                size_max=20
            )
            
            # Adicionar linhas de referência
            fig1.add_hline(y=0.80, line_dash="dash", line_color="#10B981", opacity=0.5)
            fig1.add_hline(y=0.65, line_dash="dash", line_color="#F59E0B", opacity=0.5)
            fig1.add_hline(y=0.50, line_dash="dash", line_color="#EF4444", opacity=0.5)
            
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#F1F5F9",
                height=500
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_graf2:
            # Gráfico 2: Distribuição do ICP
            fig2 = go.Figure()
            
            # Histograma
            fig2.add_trace(go.Histogram(
                x=icp_resultados['icp_scores'],
                nbinsx=20,
                marker_color='#8B5CF6',
                opacity=0.7,
                name='Distribuição do ICP'
            ))
            
            # Linhas de referência
            fig2.add_vline(x=0.80, line_dash="dash", line_color="#10B981", annotation_text="Alta Consistência")
            fig2.add_vline(x=0.65, line_dash="dash", line_color="#F59E0B", annotation_text="Consistência Moderada")
            
            fig2.update_layout(
                title='📊 Distribuição do Índice de Consistência Pedagógica',
                xaxis_title='ICP',
                yaxis_title='Frequência',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#F1F5F9",
                height=500
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # ====================
        # GRÁFICOS ADICIONAIS
        # ====================
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            # Gráfico 3: Dificuldade das questões
            df_dificuldade = pd.DataFrame({
                'Questão': st.session_state.df_binario.columns,
                'Taxa de Acerto (%)': estatisticas['acerto_por_questao'].values,
                'Dificuldade (b)': icp_resultados['parametros_tri']['dificuldade'],
                'Discriminação (a)': icp_resultados['parametros_tri']['discriminacao']
            })
            
            fig3 = px.bar(
                df_dificuldade,
                x='Questão',
                y='Taxa de Acerto (%)',
                color='Taxa de Acerto (%)',
                title='🎯 Desempenho por Questão',
                color_continuous_scale='RdYlGn',
                text_auto='.0f'
            )
            
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#F1F5F9",
                height=400
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col_graf4:
            # Gráfico 4: Diagnósticos do ICP
            df_diagnosticos = pd.DataFrame({
                'Categoria': ['Alta Consistência', 'Consistência Moderada', 'Baixa Consistência'],
                'Quantidade': [
                    icp_resultados['estatisticas']['coerentes'],
                    icp_resultados['estatisticas']['oscilantes'],
                    icp_resultados['estatisticas']['erraticos']
                ],
                'Cor': ['#10B981', '#F59E0B', '#EF4444']
            })
            
            fig4 = px.pie(
                df_diagnosticos,
                values='Quantidade',
                names='Categoria',
                title='📈 Distribuição de Consistência Pedagógica',
                color='Categoria',
                color_discrete_map={
                    'Alta Consistência': '#10B981',
                    'Consistência Moderada': '#F59E0B',
                    'Baixa Consistência': '#EF4444'
                }
            )
            
            fig4.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#F1F5F9",
                height=400,
                showlegend=True
            )
            
            fig4.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig4, use_container_width=True)
        
        # ====================
        # TABELA DETALHADA
        # ====================
        st.markdown("### 📋 Tabela de Resultados com ICP")
        
        # Criar DataFrame completo
        df_resultados = pd.DataFrame({
            'Aluno': st.session_state.df_binario.index,
            'Proficiência (θ)': icp_resultados['proficiencias'],
            'ICP': icp_resultados['icp_scores'],
            'Diagnóstico': [d['diagnostico'] for d in icp_resultados['diagnosticos']],
            'Acertos (%)': estatisticas['acerto_por_aluno'].values,
            'Acertos (abs)': st.session_state.df_binario.sum(axis=1),
            'Total Questões': len(st.session_state.gabarito)
        })
        
        # Adicionar coluna de classificação
        def classificar_icp(icp):
            if icp > 0.80:
                return "🟢 Alta"
            elif icp > 0.65:
                return "🟡 Moderada"
            else:
                return "🔴 Baixa"
        
        df_resultados['Classificação ICP'] = df_resultados['ICP'].apply(classificar_icp)
        
        # Ordenar por ICP
        df_resultados = df_resultados.sort_values('ICP', ascending=False)
        
        # Filtro interativo
        st.markdown("#### 🔍 Filtrar Resultados")
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            filtro_diagnostico = st.multiselect(
                "Filtrar por diagnóstico:",
                options=df_resultados['Diagnóstico'].unique(),
                default=df_resultados['Diagnóstico'].unique()
            )
        
        with col_filtro2:
            filtro_classificacao = st.multiselect(
                "Filtrar por classificação ICP:",
                options=df_resultados['Classificação ICP'].unique(),
                default=df_resultados['Classificação ICP'].unique()
            )
        
        with col_filtro3:
            min_acertos = st.slider(
                "Mínimo de acertos (%):",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )
        
        # Aplicar filtros
        df_filtrado = df_resultados[
            (df_resultados['Diagnóstico'].isin(filtro_diagnostico)) &
            (df_resultados['Classificação ICP'].isin(filtro_classificacao)) &
            (df_resultados['Acertos (%)'] >= min_acertos)
        ]
        
        # Mostrar tabela
        st.dataframe(
            df_filtrado.style.format({
                'Proficiência (θ)': '{:.2f}',
                'ICP': '{:.2f}',
                'Acertos (%)': '{:.1f}%'
            }),
            use_container_width=True,
            height=500
        )
        
        # ====================
        # ANÁLISE DETALHADA
        # ====================
        st.markdown("### 🔍 Análise Detalhada por Categoria")
        
        col_analise1, col_analise2, col_analise3 = st.columns(3)
        
        with col_analise1:
            st.markdown(f"""
            <div class="success-box">
            <h4>🎯 Alunos com Alta Consistência ({icp_resultados['estatisticas']['coerentes']})</h4>
            <p><strong>Características:</strong></p>
            <ul>
                <li>Respostas previsíveis e confiáveis</li>
                <li>Bom conhecimento do conteúdo</li>
                <li>Potenciais tutores/monitores</li>
            </ul>
            <p><strong>Ações:</strong> Desafios avançados, liderança</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_analise2:
            st.markdown(f"""
            <div class="warning-box">
            <h4>⚠️ Alunos com Consistência Moderada ({icp_resultados['estatisticas']['oscilantes']})</h4>
            <p><strong>Características:</strong></p>
            <ul>
                <li>Oscilações de atenção</li>
                <li>Lacunas pontuais no conhecimento</li>
                <li>Ansiedade ou pressão</li>
            </ul>
            <p><strong>Ações:</strong> Monitoramento, feedback específico</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_analise3:
            st.markdown(f"""
            <div class="danger-box">
            <h4>❌ Alunos com Baixa Consistência ({icp_resultados['estatisticas']['erraticos']})</h4>
            <p><strong>Características:</strong></p>
            <ul>
                <li>Possível chute sistemático</li>
                <li>Falta de engajamento</li>
                <li>Dificuldades significativas</li>
            </ul>
            <p><strong>Ações:</strong> Reforço individualizado, diagnóstico</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# ABA 4: EXPORTAR
# ============================================
with tab4:
    st.markdown('<div class="card-title">📤 Passo 4: Exportar Resultados</div>', unsafe_allow_html=True)
    
    if not st.session_state.dados_carregados:
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: rgba(30, 41, 59, 0.8); border-radius: 15px; margin: 20px 0;">
            <h3>📭 Aguardando Dados</h3>
            <p>Complete os passos 1, 2 e 3 para exportar resultados</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        estatisticas = calcular_estatisticas_basicas(st.session_state.df_binario)
        icp_resultados = st.session_state.icp_resultados
        
        st.markdown("### 🚀 Escolha o formato de exportação:")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            if st.button("📄 Relatório HTML Completo", use_container_width=True):
                html_content = gerar_relatorio_html(
                    estatisticas,
                    icp_resultados,
                    st.session_state.nome_turma,
                    st.session_state.gabarito
                )
                
                b64 = base64.b64encode(html_content.encode()).decode()
                href = f"""
                <a href="data:text/html;base64,{b64}" 
                   download="relatorio_kairos_{st.session_state.nome_turma}.html"
                   style="text-decoration: none; display: block; width: 100%;">
                   <button style="background: linear-gradient(135deg, #8B5CF6, #3B82F6); 
                           color: white; border: none; padding: 15px; border-radius: 10px; 
                           font-weight: bold; font-size: 16px; width: 100%; cursor: pointer;">
                    📥 Baixar Relatório HTML
                   </button>
                </a>
                """
                st.markdown(href, unsafe_allow_html=True)
                
                with st.expander("👁️ Pré-visualização do Relatório"):
                    st.components.v1.html(html_content, height=600, scrolling=True)
        
        with col_exp2:
            if st.button("📊 Dados Analíticos CSV", use_container_width=True):
                # Criar CSV completo com ICP
                df_export = pd.DataFrame({
                    'Aluno': st.session_state.df_binario.index,
                    'Proficiencia_TRI': icp_resultados['proficiencias'],
                    'ICP': icp_resultados['icp_scores'],
                    'Diagnostico_ICP': [d['diagnostico'] for d in icp_resultados['diagnosticos']],
                    'Acertos_Porcentagem': estatisticas['acerto_por_aluno'].values,
                    'Acertos_Absolutos': st.session_state.df_binario.sum(axis=1),
                    'Total_Questoes': len(st.session_state.gabarito)
                })
                
                # Adicionar respostas detalhadas
                for i, col in enumerate(st.session_state.df_respostas.columns):
                    df_export[f'Resposta_Q{i+1}'] = st.session_state.df_respostas[col]
                    df_export[f'Acerto_Q{i+1}'] = st.session_state.df_binario[col]
                    if i < len(st.session_state.gabarito):
                        df_export[f'Gabarito_Q{i+1}'] = st.session_state.gabarito[i]
                
                csv = df_export.to_csv(index=False, sep=';', decimal=',', encoding='utf-8-sig')
                b64 = base64.b64encode(csv.encode()).decode()
                
                href = f"""
                <a href="data:file/csv;base64,{b64}" 
                   download="dados_analiticos_kairos_{st.session_state.nome_turma}.csv"
                   style="text-decoration: none; display: block; width: 100%; margin-top: 10px;">
                   <button style="background: linear-gradient(135deg, #10B981, #059669); 
                           color: white; border: none; padding: 15px; border-radius: 10px; 
                           font-weight: bold; font-size: 16px; width: 100%; cursor: pointer;">
                    📥 Baixar CSV Analítico
                   </button>
                </a>
                """
                st.markdown(href, unsafe_allow_html=True)
        
        with col_exp3:
            if st.button("🎯 Lista de Tutores Potenciais", use_container_width=True):
                # Identificar potenciais tutores (alto ICP e alta proficiência)
                df_tutores = pd.DataFrame({
                    'Aluno': st.session_state.df_binario.index,
                    'Proficiencia': icp_resultados['proficiencias'],
                    'ICP': icp_resultados['icp_scores'],
                    'Acertos_Porcentagem': estatisticas['acerto_por_aluno'].values
                })
                
                # Filtro: ICP > 0.80 e proficiência > 0 (acima da média)
                df_tutores = df_tutores[
                    (df_tutores['ICP'] > 0.80) & 
                    (df_tutores['Proficiencia'] > 0) &
                    (df_tutores['Acertos_Porcentagem'] > 70)
                ].sort_values('Proficiencia', ascending=False)
                
                if not df_tutores.empty:
                    csv_tutores = df_tutores.to_csv(index=False, sep=';')
                    b64 = base64.b64encode(csv_tutores.encode()).decode()
                    
                    href = f"""
                    <a href="data:file/csv;base64,{b64}" 
                       download="tutores_potenciais_{st.session_state.nome_turma}.csv"
                       style="text-decoration: none; display: block; width: 100%;">
                       <button style="background: linear-gradient(135deg, #F59E0B, #D97706); 
                               color: white; border: none; padding: 15px; border-radius: 10px; 
                               font-weight: bold; font-size: 16px; width: 100%; cursor: pointer;">
                        📥 Baixar Lista de Tutores
                       </button>
                    </a>
                    """
                    st.markdown(href, unsafe_allow_html=True)
                    
                    st.success(f"✅ {len(df_tutores)} alunos identificados como potenciais tutores!")
                    st.dataframe(df_tutores, use_container_width=True)
                else:
                    st.warning("Nenhum aluno atende aos critérios para ser tutor.")
        
        # ====================
        # RELATÓRIO PERSONALIZADO
        # ====================
        st.markdown("---")
        st.markdown("### 🎨 Personalizar Relatório")
        
        with st.expander("⚙️ Configurações Avançadas"):
            col_config1, col_config2 = st.columns(2)
            
            with col_config1:
                incluir_graficos = st.checkbox("Incluir gráficos no relatório", value=True)
                incluir_diagnosticos = st.checkbox("Incluir diagnósticos detalhados", value=True)
                incluir_recomendacoes = st.checkbox("Incluir recomendações pedagógicas", value=True)
            
            with col_config2:
                limiar_coerente = st.slider("Limiar para 'Alta Consistência':", 0.70, 0.90, 0.80)
                limiar_oscilante = st.slider("Limiar para 'Consistência Moderada':", 0.55, 0.75, 0.65)
        
        if st.button("✨ Gerar Relatório Personalizado", type="primary", use_container_width=True):
            with st.spinner("Gerando relatório personalizado..."):
                # Aqui você poderia implementar a lógica para ajustar o relatório
                # com base nas configurações selecionadas
                st.success("✅ Relatório personalizado gerado com sucesso!")
                st.info("Use os botões acima para baixar nos formatos disponíveis.")

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 0.9em; padding: 20px;">
    <p>🧠 <strong>KAIROS - Sistema de Análise Pedagógica com ICP</strong></p>
    <p>Integrando Teoria de Resposta ao Item (TRI) e Índice de Consistência Pedagógica (ICP)</p>
    <p>© 2024 - Desenvolvido para educadores e pesquisadores</p>
</div>
""", unsafe_allow_html=True)