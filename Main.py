import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm, pearsonr
import warnings
from datetime import datetime
import io
import json
import base64
import tempfile
import zipfile
from PIL import Image

warnings.filterwarnings('ignore')

# --- Verificar dependências ---
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    st.warning("⚠️ **Aviso:** O módulo `openpyxl` não está instalado. A exportação para Excel estará limitada.")

# --- Configurações da Página ---
st.set_page_config(
    page_title="📊 KAIROS - Análise de Avaliações",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estilo CSS com Tema Escuro Elegante ---
st.markdown("""
<style>
    /* Tema Escuro Elegante */
    :root {
        --primary-purple: #8B5CF6;
        --secondary-purple: #A78BFA;
        --dark-bg: #0F172A;
        --darker-bg: #1E293B;
        --card-bg: #334155;
        --text-light: #F1F5F9;
        --text-muted: #94A3B8;
        --success-green: #10B981;
        --warning-orange: #F59E0B;
        --danger-red: #EF4444;
        --info-blue: #3B82F6;
    }
    
    /* Background principal */
    .stApp {
        background-color: var(--dark-bg);
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        color: var(--primary-purple);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
        background: linear-gradient(135deg, var(--primary-purple), var(--secondary-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: var(--text-light);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
        border-bottom: 2px solid var(--primary-purple);
        padding-bottom: 0.5rem;
    }
    
    /* Boxes e Cards */
    .info-box {
        background: linear-gradient(145deg, var(--darker-bg), var(--card-bg));
        padding: 1.8rem;
        border-radius: 12px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin-bottom: 1.5rem;
        color: var(--text-light);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .success-box {
        background: linear-gradient(145deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
        padding: 1.8rem;
        border-radius: 12px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        margin-bottom: 1.5rem;
        color: var(--text-light);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .warning-box {
        background: linear-gradient(145deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
        padding: 1.8rem;
        border-radius: 12px;
        border: 1px solid rgba(245, 158, 11, 0.3);
        margin-bottom: 1.5rem;
        color: var(--text-light);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(145deg, var(--card-bg), var(--darker-bg));
        padding: 1.8rem;
        border-radius: 12px;
        text-align: center;
        border-left: 4px solid var(--primary-purple);
        color: var(--text-light);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(139, 92, 246, 0.2);
        border-left: 4px solid var(--secondary-purple);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--darker-bg), #1a1f3a) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    /* Inputs e Selects */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background-color: var(--card-bg) !important;
        color: var(--text-light) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-purple) !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-purple), var(--secondary-purple)) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(139, 92, 246, 0.4) !important;
        background: linear-gradient(135deg, var(--secondary-purple), var(--primary-purple)) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--darker-bg) !important;
        border-radius: 12px 12px 0 0;
        padding: 8px;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-purple), var(--secondary-purple)) !important;
        color: white !important;
        box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, var(--darker-bg), var(--card-bg)) !important;
        color: var(--text-light) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--darker-bg) !important;
        color: var(--text-light) !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: var(--card-bg) !important;
        color: var(--text-light) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, var(--primary-purple), var(--secondary-purple)) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: rgba(139, 92, 246, 0.05) !important;
    }
    
    .dataframe tr:hover {
        background-color: rgba(139, 92, 246, 0.1) !important;
    }
    
    /* Texto geral */
    p, li, span, div, label {
        color: var(--text-light) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-light) !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: var(--darker-bg) !important;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    .stRadio > div > label {
        color: var(--text-light) !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(139, 92, 246, 0.3) !important;
        margin: 2rem 0 !important;
    }
    
    /* Estilo para a imagem do logo na sidebar */
    .sidebar-logo-container {
        text-align: center;
        margin: 0 auto 2rem auto;
        max-width: 100%;
    }
    
    .sidebar-logo-wrapper {
        padding: 15px;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.8));
        border-radius: 12px;
        border: 1px solid rgba(139, 92, 246, 0.5);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Funções do TRI ---
class TRI_Simulator:
    def __init__(self):
        self.ability_range = np.linspace(-4, 4, 100)

    def probability_2pl(self, theta, a, b):
        return 1 / (1 + np.exp(-a * (theta - b)))

    def fit_model(self, response_matrix):
        n_students, n_items = response_matrix.shape
        p_values = response_matrix.mean(axis=0)
        p_values = np.clip(p_values, 0.001, 0.999)
        difficulty = -np.log(p_values / (1 - p_values))
        discrimination = []
        total_scores = response_matrix.sum(axis=1)
        for i in range(n_items):
            try:
                corr = pearsonr(response_matrix[:, i], total_scores)[0]
                discrimination.append(2.5 * corr if not np.isnan(corr) else 0.5)
            except:
                discrimination.append(0.5)
        student_p = (response_matrix.sum(axis=1) + 0.5) / (n_items + 1)
        student_p = np.clip(student_p, 0.001, 0.999)
        ability = norm.ppf(student_p)
        return {
            'difficulty': difficulty, 'discrimination': np.array(discrimination), 
            'ability': ability, 'n_items': n_items, 'n_students': n_students
        }

@st.cache_data
def run_advanced_tri_analysis(df):
    student_names = df[df.columns[0]]
    df_responses = df.set_index(df.columns[0]).copy()
    df_responses = df_responses.apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    response_matrix = df_responses.to_numpy()
    simulator = TRI_Simulator()
    model_params = simulator.fit_model(response_matrix)
    
    student_results = pd.DataFrame({
        'Aluno': student_names,
        'Proficiencia (θ)': model_params['ability'],
        'Pontuacao Total': response_matrix.sum(axis=1),
        'Percentual de Acerto': (response_matrix.sum(axis=1) / model_params['n_items'] * 100).round(2),
        'Z-Score': (model_params['ability'] - model_params['ability'].mean()) / model_params['ability'].std()
    })
    
    item_results = pd.DataFrame({
        'Questao': df_responses.columns,
        'Dificuldade (b)': model_params['difficulty'],
        'Discriminacao (a)': model_params['discrimination'],
        '% Acerto': (response_matrix.mean(axis=0) * 100).round(2),
        'Indice de Discriminacao': [
            (response_matrix[model_params['ability'] > np.median(model_params['ability']), i].mean() -
             response_matrix[model_params['ability'] <= np.median(model_params['ability']), i].mean())
            for i in range(model_params['n_items'])
        ]
    })
    
    corr_bisserial = []
    for i in range(model_params['n_items']):
        try:
            corr = np.corrcoef(response_matrix[:, i], model_params['ability'])[0, 1]
            corr_bisserial.append(corr if not np.isnan(corr) else 0)
        except: 
            corr_bisserial.append(0)
    item_results['Correlacao Bisserial'] = corr_bisserial
    
    cci_data = []
    for i, item in enumerate(df_responses.columns):
        for theta in simulator.ability_range:
            prob = simulator.probability_2pl(theta, model_params['discrimination'][i], model_params['difficulty'][i])
            cci_data.append({
                'Questao': item, 'Theta': theta, 'Probabilidade': prob,
                'Dificuldade': model_params['difficulty'][i], 'Discriminacao': model_params['discrimination'][i]
            })
    cci_df = pd.DataFrame(cci_data)
    
    return student_results, item_results, cci_df, model_params, response_matrix, df_responses

def calculate_reliability(item_results):
    try:
        avg_correlation = item_results['Correlacao Bisserial'].mean()
        n_items = len(item_results)
        alpha = (n_items * avg_correlation) / (1 + (n_items - 1) * avg_correlation)
        return max(0, min(1, alpha))
    except:
        return 0.7

# --- Funções para Gráficos com Tema Escuro ---
def plot_theta_distribution_dark(student_results):
    fig = px.histogram(
        student_results, 
        x='Proficiencia (θ)', 
        nbins=20,
        title='📈 Distribuicao das Proficiencias',
        labels={'Proficiencia (θ)': 'Proficiencia (θ)', 'count': 'Numero de Alunos'},
        color_discrete_sequence=['#8B5CF6']
    )
    
    mean_theta = student_results['Proficiencia (θ)'].mean()
    fig.add_vline(x=mean_theta, line_dash="dash", line_color="#10B981", 
                  annotation_text=f"Media: {mean_theta:.2f}", 
                  annotation_position="top right")
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        font_color='#F1F5F9',
        height=400
    )
    
    fig.update_xaxes(gridcolor='rgba(139, 92, 246, 0.2)')
    fig.update_yaxes(gridcolor='rgba(139, 92, 246, 0.2)')
    
    return fig

def plot_item_analysis_dark(item_results):
    fig = px.scatter(
        item_results,
        x='Dificuldade (b)',
        y='Discriminacao (a)',
        size='% Acerto',
        color='Correlacao Bisserial',
        hover_name='Questao',
        title='🎯 Analise Multidimensional das Questoes',
        labels={
            'Dificuldade (b)': 'Dificuldade (b) →',
            'Discriminacao (a)': 'Discriminacao (a) ↑',
            '% Acerto': 'Taxa de Acerto (%)',
            'Correlacao Bisserial': 'Correlacao'
        },
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        font_color='#F1F5F9'
    )
    
    fig.update_xaxes(gridcolor='rgba(139, 92, 246, 0.2)')
    fig.update_yaxes(gridcolor='rgba(139, 92, 246, 0.2)')
    
    return fig

def plot_student_progress_dark(detailed_df, aluno_nome):
    aluno_data = detailed_df[detailed_df['Aluno'] == aluno_nome]
    
    fig = go.Figure()
    
    colors = ['#10B981' if x == 1 else '#EF4444' for x in aluno_data['Acerto']]
    
    # Adicionar dificuldade como uma segunda linha
    fig.add_trace(go.Bar(
        x=aluno_data['Questao'],
        y=aluno_data['Dificuldade_Questao'],
        name='Dificuldade da Questao',
        marker_color='#8B5CF6',
        opacity=0.7,
        yaxis='y2'
    ))
    
    # Adicionar barras para acertos/erros
    fig.add_trace(go.Bar(
        x=aluno_data['Questao'],
        y=[1] * len(aluno_data),
        marker_color=colors,
        name='Desempenho',
        hovertemplate="<b>Questao %{x}</b><br>" +
                     "Status: %{customdata}<extra></extra>",
        customdata=['✓ Acertou' if a == 1 else '✗ Errou' for a in aluno_data['Acerto']]
    ))
    
    fig.update_layout(
        title=f'📊 Desempenho Individual: {aluno_nome}',
        xaxis_title='Questoes',
        yaxis_title='',
        yaxis2=dict(
            title='Dificuldade',
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        height=400,
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        font_color='#F1F5F9',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def plot_turma_panorama_dark(student_results, item_results):
    """Grafico de panorama geral da turma"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('📊 Distribuicao da Proficiencia', '📈 Dificuldade por Questao',
                       '🎯 Taxa de Acerto da Turma', '🏆 Top 5 Melhores Desempenhos'),
        vertical_spacing=0.15,
        horizontal_spacing=0.15
    )
    
    # Grafico 1: Distribuicao da proficiencia
    fig.add_trace(
        go.Histogram(
            x=student_results['Proficiencia (θ)'],
            marker_color='#8B5CF6',
            name='Proficiencia',
            nbinsx=15
        ),
        row=1, col=1
    )
    
    mean_theta = student_results['Proficiencia (θ)'].mean()
    fig.add_vline(x=mean_theta, line_dash="dash", line_color="#10B981", 
                  annotation_text=f"Media: {mean_theta:.2f}", 
                  annotation_position="top right",
                  row=1, col=1)
    
    # Grafico 2: Dificuldade por questao
    fig.add_trace(
        go.Bar(
            x=item_results['Questao'],
            y=item_results['Dificuldade (b)'],
            marker_color='#8B5CF6',
            name='Dificuldade',
            hovertemplate='Questao: %{x}<br>Dificuldade: %{y:.2f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Linha de media da dificuldade
    mean_diff = item_results['Dificuldade (b)'].mean()
    fig.add_hline(y=mean_diff, line_dash="dash", line_color="#F59E0B",
                 annotation_text=f"Media: {mean_diff:.2f}",
                 annotation_position="top right",
                 row=1, col=2)
    
    # Grafico 3: Taxa de acerto da turma
    fig.add_trace(
        go.Scatter(
            x=item_results['Questao'],
            y=item_results['% Acerto'],
            mode='lines+markers',
            line=dict(color='#10B981', width=3),
            marker=dict(size=8, color='#10B981'),
            name='% Acerto',
            hovertemplate='Questao: %{x}<br>Acerto: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Linha de 50% para referencia
    fig.add_hline(y=50, line_dash="dot", line_color="#94A3B8",
                 annotation_text="Meta 50%",
                 annotation_position="bottom right",
                 row=2, col=1)
    
    # Grafico 4: Top 5 melhores desempenhos
    top_5 = student_results.nlargest(5, 'Proficiencia (θ)')
    fig.add_trace(
        go.Bar(
            x=top_5['Aluno'],
            y=top_5['Proficiencia (θ)'],
            marker_color='#8B5CF6',
            name='Top 5',
            hovertemplate='%{x}<br>Proficiencia: %{y:.2f}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=700,
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        font_color='#F1F5F9',
        showlegend=False
    )
    
    # Atualizar eixos
    fig.update_xaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=1, col=1)
    fig.update_yaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=1, col=1)
    fig.update_xaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=1, col=2)
    fig.update_yaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=1, col=2)
    fig.update_xaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=2, col=1)
    fig.update_yaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=2, col=1)
    fig.update_xaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=2, col=2)
    fig.update_yaxes(gridcolor='rgba(139, 92, 246, 0.1)', row=2, col=2)
    
    # Rotacionar labels do eixo X nos graficos de barras
    fig.update_xaxes(tickangle=45, row=1, col=2)
    fig.update_xaxes(tickangle=45, row=2, col=2)
    
    return fig

def get_top_tutors(student_results, n=10):
    """Identifica os melhores alunos para serem tutores"""
    # Alunos com proficiencia alta (θ > 1.0) e bom percentual de acerto (> 70%)
    potential_tutors = student_results[
        (student_results['Proficiencia (θ)'] > 1.0) & 
        (student_results['Percentual de Acerto'] > 70)
    ].copy()
    
    if len(potential_tutors) == 0:
        # Se nao houver alunos com θ > 1.0, pegar os top n por proficiencia
        potential_tutors = student_results.nlargest(n, 'Proficiencia (θ)').copy()
    
    # Verificar se há dados suficientes para calcular o score
    if len(potential_tutors) > 0:
        # Adicionar classificacao de qualidade do tutor
        # Prevenir divisão por zero se todos os valores forem iguais
        theta_min = potential_tutors['Proficiencia (θ)'].min()
        theta_max = potential_tutors['Proficiencia (θ)'].max()
        acerto_min = potential_tutors['Percentual de Acerto'].min()
        acerto_max = potential_tutors['Percentual de Acerto'].max()
        
        theta_range = theta_max - theta_min
        acerto_range = acerto_max - acerto_min
        
        if theta_range > 0 and acerto_range > 0:
            potential_tutors['Score_Tutor'] = (
                (potential_tutors['Proficiencia (θ)'] - theta_min) / theta_range * 0.6 +
                (potential_tutors['Percentual de Acerto'] - acerto_min) / acerto_range * 0.4
            )
        else:
            # Se todos os valores forem iguais, usar score base 0.5
            potential_tutors['Score_Tutor'] = 0.5
        
        # Ordenar por score
        potential_tutors = potential_tutors.sort_values('Score_Tutor', ascending=False)
    else:
        # Se não houver potenciais tutores, criar DataFrame vazio com colunas
        potential_tutors = pd.DataFrame(columns=student_results.columns.tolist() + ['Score_Tutor'])
    
    # Adicionar posicao
    if len(potential_tutors) > 0:
        potential_tutors['Posicao'] = range(1, len(potential_tutors) + 1)
    
    return potential_tutors.head(n)

# --- Funcao para criar relatorio em texto simples (TXT) ---
def create_text_report(student_results, item_results, detailed_df, aluno_selecionado=None):
    """Cria um relatorio em formato de texto simples (.TXT)"""
    
    report = []
    report.append("=" * 70)
    report.append("RELATORIO DE ANALISE - KAIROS")
    report.append("=" * 70)
    report.append(f"Data de geracao: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append(f"Total de alunos: {len(student_results)}")
    report.append(f"Total de questoes: {len(item_results)}")
    report.append("")
    
    # Explicacao dos parametros TRI
    report.append("EXPLICACAO DOS PARAMETROS TRI")
    report.append("-" * 40)
    report.append("1. DIFICULDADE (b):")
    report.append("   - Valores negativos: Questao facil")
    report.append("   - Valores proximos a 0: Dificuldade media")
    report.append("   - Valores positivos: Questao dificil")
    report.append("   - Faixa tipica: -3 a +3")
    report.append("")
    report.append("2. DISCRIMINACAO (a):")
    report.append("   - Valores abaixo de 0.3: Discriminacao baixa (questao problematica)")
    report.append("   - Valores 0.3-0.6: Discriminacao moderada")
    report.append("   - Valores acima de 0.6: Discriminacao alta (questao excelente)")
    report.append("   - Valores negativos: Questao funciona inversamente (erro grave)")
    report.append("")
    report.append("3. PROFICIENCIA (θ):")
    report.append("   - Valores abaixo de -1: Proficiencia baixa")
    report.append("   - Valores entre -1 e +1: Proficiencia media")
    report.append("   - Valores acima de +1: Proficiencia alta")
    report.append("   - Escala tipica: -4 a +4 (media 0, desvio padrao 1)")
    report.append("")
    
    report.append("PANORAMA GERAL DA TURMA")
    report.append("-" * 40)
    report.append(f"Proficiencia media (θ): {student_results['Proficiencia (θ)'].mean():.3f}")
    report.append(f"Desvio padrao da proficiencia: {student_results['Proficiencia (θ)'].std():.3f}")
    report.append(f"Taxa media de acerto: {student_results['Percentual de Acerto'].mean():.1f}%")
    report.append(f"Dificuldade media das questoes (b): {item_results['Dificuldade (b)'].mean():.3f}")
    report.append(f"Confiabilidade do teste: {calculate_reliability(item_results):.3f}")
    report.append("")
    
    # Top 10 tutores
    top_tutors = get_top_tutors(student_results, 10)
    if len(top_tutors) > 0:
        report.append("TOP 10 TUTORES DE COLEGAS")
        report.append("-" * 40)
        report.append("Pos | Aluno | Proficiencia (θ) | % Acerto | Score Tutor")
        report.append("-" * 70)
        for idx, row in top_tutors.iterrows():
            report.append(f"{row['Posicao']:3d} | {row['Aluno'][:20]:20s} | {row['Proficiencia (θ)']:7.2f} | {row['Percentual de Acerto']:7.1f}% | {row['Score_Tutor']:6.2f}")
        report.append("")
        report.append("SUGESTOES PARA GRUPOS DE TUTORIA:")
        report.append("1. Formar grupos de 3-4 alunos com 1 tutor")
        report.append("2. Atribuir tutores para temas especificos de dificuldade")
        report.append("3. Realizar sessoes semanais de reforco")
        report.append("")
    
    if aluno_selecionado:
        aluno_data = student_results[student_results['Aluno'] == aluno_selecionado].iloc[0]
        rank = list(student_results.sort_values('Proficiencia (θ)', ascending=False)['Aluno']).index(aluno_selecionado) + 1
        
        report.append(f"ANALISE INDIVIDUAL - {aluno_selecionado}")
        report.append("-" * 40)
        report.append(f"Proficiencia (θ): {aluno_data['Proficiencia (θ)']:.3f}")
        report.append(f"Pontuacao: {int(aluno_data['Pontuacao Total'])}/{len(item_results)}")
        report.append(f"Percentual de acerto: {aluno_data['Percentual de Acerto']:.1f}%")
        report.append(f"Posicao no ranking: {rank}º de {len(student_results)}")
        report.append("")
        
        # Verificar se e tutor potencial
        if aluno_selecionado in top_tutors['Aluno'].values:
            tutor_info = top_tutors[top_tutors['Aluno'] == aluno_selecionado].iloc[0]
            report.append("🎓 **ESTE ALUNO PODE SER TUTOR DE COLEGAS**")
            report.append(f"   - Score como tutor: {tutor_info['Score_Tutor']:.2f}")
            report.append(f"   - Posicao entre tutores: {tutor_info['Posicao']}º")
            report.append("   - Sugestao: Atribuir para auxiliar 2-3 colegas com dificuldades")
            report.append("")
        
        # Interpretacao da proficiencia do aluno
        theta = aluno_data['Proficiencia (θ)']
        if theta < -1.5:
            report.append("INTERPRETACAO: Proficiencia MUITO BAIXA")
            report.append("   * Necessita de intervencao pedagogica imediata")
            report.append("   * Dificuldades significativas na aprendizagem")
            report.append("   * Sugestao: Acompanhamento individual com tutor")
        elif theta < -0.5:
            report.append("INTERPRETACAO: Proficiencia BAIXA")
            report.append("   * Necessita de reforco escolar")
            report.append("   * Recomenda-se atendimento individualizado")
            report.append("   * Sugestao: Participar de grupos de estudo com tutores")
        elif theta < 0.5:
            report.append("INTERPRETACAO: Proficiencia MEDIA")
            report.append("   * Desempenho adequado para o nivel escolar")
            report.append("   * Manter ritmo de estudos atual")
            report.append("   * Sugestao: Praticar questoes de maior dificuldade")
        elif theta < 1.5:
            report.append("INTERPRETACAO: Proficiencia ALTA")
            report.append("   * Bom desempenho academico")
            report.append("   * Pode atuar como tutor de colegas")
            report.append("   * Sugestao: Desafios adicionais e aprofundamento")
        else:
            report.append("INTERPRETACAO: Proficiencia MUITO ALTA")
            report.append("   * Excelente desempenho")
            report.append("   * Recomenda-se atividades desafiadoras")
            report.append("   * Sugestao: Atuar como tutor principal em grupos de estudo")
        report.append("")
    
    report.append("ANALISE DAS QUESTOES")
    report.append("-" * 40)
    
    # Questoes problematicas
    problematic_items = item_results[
        (item_results['Discriminacao (a)'] < 0.3) | 
        (item_results['Correlacao Bisserial'] < 0.1) |
        (item_results['% Acerto'] < 20) |
        (item_results['% Acerto'] > 90)
    ]
    
    if len(problematic_items) > 0:
        report.append(f"Questoes que requerem atencao ({len(problematic_items)}):")
        for _, item in problematic_items.iterrows():
            issues = []
            if item['Discriminacao (a)'] < 0.3:
                issues.append("baixa discriminacao")
            if item['Correlacao Bisserial'] < 0.1:
                issues.append("baixa correlacao")
            if item['% Acerto'] < 20:
                issues.append("muito dificil")
            if item['% Acerto'] > 90:
                issues.append("muito facil")
            
            report.append(f"   * {item['Questao']}: {', '.join(issues)} (Dificuldade: {item['Dificuldade (b)']:.2f}, Acerto: {item['% Acerto']:.1f}%)")
    else:
        report.append("Todas as questoes apresentam caracteristicas adequadas.")
    
    report.append("")
    report.append("RECOMENDACOES PEDAGOGICAS")
    report.append("-" * 40)
    recommendations = [
        "1. Revise questoes com discriminacao abaixo de 0.3",
        "2. Considere reformular questoes muito faceis (>90%) ou dificeis (<20%)",
        "3. Use questoes com alta discriminacao (>0.6) em futuras avaliacoes",
        "4. Organize grupos de tutoria com os 10 melhores alunos identificados",
        "5. Planeje atividades de reforco para alunos com θ < -0.5",
        "6. Proponha desafios adicionais para alunos com θ > 1.0",
        "7. Implemente monitoramento continuo com relatorios mensais",
        "8. Use os dados para personalizacao do ensino"
    ]
    
    for rec in recommendations:
        report.append(rec)
    
    report.append("")
    report.append("=" * 70)
    report.append("Fim do relatorio")
    report.append("=" * 70)
    
    return "\n".join(report)

# --- Funcao para criar relatorio CSV formatado ---
def create_csv_report(student_results, item_results, detailed_df, aluno_selecionado=None):
    """Cria um relatorio formatado em CSV com multiplas secoes"""
    
    # Criar buffer para o CSV
    buffer = io.StringIO()
    
    # Secao 1: Metadados
    buffer.write("=== METADADOS ===\n")
    buffer.write("Metrica,Valor\n")
    buffer.write(f"Data de geracao,{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    buffer.write(f"Total de alunos,{len(student_results)}\n")
    buffer.write(f"Total de questoes,{len(item_results)}\n")
    buffer.write(f"Proficiencia media,{student_results['Proficiencia (θ)'].mean():.3f}\n")
    buffer.write(f"Desvio padrao da proficiencia,{student_results['Proficiencia (θ)'].std():.3f}\n")
    buffer.write(f"Dificuldade media das questoes,{item_results['Dificuldade (b)'].mean():.3f}\n")
    buffer.write(f"Taxa media de acerto,{student_results['Percentual de Acerto'].mean():.1f}%\n")
    buffer.write(f"Confiabilidade,{calculate_reliability(item_results):.3f}\n")
    buffer.write("\n")
    
    # Secao 2: Explicacao dos parametros TRI
    buffer.write("=== EXPLICACAO DOS PARAMETROS TRI ===\n")
    buffer.write("Parametro,Descricao,Interpretacao\n")
    buffer.write('Dificuldade (b),"Mede o nivel de dificuldade da questao",')
    buffer.write('"Negativo: facil; Proximo a 0: media; Positivo: dificil"\n')
    buffer.write('Discriminacao (a),"Capacidade de diferenciar alunos",')
    buffer.write('"<0.3: baixa; 0.3-0.6: moderada; >0.6: alta; Negativo: problema grave"\n')
    buffer.write('Proficiencia (θ),"Habilidade do aluno na escala TRI",')
    buffer.write('"<-1.5: muito baixa; -1.5 a -0.5: baixa; -0.5 a 0.5: media; 0.5 a 1.5: alta; >1.5: muito alta"\n')
    buffer.write("\n")
    
    # Secao 3: Top 10 Tutores
    top_tutors = get_top_tutors(student_results, 10)
    if len(top_tutors) > 0:
        buffer.write("=== TOP 10 TUTORES DE COLEGAS ===\n")
        buffer.write("Posicao,Aluno,Proficiencia (θ),% Acerto,Score Tutor,Sugestao\n")
        for idx, row in top_tutors.iterrows():
            sugestao = f"Tutor para {min(3, len(student_results)//10)} alunos"
            buffer.write(f"{row['Posicao']},{row['Aluno']},{row['Proficiencia (θ)']:.3f},{row['Percentual de Acerto']:.1f}%,{row['Score_Tutor']:.3f},{sugestao}\n")
        buffer.write("\n")
    
    # Secao 4: Ranking de Alunos
    buffer.write("=== RANKING DE ALUNOS ===\n")
    ranking_df = student_results.sort_values('Proficiencia (θ)', ascending=False)
    ranking_df['Posicao'] = range(1, len(ranking_df) + 1)
    ranking_df[['Posicao', 'Aluno', 'Proficiencia (θ)', 'Percentual de Acerto', 'Pontuacao Total']].to_csv(buffer, index=False)
    buffer.write("\n")
    
    # Secao 5: Analise de Questoes
    buffer.write("=== ANALISE DE QUESTOES ===\n")
    item_results[['Questao', 'Dificuldade (b)', 'Discriminacao (a)', '% Acerto', 'Correlacao Bisserial']].to_csv(buffer, index=False)
    buffer.write("\n")
    
    # Secao 6: Questoes Problematicas
    problematic_items = item_results[
        (item_results['Discriminacao (a)'] < 0.3) | 
        (item_results['Correlacao Bisserial'] < 0.1) |
        (item_results['% Acerto'] < 20) |
        (item_results['% Acerto'] > 90)
    ]
    
    if len(problematic_items) > 0:
        buffer.write("=== QUESTOES PROBLEMATICAS ===\n")
        buffer.write("Questao,Problemas,Dificuldade,Discriminacao,% Acerto,Acão Recomendada\n")
        for _, item in problematic_items.iterrows():
            issues = []
            if item['Discriminacao (a)'] < 0.3:
                issues.append("Baixa discriminacao")
            if item['Correlacao Bisserial'] < 0.1:
                issues.append("Baixa correlacao")
            if item['% Acerto'] < 20:
                issues.append("Muito dificil")
            if item['% Acerto'] > 90:
                issues.append("Muito facil")
            
            acao = "Revisar questao" if len(issues) > 0 else "Manter"
            buffer.write(f"{item['Questao']},{';'.join(issues)},{item['Dificuldade (b)']:.3f},{item['Discriminacao (a)']:.3f},{item['% Acerto']:.1f}%,{acao}\n")
        buffer.write("\n")
    
    # Secao 7: Analise Individual (se aluno selecionado)
    if aluno_selecionado:
        aluno_data = student_results[student_results['Aluno'] == aluno_selecionado].iloc[0]
        rank = list(student_results.sort_values('Proficiencia (θ)', ascending=False)['Aluno']).index(aluno_selecionado) + 1
        
        buffer.write(f"=== ANALISE INDIVIDUAL: {aluno_selecionado} ===\n")
        buffer.write("Metrica,Valor\n")
        buffer.write(f"Proficiencia (θ),{aluno_data['Proficiencia (θ)']:.3f}\n")
        buffer.write(f"Pontuacao,{int(aluno_data['Pontuacao Total'])}/{len(item_results)}\n")
        buffer.write(f"Percentual de acerto,{aluno_data['Percentual de Acerto']:.1f}%\n")
        buffer.write(f"Posicao no ranking,{rank}º de {len(student_results)}\n")
        
        # Verificar se e tutor
        if aluno_selecionado in top_tutors['Aluno'].values:
            tutor_info = top_tutors[top_tutors['Aluno'] == aluno_selecionado].iloc[0]
            buffer.write(f"E tutor potencial?,Sim\n")
            buffer.write(f"Score como tutor,{tutor_info['Score_Tutor']:.3f}\n")
            buffer.write(f"Posicao entre tutores,{tutor_info['Posicao']}º\n")
        else:
            buffer.write(f"E tutor potencial?,Nao\n")
        
        buffer.write("\n")
        
        # Interpretacao da proficiencia
        theta = aluno_data['Proficiencia (θ)']
        buffer.write("=== INTERPRETACAO DA PROFICIENCIA ===\n")
        if theta < -1.5:
            buffer.write("Classificacao,MUITO BAIXA\n")
            buffer.write("Recomendacao,Intervencao pedagogica imediata\n")
            buffer.write("Sugestao,Acompanhamento individual com tutor\n")
        elif theta < -0.5:
            buffer.write("Classificacao,BAIXA\n")
            buffer.write("Recomendacao,Reforco escolar\n")
            buffer.write("Sugestao,Participar de grupos de estudo\n")
        elif theta < 0.5:
            buffer.write("Classificacao,MEDIA\n")
            buffer.write("Recomendacao,Manter ritmo atual\n")
            buffer.write("Sugestao,Praticar questoes dificeis\n")
        elif theta < 1.5:
            buffer.write("Classificacao,ALTA\n")
            buffer.write("Recomendacao,Atuar como tutor\n")
            buffer.write("Sugestao,Desafios adicionais\n")
        else:
            buffer.write("Classificacao,MUITO ALTA\n")
            buffer.write("Recomendacao,Tutor principal\n")
            buffer.write("Sugestao,Atividades avancadas\n")
        buffer.write("\n")
        
        # Detalhamento por questao do aluno
        aluno_detailed = detailed_df[detailed_df['Aluno'] == aluno_selecionado]
        buffer.write("=== DETALHAMENTO POR QUESTAO ===\n")
        aluno_detailed[['Questao', 'Resposta_Aluno', 'Resposta_Correta', 'Acerto', 'Dificuldade_Questao']].to_csv(buffer, index=False)
    
    return buffer.getvalue()

# --- Funcao para exportar Excel (com fallback se openpyxl nao disponivel) ---
def export_to_excel(df_binary, student_results, item_results, detailed_df):
    """Exporta dados para Excel com fallback para CSV se openpyxl nao estiver disponivel"""
    
    if OPENPYXL_AVAILABLE:
        try:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_binary.to_excel(writer, sheet_name='Respostas Binarias', index=False)
                student_results.to_excel(writer, sheet_name='Resultados Alunos', index=False)
                item_results.to_excel(writer, sheet_name='Analise Questoes', index=False)
                detailed_df.to_excel(writer, sheet_name='Detalhado', index=False)
                
                # Adicionar aba de tutores
                top_tutors = get_top_tutors(student_results, 10)
                if len(top_tutors) > 0:
                    top_tutors.to_excel(writer, sheet_name='Top Tutores', index=False)
            
            return excel_buffer.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        except Exception as e:
            st.error(f"Erro ao criar Excel: {str(e)}")
            # Fallback para CSV
            return None, None
    else:
        # Criar um arquivo ZIP com multiplos CSVs
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Adicionar cada dataframe como CSV separado
            zip_file.writestr('respostas_binarias.csv', df_binary.to_csv(index=False))
            zip_file.writestr('resultados_alunos.csv', student_results.to_csv(index=False))
            zip_file.writestr('analise_questoes.csv', item_results.to_csv(index=False))
            zip_file.writestr('detalhado.csv', detailed_df.to_csv(index=False))
            
            # Adicionar CSV de tutores
            top_tutors = get_top_tutors(student_results, 10)
            if len(top_tutors) > 0:
                zip_file.writestr('top_tutores.csv', top_tutors.to_csv(index=False))
        
        return zip_buffer.getvalue(), 'application/zip'

# --- Função para criar logo em base64 a partir da imagem ---
def create_logo_html():
    """Cria o HTML para o logo usando base64 da imagem"""
    try:
        # Se você tiver a imagem salva como Fig_4.png
        with open('Fig_4.png', 'rb') as img_file:
            img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode()
        
        return f'''
        <div class="sidebar-logo-container">
            <div class="sidebar-logo-wrapper">
                <img src="data:image/png;base64,{img_base64}" 
                     style="width: 100%; height: auto; max-width: 180px; display: block; margin: 0 auto;"
                     alt="KAIROS Logo">
            </div>
        </div>
        '''
    except:
        # Fallback: HTML/CSS elegantíssimo se a imagem não carregar
        return '''
        <div class="sidebar-logo-container">
            <div class="sidebar-logo-wrapper">
                <div style="font-family: 'Segoe UI', Arial, sans-serif; text-align: center; padding: 5px;">
                    <div style="font-size: 26px; font-weight: 900; color: #8B5CF6; letter-spacing: 1.5px; 
                                text-shadow: 0 2px 4px rgba(139, 92, 246, 0.3); margin-bottom: 5px;">
                        KAIROS
                    </div>
                    <div style="font-size: 11px; font-weight: 700; color: #A78BFA; letter-spacing: 0.8px; 
                                margin-bottom: 3px; text-transform: uppercase;">
                        Inteligência Educacional
                    </div>
                    <hr style="border: none; height: 1.5px; background: linear-gradient(90deg, transparent, #8B5CF6, transparent); 
                              margin: 5px auto 8px auto; width: 85%; opacity: 0.7;">
                    <div style="font-size: 9px; color: #94A3B8; line-height: 1.3; letter-spacing: 0.3px;">
                        Sistema de Gestão Pedagógica<br>
                        Avançada v2.0
                    </div>
                </div>
            </div>
        </div>
        '''

# --- Interface Principal ---
st.markdown('<h1 class="main-header"> KAIROS - Sistema de Análise de Avaliações</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #94A3B8; font-weight: 500;">Análise psicométrica avançada para educadores</p>', unsafe_allow_html=True)

# --- Sidebar com Configuracoes ---
with st.sidebar:
    # Logo KAIROS elegante
    st.markdown(create_logo_html(), unsafe_allow_html=True)
    
    st.markdown("### 🚀 **Como Usar**")
    st.markdown("""
    1. **📝 Configure o gabarito** abaixo
    2. **👥 Adicione os alunos** (manual ou CSV)
    3. **📊 Analise os resultados** automaticamente
    4. **📄 Exporte relatórios** em TXT e CSV
    5. **👨‍🏫 Identifique tutores** para grupos de estudo
    """)
    
    # Avisos sobre dependencias
    if not OPENPYXL_AVAILABLE:
        st.warning("""
        ⚠️ **Módulo openpyxl não instalado**
        
        Para exportar em Excel, instale:
        ```bash
        pip install openpyxl
        ```
        """)
    
    st.markdown("### 📝 **Configurar Gabarito**")
    
    # Input do gabarito
    gabarito_input = st.text_area(
        "**Digite as respostas corretas:**",
        placeholder="Ex: A, B, C, D, A, B, C, D, E, A",
        help="Separe por vírgula ou escreva sem espaços",
        height=100,
        key="gabarito_input"
    )
    
    if gabarito_input:
        gabarito_input_clean = gabarito_input.replace(' ', '').replace(',', '').upper()
        num_questoes = len(gabarito_input_clean)
        
        if num_questoes > 0:
            gabarito = {f'Q{i+1}': gabarito_input_clean[i] for i in range(num_questoes)}
            
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown(f"### ✅ **Gabarito Configurado**")
            st.markdown(f"**{num_questoes} questões** identificadas")
            
            # Mostrar preview
            cols = st.columns(min(6, num_questoes))
            for i in range(min(6, num_questoes)):
                with cols[i]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 8px; background: #8B5CF6; color: white; border-radius: 6px; font-weight: bold;">
                        Q{i+1}<br>
                        <span style="font-size: 1.2em;">{gabarito[f'Q{i+1}']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            if num_questoes > 6:
                st.markdown(f"*... e mais {num_questoes - 6} questões*")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ **Digite um gabarito válido**")
            gabarito = {}
            num_questoes = 0
    else:
        gabarito = {}
        num_questoes = 0
    
    st.markdown("---")
    
    # Modo de entrada
    st.markdown("### 👥 **Adicionar Alunos**")
    modo_entrada = st.radio(
        "**Escolha o método:**",
        ["✍️ **Inserção Manual**", "📁 **Upload de CSV**"],
        index=0,
        key="modo_entrada"
    )

# --- Área Principal ---
if gabarito and num_questoes > 0:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"### 📋 **Gabarito Configurado**")
    st.markdown(f"**{num_questoes} questões** | Pronto para receber dados dos alunos")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- INSERÇÃO MANUAL FUNCIONAL ---
    if modo_entrada == "✍️ **Inserção Manual**":
        st.markdown("### ✍️ **Inserir Dados dos Alunos**")
        
        # Controle do número de alunos
        col_num, col_btn = st.columns([2, 1])
        with col_num:
            num_alunos = st.number_input(
                "**Número de alunos:**",
                min_value=1,
                max_value=50,
                value=5,
                step=1,
                key="num_alunos"
            )
        
        with col_btn:
            if st.button("🔄 Atualizar Formulário", type="primary", use_container_width=True):
                st.rerun()
        
        # Formulário dinâmico
        if num_alunos > 0:
            st.markdown("### 📝 **Preencha as Respostas**")
            
            # Inicializar session state para armazenar respostas
            if 'alunos_respostas' not in st.session_state:
                st.session_state.alunos_respostas = {}
            
            # Criar formulário
            alunos_data = []
            
            for aluno_idx in range(num_alunos):
                st.markdown(f"---")
                st.markdown(f"#### 👨‍🎓 **Aluno {aluno_idx + 1}**")
                
                # Nome do aluno
                nome_key = f"nome_{aluno_idx}"
                nome = st.text_input(
                    "**Nome do aluno:**",
                    value=st.session_state.alunos_respostas.get(nome_key, f"Aluno {aluno_idx + 1}"),
                    key=nome_key
                )
                st.session_state.alunos_respostas[nome_key] = nome
                
                # Respostas por questão
                st.markdown("**Respostas:**")
                
                # Organizar questões em colunas
                num_cols = min(5, num_questoes)
                num_rows = (num_questoes + num_cols - 1) // num_cols
                
                respostas_aluno = []
                for row in range(num_rows):
                    cols = st.columns(num_cols)
                    for col in range(num_cols):
                        q_idx = row * num_cols + col
                        if q_idx < num_questoes:
                            questao_num = q_idx + 1
                            with cols[col]:
                                resposta_key = f"aluno_{aluno_idx}_q_{q_idx}"
                                resposta = st.selectbox(
                                    f"**Q{questao_num}**",
                                    options=["-", "A", "B", "C", "D", "E"],
                                    index=0,
                                    key=resposta_key
                                )
                                st.session_state.alunos_respostas[resposta_key] = resposta
                                respostas_aluno.append(resposta)
                
                alunos_data.append([nome] + respostas_aluno)
            
            # Botão para processar
            col_process, col_clear = st.columns(2)
            with col_process:
                if st.button("✅ **Processar Respostas**", type="primary", use_container_width=True):
                    # Verificar se todos os nomes foram preenchidos
                    nomes = [aluno[0] for aluno in alunos_data]
                    if len(set(nomes)) != len(nomes):
                        st.error("⚠️ **Erro:** Nomes de alunos duplicados!")
                    else:
                        # Criar DataFrame com os dados
                        colunas = ['Aluno'] + [f'Q{i+1}' for i in range(num_questoes)]
                        df_manual = pd.DataFrame(alunos_data, columns=colunas)
                        
                        # Converter para binário
                        df_binary = df_manual.copy()
                        for i in range(num_questoes):
                            questao = f'Q{i+1}'
                            df_binary[questao] = (df_manual[questao] == gabarito[questao]).astype(int)
                        
                        st.session_state['df_manual'] = df_manual
                        st.session_state['df_binary'] = df_binary
                        st.success(f"✅ **{num_alunos} alunos** processados com sucesso!")
            
            with col_clear:
                if st.button("🗑️ **Limpar Dados**", type="secondary", use_container_width=True):
                    for key in list(st.session_state.alunos_respostas.keys()):
                        del st.session_state.alunos_respostas[key]
                    if 'df_manual' in st.session_state:
                        del st.session_state['df_manual']
                    if 'df_binary' in st.session_state:
                        del st.session_state['df_binary']
                    st.rerun()
    
    # --- UPLOAD DE CSV ---
    elif modo_entrada == "📁 **Upload de CSV**":
        st.markdown("### 📁 **Upload de Arquivo CSV**")
        
        uploaded_file = st.file_uploader(
            "**Selecione o arquivo CSV com as respostas:**",
            type=['csv'],
            help="**Formato esperado:** Primeira coluna = Nomes dos alunos, demais colunas = Respostas (A, B, C, D, E)",
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file)
                
                # Verificar compatibilidade
                if df_upload.shape[1] - 1 != num_questoes:
                    st.error(f"⚠️ **Incompatibilidade:** O arquivo tem {df_upload.shape[1]-1} questões, mas o gabarito tem {num_questoes}.")
                else:
                    # Renomear primeira coluna se necessário
                    if df_upload.columns[0] != 'Aluno':
                        df_upload = df_upload.rename(columns={df_upload.columns[0]: 'Aluno'})
                    
                    # Converter para binário
                    df_binary = df_upload.copy()
                    for i in range(num_questoes):
                        questao = f'Q{i+1}'
                        if questao in df_upload.columns:
                            df_binary[questao] = (df_upload[questao].astype(str).str.upper() == gabarito[questao]).astype(int)
                    
                    st.session_state['df_manual'] = df_upload
                    st.session_state['df_binary'] = df_binary
                    
                    st.success(f"✅ **{len(df_upload)} alunos** carregados com sucesso!")
                    
                    with st.expander("📋 **Visualizar Dados Carregados**", expanded=False):
                        st.dataframe(df_upload.head(), use_container_width=True)
                        
            except Exception as e:
                st.error(f"❌ **Erro ao processar arquivo:** {str(e)}")

    # --- PROCESSAMENTO E ANÁLISE ---
    if 'df_binary' in st.session_state:
        df_binary = st.session_state['df_binary']
        df_original = st.session_state.get('df_manual', df_binary)
        
        # Executar análise TRI
        with st.spinner('🔍 **Analisando dados...**'):
            student_results, item_results, cci_df, model_params, response_matrix, df_responses = run_advanced_tri_analysis(df_binary)
            
            # Criar análise detalhada
            detailed_data = []
            for aluno_idx, aluno in enumerate(student_results['Aluno']):
                for q_idx in range(num_questoes):
                    questao = f'Q{q_idx + 1}'
                    detailed_data.append({
                        'Aluno': aluno,
                        'Questao': questao,
                        'Resposta_Aluno': df_original.iloc[aluno_idx, q_idx + 1] if df_original.shape[1] > q_idx + 1 else 'N/A',
                        'Resposta_Correta': gabarito[questao],
                        'Acerto': response_matrix[aluno_idx, q_idx],
                        'Proficiencia_Aluno': student_results.loc[aluno_idx, 'Proficiencia (θ)'],
                        'Dificuldade_Questao': item_results.loc[q_idx, 'Dificuldade (b)'],
                        'Discriminacao_Questao': item_results.loc[q_idx, 'Discriminacao (a)']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(f"### 🎉 **Análise Concluída!**")
        st.markdown(f"**{len(student_results)} alunos** | **{num_questoes} questões**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- ABAS PRINCIPAIS ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 **Dashboard**", 
            "👨‍🎓 **Análise Individual**", 
            "👨‍🏫 **Tutores de Colegas**",
            "📝 **Exportar Dados**"
        ])
        
        with tab1:
            st.markdown('<h2 class="sub-header">📊 Dashboard de Análise</h2>', unsafe_allow_html=True)
            
            # Métricas Principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("👥 **Alunos**", len(student_results))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                mean_theta = student_results['Proficiencia (θ)'].mean()
                st.metric("📈 **Proficiência Média**", f"{mean_theta:.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                mean_score = student_results['Percentual de Acerto'].mean()
                st.metric("🎯 **Taxa de Acerto**", f"{mean_score:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                reliability = calculate_reliability(item_results)
                st.metric("🛡️ **Confiabilidade**", f"{reliability:.3f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Panorama Geral da Turma
            st.markdown("### 🌟 **Panorama Geral da Turma**")
            st.plotly_chart(plot_turma_panorama_dark(student_results, item_results), use_container_width=True)
            
            # Gráficos adicionais
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                st.plotly_chart(plot_theta_distribution_dark(student_results), use_container_width=True)
            
            with col_graph2:
                st.plotly_chart(plot_item_analysis_dark(item_results), use_container_width=True)
            
            # Ranking de Alunos
            st.markdown("### 🏆 **Ranking de Alunos**")
            
            col_rank1, col_rank2 = st.columns([3, 2])
            
            with col_rank1:
                # Top 10 alunos
                top_students = student_results.sort_values('Proficiencia (θ)', ascending=False).head(10)
                top_students['Posicao'] = range(1, len(top_students) + 1)
                top_students = top_students[['Posicao', 'Aluno', 'Proficiencia (θ)', 'Percentual de Acerto']]
                
                # Exibir DataFrame
                st.dataframe(top_students, use_container_width=True)
            
            with col_rank2:
                st.markdown("### ⚠️ **Questões Problemáticas**")
                
                problematic_items = item_results[
                    (item_results['Discriminacao (a)'] < 0.3) | 
                    (item_results['% Acerto'] < 20) | 
                    (item_results['% Acerto'] > 90)
                ]
                
                if len(problematic_items) > 0:
                    for _, item in problematic_items.head(3).iterrows():
                        issues = []
                        if item['Discriminacao (a)'] < 0.3:
                            issues.append("📉 Baixa discriminação")
                        if item['% Acerto'] < 20:
                            issues.append("🔴 Muito difícil")
                        if item['% Acerto'] > 90:
                            issues.append("🟢 Muito fácil")
                        
                        st.warning(f"**{item['Questao']}**: {', '.join(issues)}")
                else:
                    st.success("✅ **Todas as questões estão dentro dos parâmetros adequados!**")
        
        with tab2:
            st.markdown('<h2 class="sub-header">👨‍🎓 Análise Individual</h2>', unsafe_allow_html=True)
            
            # Seletor de aluno
            aluno_selecionado = st.selectbox(
                "**Selecione um aluno para análise detalhada:**",
                student_results['Aluno'].tolist(),
                help="Clique no nome do aluno para ver seu desempenho completo",
                key="aluno_selecionado_tab2"
            )
            
            if aluno_selecionado:
                aluno_data = student_results[student_results['Aluno'] == aluno_selecionado].iloc[0]
                
                # Cartões de métricas
                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                
                with col_a1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    theta = aluno_data['Proficiencia (θ)']
                    status = "⏫ Acima" if theta > 0 else "⏬ Abaixo"
                    st.metric("🎓 **Proficiência (θ)**", f"{theta:.2f}", delta=status)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_a2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    score = int(aluno_data['Pontuacao Total'])
                    total = num_questoes
                    st.metric("📝 **Pontuação**", f"{score}/{total}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_a3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    percent = aluno_data['Percentual de Acerto']
                    st.metric("✅ **% Acerto**", f"{percent:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_a4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    rank = list(student_results.sort_values('Proficiencia (θ)', ascending=False)['Aluno']).index(aluno_selecionado) + 1
                    total = len(student_results)
                    st.metric("🏅 **Posição**", f"{rank}º/{total}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Gráfico de desempenho
                st.plotly_chart(plot_student_progress_dark(detailed_df, aluno_selecionado), use_container_width=True)
                
                # Verificar se é tutor potencial
                top_tutors = get_top_tutors(student_results, 10)
                if len(top_tutors) > 0 and aluno_selecionado in top_tutors['Aluno'].values:
                    tutor_info = top_tutors[top_tutors['Aluno'] == aluno_selecionado].iloc[0]
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown(f"### 👨‍🏫 **Potencial Tutor de Colegas**")
                    st.markdown(f"**Score como tutor:** {tutor_info['Score_Tutor']:.2f}")
                    st.markdown(f"**Posição entre tutores:** {tutor_info['Posicao']}º")
                    st.markdown("**Sugestão:** Este aluno pode auxiliar 2-3 colegas com dificuldades")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Dicas pedagógicas
                st.markdown("### 👨‍🏫 **Recomendações Pedagógicas**")
                
                if aluno_data['Proficiencia (θ)'] < -1:
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown("""
                    ### 🔴 **Atenção Especial Necessária**
                    - **Proficiência significativamente abaixo** da média
                    - **Recomenda-se:** Atividades de reforço intensivo
                    - **Sugestão:** Tutoria individualizada com aluno-tutor
                    - **Acompanhamento:** Monitoramento constante
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                elif aluno_data['Proficiencia (θ)'] < 0:
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown("""
                    ### 🟡 **Acompanhamento Recomendado**
                    - **Proficiência abaixo** da média
                    - **Recomenda-se:** Reforço nos tópicos com dificuldade
                    - **Sugestão:** Grupo de estudos com tutores
                    - **Acompanhamento:** Avaliação periódica
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                elif aluno_data['Proficiencia (θ)'] > 1:
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("""
                    ### 🟢 **Excelente Desempenho**
                    - **Proficiência significativamente acima** da média
                    - **Recomenda-se:** Desafios adicionais
                    - **Sugestão:** Atuação como tutor de colegas
                    - **Potencial:** Desenvolvimento avançado
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("""
                    ### 🔵 **Desempenho Adequado**
                    - **Proficiência dentro** da média esperada
                    - **Manter:** Ritmo atual de estudos
                    - **Sugestão:** Aprimoramento contínuo
                    - **Acompanhamento:** Regular
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<h2 class="sub-header">👨‍🏫 Tutores de Colegas</h2>', unsafe_allow_html=True)
            
            # Identificar os melhores tutores
            top_tutors = get_top_tutors(student_results, 10)
            
            if len(top_tutors) > 0:
                st.markdown("### 🏆 **Top 10 Alunos com Potencial para Tutoria**")
                st.markdown("""
                **Critérios para seleção de tutores:**
                - Proficiência (θ) > 1.0
                - Taxa de acerto > 70%
                - Score combinado de desempenho
                """)
                
                # Mostrar tabela de tutores
                display_tutors = top_tutors[['Posicao', 'Aluno', 'Proficiencia (θ)', 'Percentual de Acerto', 'Score_Tutor']].copy()
                display_tutors['Proficiencia (θ)'] = display_tutors['Proficiencia (θ)'].round(2)
                display_tutors['Percentual de Acerto'] = display_tutors['Percentual de Acerto'].round(1)
                display_tutors['Score_Tutor'] = display_tutors['Score_Tutor'].round(3)
                
                st.dataframe(display_tutors, use_container_width=True)
                
                # Sugestões para formação de grupos
                st.markdown("### 👥 **Sugestões para Formação de Grupos**")
                
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.markdown("#### **Grupos Heterogêneos**")
                    st.markdown("""
                    **Estratégia:** 1 tutor + 2-3 alunos com dificuldades
                    
                    **Vantagens:**
                    - Aprendizagem colaborativa
                    - Desenvolvimento de liderança
                    - Redução da carga do professor
                    - Personalização do ensino
                    """)
                
                with col_g2:
                    st.markdown("#### **Plano de Ação**")
                    st.markdown("""
                    **1. Organização:**
                    - Formar grupos semanais
                    - Definir horários fixos
                    
                    **2. Monitoramento:**
                    - Avaliações quinzenais
                    - Feedback dos tutores
                    - Ajuste de grupos
                    
                    **3. Reconhecimento:**
                    - Certificados de mérito
                    - Menções honrosas
                    - Incentivos pedagógicos
                    """)
                
                # Botão para exportar lista de tutores
                st.markdown("### 📋 **Exportar Lista de Tutores**")
                tutors_csv = top_tutors[['Posicao', 'Aluno', 'Proficiencia (θ)', 'Percentual de Acerto', 'Score_Tutor']].to_csv(index=False)
                
                st.download_button(
                    label="⬇️ **Baixar Lista de Tutores (CSV)**",
                    data=tutors_csv,
                    file_name=f"tutores_colega_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    type="primary"
                )
                
                # Visualização gráfica alternativa (sem usar Score_Tutor no size)
                st.markdown("### 📈 **Distribuição dos Potenciais Tutores**")
                
                # Criar gráfico de barras em vez de scatter com size
                fig_tutors = px.bar(
                    top_tutors,
                    x='Aluno',
                    y='Proficiencia (θ)',
                    color='Percentual de Acerto',
                    title='📊 Perfil dos Tutores Identificados',
                    color_continuous_scale='Viridis',
                    hover_data=['Percentual de Acerto', 'Score_Tutor', 'Posicao']
                )
                
                fig_tutors.update_layout(
                    height=500,
                    plot_bgcolor='rgba(30, 41, 59, 0.5)',
                    paper_bgcolor='rgba(15, 23, 42, 0)',
                    font_color='#F1F5F9',
                    xaxis_tickangle=45
                )
                
                st.plotly_chart(fig_tutors, use_container_width=True)
                
            else:
                st.warning("""
                ### ⚠️ **Nenhum aluno atende aos critérios para tutoria no momento**
                
                **Sugestões:**
                1. Considere reduzir os critérios (ex: θ > 0.5)
                2. Realize atividades de nivelamento
                3. Considere os top 5 alunos por proficiência como tutores provisórios
                """)
                
                # Mostrar top 5 alunos mesmo que não atendam aos critérios
                top_5 = student_results.nlargest(5, 'Proficiencia (θ)')
                st.markdown("#### **Top 5 Alunos por Proficiência**")
                st.dataframe(top_5[['Aluno', 'Proficiencia (θ)', 'Percentual de Acerto']], use_container_width=True)
        
        with tab4:
            st.markdown('<h2 class="sub-header">📝 Exportar Dados e Relatórios</h2>', unsafe_allow_html=True)
            
            col_r1, col_r2 = st.columns([2, 1])
            
            with col_r1:
                st.markdown("### 📄 **Gerar Relatórios**")
                
                report_type = st.radio(
                    "**Tipo de relatório:**",
                    ["📋 **Relatório Geral da Turma**", "👤 **Relatório Individual**"],
                    key="report_type"
                )
                
                if report_type == "👤 **Relatório Individual**":
                    aluno_relatorio = st.selectbox(
                        "**Selecione o aluno:**",
                        student_results['Aluno'].tolist(),
                        key="aluno_relatorio"
                    )
                
                # Container para os botões de exportação
                st.markdown("### 📤 **Exportar em Diferentes Formatos**")
                
                # Botão para gerar relatório em texto (TXT)
                if st.button("📝 **Gerar Relatório (TXT)**", type="primary", use_container_width=True):
                    with st.spinner("📊 Gerando relatório TXT..."):
                        try:
                            if report_type == "📋 **Relatório Geral da Turma**":
                                text_report = create_text_report(student_results, item_results, detailed_df)
                                filename = f"Relatorio_Turma_TRI_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                            else:
                                text_report = create_text_report(student_results, item_results, detailed_df, aluno_relatorio)
                                filename = f"Relatorio_{aluno_relatorio}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                            
                            # Botão de download TXT
                            st.download_button(
                                label="⬇️ **Baixar Relatório TXT**",
                                data=text_report,
                                file_name=filename,
                                mime="text/plain",
                                type="primary"
                            )
                            
                            st.success("✅ **Relatório TXT gerado com sucesso!**")
                        except Exception as e:
                            st.error(f"❌ **Erro ao gerar relatório TXT:** {str(e)}")
                
                # Botão para gerar relatório em CSV formatado
                if st.button("📊 **Gerar Relatório (CSV)**", type="secondary", use_container_width=True):
                    with st.spinner("📊 Gerando relatório CSV..."):
                        try:
                            if report_type == "📋 **Relatório Geral da Turma**":
                                csv_report = create_csv_report(student_results, item_results, detailed_df)
                                filename = f"Relatorio_Turma_TRI_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                            else:
                                csv_report = create_csv_report(student_results, item_results, detailed_df, aluno_relatorio)
                                filename = f"Relatorio_{aluno_relatorio}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                            
                            # Botão de download CSV
                            st.download_button(
                                label="⬇️ **Baixar Relatório CSV**",
                                data=csv_report,
                                file_name=filename,
                                mime="text/csv",
                                type="secondary"
                            )
                            
                            st.success("✅ **Relatório CSV gerado com sucesso!**")
                        except Exception as e:
                            st.error(f"❌ **Erro ao gerar relatório CSV:** {str(e)}")
                
                # Exportar dados completos
                st.markdown("### 💾 **Exportar Dados Completos**")
                
                # Botão para exportar CSV básico
                csv_data = df_binary.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ **Exportar CSV Simples**",
                    data=csv_data,
                    file_name=f"dados_alunos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    type="secondary",
                    use_container_width=True
                )
                
                # Botão para exportar Excel completo ou ZIP
                if st.button("📗 **Exportar Dados Completos**", use_container_width=True):
                    with st.spinner("Preparando dados para exportação..."):
                        try:
                            excel_data, mime_type = export_to_excel(df_binary, student_results, item_results, detailed_df)
                            
                            if excel_data:
                                filename = f"dados_completos_tri_{datetime.now().strftime('%Y%m%d')}"
                                
                                if mime_type == 'application/zip':
                                    filename += ".zip"
                                    label = "📦 **Baixar ZIP (múltiplos CSVs)**"
                                else:
                                    filename += ".xlsx"
                                    label = "📗 **Baixar Excel Completo**"
                                
                                st.download_button(
                                    label=label,
                                    data=excel_data,
                                    file_name=filename,
                                    mime=mime_type,
                                    use_container_width=True
                                )
                                st.success("✅ **Dados exportados com sucesso!**")
                            else:
                                st.error("❌ **Não foi possível criar o arquivo de exportação.**")
                        except Exception as e:
                            st.error(f"❌ **Erro ao exportar dados:** {str(e)}")
                
                # Exportar JSON
                top_tutors = get_top_tutors(student_results, 10)
                json_data = {
                    'metadata': {
                        'data_analise': datetime.now().isoformat(),
                        'total_alunos': len(student_results),
                        'total_questoes': num_questoes,
                        'proficiencia_media': float(student_results['Proficiencia (θ)'].mean()),
                        'desvio_padrao_proficiencia': float(student_results['Proficiencia (θ)'].std()),
                        'taxa_acerto_media': float(student_results['Percentual de Acerto'].mean()),
                        'confiabilidade': float(calculate_reliability(item_results))
                    },
                    'gabarito': gabarito,
                    'resumo_alunos': student_results.to_dict('records'),
                    'resumo_questoes': item_results.to_dict('records')
                }
                
                if len(top_tutors) > 0:
                    json_data['top_tutores'] = top_tutors.to_dict('records')
                
                st.download_button(
                    label="📄 **Exportar JSON Estruturado**",
                    data=json.dumps(json_data, indent=2, ensure_ascii=False),
                    file_name=f"dados_tri_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    type="secondary",
                    use_container_width=True
                )
            
            with col_r2:
                st.markdown("### 📈 **Informações**")
                st.info("""
                **Formatos disponíveis:**
                
                **📝 TXT:**
                - Relatório formatado em texto
                - Fácil de ler e compartilhar
                - Inclui análise completa
                
                **📊 CSV:**
                - Dados estruturados
                - Ideal para análise em planilhas
                - Múltiplas seções organizadas
                
                **📗 Excel/ZIP:**
                - Múltiplas abas/arquivos
                - Dados completos organizados
                - Inclui lista de tutores
                
                **📄 JSON:**
                - Dados estruturados
                - Ideal para integração com outros sistemas
                - Formato universal
                """)
                
                # Explicação dos parâmetros TRI
                with st.expander("📚 **Explicação dos Parâmetros TRI**", expanded=False):
                    st.markdown("""
                    ### 📊 **Parâmetros da Teoria de Resposta ao Item (TRI)**
                    
                    **1. Dificuldade (b)**
                    - **Valores negativos**: Questão fácil (alunos com baixa proficiência conseguem responder)
                    - **Valores próximos a 0**: Dificuldade média (alunos com proficiência média)
                    - **Valores positivos**: Questão difícil (apenas alunos com alta proficiência)
                    - **Faixa típica**: -3 (muito fácil) a +3 (muito difícil)
                    
                    **2. Discriminação (a)**
                    - **< 0.3**: Discriminação baixa (questão problemática, não diferencia bem os alunos)
                    - **0.3-0.6**: Discriminação moderada (questão aceitável)
                    - **> 0.6**: Discriminação alta (questão excelente, diferencia bem alunos bons e ruins)
                    - **Valores negativos**: Questão funciona inversamente (deve ser revisada)
                    
                    **3. Proficiência (θ)**
                    - **< -1.5**: Proficiência muito baixa (intervenção necessária)
                    - **-1.5 a -0.5**: Proficiência baixa (necessita reforço)
                    - **-0.5 a 0.5**: Proficiência média (desempenho adequado)
                    - **0.5 a 1.5**: Proficiência alta (bom desempenho)
                    - **> 1.5**: Proficiência muito alta (excelente desempenho)
                    - **Escala**: média = 0, desvio padrão = 1
                    """)

else:
    # Tela inicial
    st.markdown("""
    <div class="info-box">
    <h2 style="color: #8B5CF6;">🎯 Bem-vindo ao KAIROS!</h2>
    <p style="color: #F1F5F9; font-size: 1.1em;">
    <strong>Sistema de Análise Psicométrica</strong> para avaliações educacionais usando a <strong>Teoria de Resposta ao Item (TRI)</strong>.
    </p>
    
    <div style="background: rgba(139, 92, 246, 0.1); padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 4px solid #8B5CF6;">
    <h3 style="color: #A78BFA;">✨ Funcionalidades Principais</h3>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
        <div style="background: rgba(51, 65, 85, 0.8); padding: 1rem; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.3);">
            <span style="font-size: 1.5em; color: #8B5CF6;">📊</span><br>
            <strong style="color: #F1F5F9;">Análise Psicométrica</strong><br>
            <small style="color: #94A3B8;">Parâmetros TRI completos</small>
        </div>
        <div style="background: rgba(51, 65, 85, 0.8); padding: 1rem; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.3);">
            <span style="font-size: 1.5em; color: #8B5CF6;">👨‍🏫</span><br>
            <strong style="color: #F1F5F9;">Sistema de Tutores</strong><br>
            <small style="color: #94A3B8;">Identifica os 10 melhores alunos para tutoria</small>
        </div>
        <div style="background: rgba(51, 65, 85, 0.8); padding: 1rem; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.3);">
            <span style="font-size: 1.5em; color: #8B5CF6;">📝</span><br>
            <strong style="color: #F1F5F9;">Relatórios TXT/CSV</strong><br>
            <small style="color: #94A3B8;">Exportação completa e confiável</small>
        </div>
        <div style="background: rgba(51, 65, 85, 0.8); padding: 1rem; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.3);">
            <span style="font-size: 1.5em; color: #8B5CF6;">💾</span><br>
            <strong style="color: #F1F5F9;">Múltiplos Formatos</strong><br>
            <small style="color: #94A3B8;">CSV, Excel, JSON, ZIP</small>
        </div>
    </div>
    </div>
    
    <div style="background: rgba(16, 185, 129, 0.1); padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 4px solid #10B981;">
    <h3 style="color: #10B981;">🚀 Comece Agora</h3>
    <ol style="color: #F1F5F9; margin-left: 1.5rem;">
        <li>Configure o gabarito na barra lateral</li>
        <li>Adicione os alunos (manual ou CSV)</li>
        <li>Analise o panorama geral da turma</li>
        <li>Identifique os melhores tutores</li>
        <li>Exporte relatórios completos em TXT/CSV</li>
    </ol>
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "📊 Dashboard de Análise de Avaliações | Streamlit | Desenvolvedor: Mauricio A. Ribeiro"
    "</div>",
    unsafe_allow_html=True
)