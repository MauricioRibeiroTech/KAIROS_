import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import io
import base64
from datetime import datetime
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Análise de Redes Educacionais",
    page_icon="🎓",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #374151;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem;
    }
    .insight-box {
        background-color: #F0F9FF;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3B82F6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🎓 Análise de Redes Complexas - Desempenho Educacional</h1>', unsafe_allow_html=True)

# Funções auxiliares para geração de relatório HTML
def criar_imagem_rede_base64(G, pos, clusters, color_by, metodo_similaridade, limiar, config):
    """Cria uma imagem da rede e retorna em base64"""
    try:
        # Criar figura
        fig, ax = plt.subplots(figsize=(14, 11))
        
        # Configurar cores baseadas na métrica selecionada
        if color_by == "Grau de Conexão":
            node_color = [G.degree(node) for node in G.nodes()]
            cmap = plt.cm.viridis
            color_label = "Grau de Conexão"
        elif color_by == "Cluster":
            node_color = [clusters.get(node, -1) for node in G.nodes()]
            cmap = plt.cm.tab20c
            color_label = "Cluster"
        elif color_by == "Desempenho":
            node_color = [G.nodes[node].get('desempenho', 0.5) for node in G.nodes()]
            cmap = plt.cm.plasma
            color_label = "Desempenho"
        else:  # Centralidade
            if nx.is_connected(G):
                centrality = nx.betweenness_centrality(G)
                node_color = [centrality.get(node, 0) for node in G.nodes()]
            else:
                node_color = [0 for node in G.nodes()]
            cmap = plt.cm.coolwarm
            color_label = "Centralidade"
        
        # Tamanho dos nós baseado no grau
        node_size = [400 + G.degree(node) * 80 for node in G.nodes()]
        
        # Desenhar arestas primeiro (no fundo)
        nx.draw_networkx_edges(G, pos, alpha=0.2, width=1.5, edge_color='gray', ax=ax)
        
        # Desenhar nós
        nodes = nx.draw_networkx_nodes(G, pos, 
                                      node_size=node_size, 
                                      node_color=node_color, 
                                      cmap=cmap, 
                                      alpha=0.85, 
                                      ax=ax,
                                      edgecolors='white',
                                      linewidths=1.5)
        
        # Adicionar barra de cores
        sm = plt.cm.ScalarMappable(cmap=cmap, 
                                  norm=plt.Normalize(vmin=min(node_color), 
                                                    vmax=max(node_color)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
        cbar.set_label(color_label, fontsize=12, weight='bold')
        
        # Desenhar labels dos nós
        nx.draw_networkx_labels(G, pos, 
                               font_size=10, 
                               font_weight='bold',
                               font_color='black',
                               ax=ax)
        
        # Título e informações
        titulo = f"REDE DE SIMILARIDADE ENTRE ALUNOS\nMétodo: {metodo_similaridade} | Limiar: {limiar} | Layout: {config.get('layout', 'Spring')}"
        plt.title(titulo, fontsize=16, weight='bold', pad=20)
        
        # Legenda informativa
        info_text = f"""
        Total de Alunos: {G.number_of_nodes()}
        Conexões: {G.number_of_edges()}
        Densidade: {nx.density(G):.4f}
        Clusters Identificados: {len(set(clusters.values()) - {-1})}
        """
        
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        plt.axis('off')
        plt.tight_layout()
        
        # Salvar para buffer em alta resolução
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                   facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        st.error(f"Erro ao criar imagem da rede: {e}")
        return None

def gerar_relatorio_html(analise_data, config):
    """Gera um relatório HTML completo com todas as análises e imagem da rede"""
    
    # Extrair dados da análise
    df = analise_data['df']
    alunos_ids = analise_data['alunos_ids']
    respostas = analise_data['respostas']
    G = analise_data['grafo']
    matriz_sim = analise_data['matriz_similaridade']
    clusters = analise_data['clusters']
    desempenho = analise_data['desempenho']
    metricas_rede = analise_data['metricas_rede']
    analises_clusters = analise_data.get('analises_clusters', {})
    pos = analise_data.get('pos', None)
    
    # Data atual
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Gerar imagem da rede se houver posições
    img_base64 = None
    if pos is not None and G.number_of_edges() > 0:
        img_base64 = criar_imagem_rede_base64(
            G, pos, clusters, 
            config['color_by'], 
            config['metodo'],
            config['limiar'],
            config
        )
    
    # Início do HTML com CSS corrigido (sem gradientes de texto)
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório de Análise de Redes Educacionais</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto:wght@300;400;500&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
                color: #333333;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }}
            
            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .container::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 5px;
                background: linear-gradient(90deg, #1E3A8A, #3B82F6, #10B981);
            }}
            
            .header {{
                text-align: center;
                padding-bottom: 30px;
                border-bottom: 2px solid #e5e7eb;
                margin-bottom: 40px;
            }}
            
            .header h1 {{
                font-family: 'Poppins', sans-serif;
                font-size: 2.8rem;
                font-weight: 700;
                margin-bottom: 15px;
                color: #1E3A8A;
            }}
            
            .header-info {{
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 20px;
                flex-wrap: wrap;
            }}
            
            .header-info-item {{
                background: #f8fafc;
                padding: 10px 20px;
                border-radius: 10px;
                border-left: 4px solid #3B82F6;
                font-size: 0.95rem;
                color: #374151;
            }}
            
            .section {{
                margin-bottom: 40px;
                padding: 25px;
                background-color: #ffffff;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border-left: 5px solid #3B82F6;
                transition: transform 0.3s ease;
            }}
            
            .section:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }}
            
            .section h2 {{
                font-family: 'Poppins', sans-serif;
                color: #1E3A8A;
                border-bottom: 3px solid #e5e7eb;
                padding-bottom: 15px;
                margin-top: 0;
                font-size: 1.8rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                transition: transform 0.3s ease;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            }}
            
            .metric-value {{
                font-size: 2.2rem;
                font-weight: 700;
                margin: 10px 0;
                font-family: 'Poppins', sans-serif;
                color: white;
            }}
            
            .metric-label {{
                font-size: 0.9rem;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: rgba(255, 255, 255, 0.9);
            }}
            
            .network-image-container {{
                text-align: center;
                margin: 30px 0;
                padding: 20px;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 15px;
                border: 2px dashed #cbd5e1;
            }}
            
            .network-image {{
                max-width: 100%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                border: 1px solid #e5e7eb;
                transition: transform 0.3s ease;
            }}
            
            .network-image:hover {{
                transform: scale(1.01);
            }}
            
            .image-caption {{
                margin-top: 15px;
                font-style: italic;
                color: #64748b;
                font-size: 0.9rem;
            }}
            
            .table-container {{
                overflow-x: auto;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
                font-size: 0.95rem;
            }}
            
            th {{
                background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                position: sticky;
                top: 0;
            }}
            
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #e5e7eb;
                color: #374151;
            }}
            
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            
            tr:hover {{
                background-color: #e0f2fe;
                transition: background-color 0.2s ease;
            }}
            
            .highlight {{
                background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #ffc107;
                margin: 20px 0;
            }}
            
            .insight-box {{
                background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
                padding: 25px;
                border-radius: 12px;
                border-left: 5px solid #0ea5e9;
                margin: 25px 0;
            }}
            
            .cluster-info {{
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
                border: 1px solid #bae6fd;
                transition: transform 0.3s ease;
            }}
            
            .cluster-info:hover {{
                transform: translateX(5px);
            }}
            
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 30px;
                border-top: 2px solid #e5e7eb;
                color: #64748b;
                font-size: 0.9rem;
            }}
            
            .footer-logo {{
                font-size: 1.5rem;
                font-weight: bold;
                color: #3B82F6;
                margin-bottom: 10px;
                font-family: 'Poppins', sans-serif;
            }}
            
            .stats-summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            
            .stat-item {{
                text-align: center;
                padding: 20px;
                background: #f8fafc;
                border-radius: 12px;
                border: 2px solid #e2e8f0;
                transition: all 0.3s ease;
            }}
            
            .stat-item:hover {{
                border-color: #3B82F6;
                background: #ffffff;
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }}
            
            .icon {{
                font-size: 2rem;
                margin-bottom: 10px;
                display: block;
                color: #3B82F6;
            }}
            
            .config-badge {{
                display: inline-block;
                padding: 5px 12px;
                background: #3B82F6;
                color: white;
                border-radius: 20px;
                font-size: 0.85rem;
                margin: 0 5px;
                font-weight: 500;
            }}
            
            .print-button {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: #3B82F6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 50px;
                cursor: pointer;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                z-index: 1000;
                transition: all 0.3s ease;
            }}
            
            .print-button:hover {{
                background: #2563eb;
                transform: translateY(-2px);
                box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
            }}
            
            @media print {{
                .print-button {{
                    display: none;
                }}
                .container {{
                    box-shadow: none;
                }}
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 20px;
                }}
                .metric-grid {{
                    grid-template-columns: 1fr;
                }}
                .header h1 {{
                    font-size: 2rem;
                }}
            }}
            
            /* CORES DE TEXTO CORRIGIDAS */
            h1, h2, h3, h4, h5, h6 {{
                color: #1E3A8A;
            }}
            
            p, li, td, .header-info-item {{
                color: #374151;
            }}
            
            .stat-item .metric-value {{
                color: #1E3A8A;
            }}
            
            .stat-item .metric-label {{
                color: #64748b;
            }}
            
            .highlight h3 {{
                color: #dc2626;
            }}
            
            .insight-box h4 {{
                color: #1E3A8A;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Botão de impressão -->
            <button class="print-button" onclick="window.print()">🖨️ Imprimir Relatório</button>
            
            <div class="header">
                <h1>🎓 Relatório de Análise de Redes Educacionais</h1>
                <p style="color: #64748b;"><strong>Análise gerada em:</strong> {data_atual}</p>
                
                <div class="header-info">
                    <div class="header-info-item">
                        <strong style="color: #374151;">📊 Método:</strong> <span class="config-badge">{config['metodo']}</span>
                    </div>
                    <div class="header-info-item">
                        <strong style="color: #374151;">🎯 Limiar:</strong> <span class="config-badge">{config['limiar']}</span>
                    </div>
                    <div class="header-info-item">
                        <strong style="color: #374151;">🔄 Layout:</strong> <span class="config-badge">{config['layout']}</span>
                    </div>
                    <div class="header-info-item">
                        <strong style="color: #374151;">🎨 Colorir por:</strong> <span class="config-badge">{config['color_by']}</span>
                    </div>
                </div>
            </div>
    """
    
    # Seção 1: Resumo Geral
    html += f"""
            <div class="section">
                <h2>📊 Resumo Geral da Análise</h2>
                <div class="stats-summary">
                    <div class="stat-item">
                        <span class="icon">👥</span>
                        <div class="metric-value">{len(df)}</div>
                        <div class="metric-label">Total de Alunos</div>
                    </div>
                    <div class="stat-item">
                        <span class="icon">❓</span>
                        <div class="metric-value">{len(respostas.columns)}</div>
                        <div class="metric-label">Questões Analisadas</div>
                    </div>
                    <div class="stat-item">
                        <span class="icon">🔗</span>
                        <div class="metric-value">{G.number_of_edges()}</div>
                        <div class="metric-label">Conexões Identificadas</div>
                    </div>
                    <div class="stat-item">
                        <span class="icon">👨‍👩‍👧‍👦</span>
                        <div class="metric-value">{len(set(clusters.values()) - {-1})}</div>
                        <div class="metric-label">Clusters Detectados</div>
                    </div>
                </div>
            </div>
    """
    
    # Seção 2: Visualização da Rede (COM IMAGEM)
    if img_base64:
        html += f"""
            <div class="section">
                <h2>🕸️ Visualização da Rede de Similaridade</h2>
                <div class="network-image-container">
                    <img src="data:image/png;base64,{img_base64}" 
                         alt="Rede de Similaridade entre Alunos" 
                         class="network-image">
                    <div class="image-caption">
                        Figura 1: Rede de similaridade entre alunos. Cada nó representa um aluno, 
                        cada aresta indica similaridade acima do limiar de {config['limiar']}. 
                        Cores indicam {config['color_by'].lower()}.
                    </div>
                </div>
                
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value">{metricas_rede.get('densidade', 0):.4f}</div>
                        <div class="metric-label">Densidade da Rede</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metricas_rede.get('clustering_coef', 0):.3f}</div>
                        <div class="metric-label">Coeficiente de Aglomeração</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metricas_rede.get('n_componentes', 0)}</div>
                        <div class="metric-label">Componentes Conexos</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metricas_rede.get('grau_medio', 0):.1f}</div>
                        <div class="metric-label">Grau Médio por Aluno</div>
                    </div>
                </div>
            </div>
        """
    
    # Seção 3: Análise de Clusters
    if analises_clusters:
        html += """
            <div class="section">
                <h2>👥 Análise Detalhada dos Clusters</h2>
        """
        
        for cluster_id, analise in analises_clusters.items():
            html += f"""
                <div class="cluster-info">
                    <h3 style="color: #1E3A8A; margin-top: 0;">Cluster {cluster_id}</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0;">
                        <div>
                            <strong style="color: #374151;">👥 Alunos ({analise['n_alunos']}):</strong><br>
                            <div style="margin-top: 5px; font-size: 0.9rem; color: #64748b;">
                                {', '.join(analise['alunos'][:8])}{'...' if len(analise['alunos']) > 8 else ''}
                            </div>
                        </div>
                        <div>
                            <strong style="color: #374151;">📊 Métricas:</strong><br>
                            <span style="color: #64748b;">
                            • Desempenho Médio: {analise.get('desempenho_medio', 0):.2f}<br>
                            • Questões Consistentes: {analise.get('questoes_consistentes', 0)}/{len(respostas.columns)}<br>
                            • Tamanho do Cluster: {analise['n_alunos']} alunos
                            </span>
                        </div>
                    </div>
            """
            
            # Padrões fortes
            padroes_fortes = []
            if 'padroes_resposta' in analise:
                for questao, dados in analise['padroes_resposta'].items():
                    if dados.get('consistencia', 0) > 0.7:
                        padroes_fortes.append(f"{questao}: {dados.get('alternativa_mais_comum', 'N/A')} ({dados['consistencia']:.0%})")
            
            if padroes_fortes:
                html += f"""
                    <div style="margin-top: 10px;">
                        <strong style="color: #374151;">🎯 Padrões Fortes (>70% consistência):</strong><br>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 5px;">
                """
                for padrao in padroes_fortes[:6]:
                    html += f'<span style="background: #3B82F6; color: white; padding: 4px 10px; border-radius: 15px; font-size: 0.85rem;">{padrao}</span>'
                html += "</div></div>"
            
            html += "</div>"
        
        html += "</div>"
    
    # Seção 4: Top Alunos
    if 'df_metricas' in analise_data:
        df_metricas = analise_data['df_metricas']
        html += """
            <div class="section">
                <h2>🏆 Ranking de Alunos</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Posição</th>
                                <th>Aluno</th>
                                <th>Conexões (Grau)</th>
                                <th>Cluster</th>
                                <th>Desempenho</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Ordenar por grau
        df_rank = df_metricas.sort_values('Grau', ascending=False)
        for idx, (_, row) in enumerate(df_rank.head(15).iterrows(), 1):
            status = ""
            if row['Grau'] >= df_rank['Grau'].quantile(0.75):
                status = "🔷 Muito Conectado"
            elif row['Grau'] <= df_rank['Grau'].quantile(0.25):
                status = "🔶 Pouco Conectado"
            else:
                status = "⚪ Conectividade Média"
            
            html += f"""
                            <tr>
                                <td style="color: #374151;">{idx}º</td>
                                <td><strong style="color: #1E3A8A;">{row['Aluno']}</strong></td>
                                <td style="color: #374151;">{row['Grau']}</td>
                                <td style="color: #374151;">{row.get('Cluster', 'N/A')}</td>
                                <td style="color: #374151;">{row.get('Desempenho', 0):.3f}</td>
                                <td style="color: #374151;">{status}</td>
                            </tr>
            """
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        """
    
    # Seção 5: Alunos Isolados
    alunos_isolados = [node for node in G.nodes() if G.degree(node) == 0]
    if alunos_isolados:
        html += f"""
            <div class="section">
                <h2>🔍 Alunos Isolados - Atenção Especial</h2>
                <div class="highlight">
                    <h3 style="color: #dc2626; margin-top: 0;">⚠️ {len(alunos_isolados)} Alunos Isolados Identificados</h3>
                    <p style="color: #374151;"><strong>Lista de alunos:</strong> {', '.join(alunos_isolados)}</p>
                    <div style="background: #fee2e2; padding: 15px; border-radius: 8px; margin-top: 15px;">
                        <strong style="color: #dc2626;">📝 Recomendações Pedagógicas:</strong>
                        <ul style="margin: 10px 0 0 20px; color: #374151;">
                            <li>Avaliação individualizada para entender padrões de resposta únicos</li>
                            <li>Atendimento personalizado para identificar dificuldades específicas</li>
                            <li>Inserção estratégica em grupos de trabalho</li>
                            <li>Monitoramento contínuo do progresso</li>
                        </ul>
                    </div>
                </div>
            </div>
        """
    
    # Seção 6: Insights Pedagógicos
    html += """
            <div class="section">
                <h2>💡 Insights e Recomendações Pedagógicas</h2>
                <div class="insight-box">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        <div>
                            <h4 style="color: #1E3A8A; margin-top: 0;">🎯 Para o Professor</h4>
                            <ul style="color: #374151;">
                                <li><strong>Formação de grupos:</strong> Use os clusters para criar grupos homogêneos ou heterogêneos conforme objetivo</li>
                                <li><strong>Intervenções direcionadas:</strong> Foque nas questões com baixa consistência entre os alunos</li>
                                <li><strong>Monitoramento:</strong> Alunos centrais podem atuar como monitores ou líderes</li>
                                <li><strong>Personalização:</strong> Adapte o ensino baseado nos padrões identificados</li>
                            </ul>
                        </div>
                        <div>
                            <h4 style="color: #1E3A8A; margin-top: 0;">👥 Para Trabalho em Equipe</h4>
                            <ul style="color: #374151;">
                                <li><strong>Grupos homogêneos:</strong> Ideal para atividades niveladas e reforço específico</li>
                                <li><strong>Grupos heterogêneos:</strong> Promove diversidade de pensamento e aprendizado colaborativo</li>
                                <li><strong>Tutoria entre pares:</strong> Alunos fortes podem ajudar os com mais dificuldades</li>
                                <li><strong>Projetos colaborativos:</strong> Use a rede para formar equipes complementares</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
    """
    
    # Seção 7: Estatísticas de Similaridade
    if matriz_sim is not None:
        simil_triang = matriz_sim[np.triu_indices_from(matriz_sim, k=1)]
        html += f"""
            <div class="section">
                <h2>📈 Estatísticas de Similaridade</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value">{simil_triang.mean():.3f}</div>
                        <div class="metric-label">Similaridade Média</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{simil_triang.max():.3f}</div>
                        <div class="metric-label">Similaridade Máxima</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{simil_triang.min():.3f}</div>
                        <div class="metric-label">Similaridade Mínima</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{simil_triang.std():.3f}</div>
                        <div class="metric-label">Desvio Padrão</div>
                    </div>
                </div>
                
                <div style="background: #f1f5f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <strong style="color: #374151;">Interpretação:</strong>
                    <ul style="margin: 10px 0 0 20px; color: #374151;">
                        <li><strong>Similaridade alta (>0.7):</strong> Alunos com padrões de resposta muito similares</li>
                        <li><strong>Similaridade média (0.4-0.7):</strong> Padrões moderadamente similares</li>
                        <li><strong>Similaridade baixa (<0.4):</strong> Padrões de resposta distintos</li>
                    </ul>
                </div>
            </div>
        """
    
    # Seção 8: Configurações Técnicas
    html += f"""
            <div class="section">
                <h2>⚙️ Configurações Técnicas da Análise</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor Configurado</th>
                                <th>Descrição</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="color: #374151;"><strong>Método de Similaridade</strong></td>
                                <td><span class="config-badge">{config['metodo']}</span></td>
                                <td style="color: #64748b;">Algoritmo utilizado para calcular similaridade entre respostas dos alunos</td>
                            </tr>
                            <tr>
                                <td style="color: #374151;"><strong>Limiar de Conexão</strong></td>
                                <td><span class="config-badge">{config['limiar']}</span></td>
                                <td style="color: #64748b;">Valor mínimo de similaridade para criar uma conexão entre dois alunos</td>
                            </tr>
                            <tr>
                                <td style="color: #374151;"><strong>Layout da Rede</strong></td>
                                <td><span class="config-badge">{config['layout']}</span></td>
                                <td style="color: #64748b;">Algoritmo de posicionamento visual dos nós na rede</td>
                            </tr>
                            <tr>
                                <td style="color: #374151;"><strong>Coloração dos Nós</strong></td>
                                <td><span class="config-badge">{config['color_by']}</span></td>
                                <td style="color: #64748b;">Métrica utilizada para determinar a cor de cada aluno na rede</td>
                            </tr>
                            <tr>
                                <td style="color: #374151;"><strong>Tamanho Mínimo de Cluster</strong></td>
                                <td><span class="config-badge">{config.get('min_cluster_size', 5)}</span></td>
                                <td style="color: #64748b;">Número mínimo de alunos para considerar um grupo como cluster válido</td>
                            </tr>
                            <tr>
                                <td style="color: #374151;"><strong>Normalização</strong></td>
                                <td><span class="config-badge">{'Sim' if config.get('normalizar_similaridade', True) else 'Não'}</span></td>
                                <td style="color: #64748b;">Se os valores de similaridade foram normalizados para escala 0-1</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
    """
    
    # Rodapé
    html += f"""
            <div class="footer">
                <div class="footer-logo">🎓 Análise de Redes Educacionais</div>
                <p style="color: #64748b;">Relatório gerado automaticamente pela Ferramenta de Análise Pedagógica Baseada em Dados</p>
                <p style="color: #64748b;"><strong>Data de geração:</strong> {data_atual}</p>
                <p style="color: #64748b;">© {datetime.now().year} - Todos os direitos reservados | Ferramenta para educadores e pesquisadores</p>
            </div>
        </div>
        
        <script>
            // Adicionar funcionalidade de impressão
            document.addEventListener('DOMContentLoaded', function() {{
                // Adicionar números de página para impressão
                const style = document.createElement('style');
                style.innerHTML = `
                    @media print {{
                        @page {{
                            margin: 20mm;
                            size: A4;
                        }}
                        body {{
                            font-size: 12pt;
                            color: black !important;
                        }}
                        .section {{
                            page-break-inside: avoid;
                        }}
                        .network-image {{
                            max-width: 80%;
                        }}
                        h1, h2, h3, h4, h5, h6 {{
                            color: black !important;
                        }}
                        p, li, td {{
                            color: black !important;
                        }}
                    }}
                `;
                document.head.appendChild(style);
            }});
        </script>
    </body>
    </html>
    """
    
    return html

# Sidebar - Configurações
with st.sidebar:
    st.markdown("### ⚙️ Configurações da Análise")
    
    metodo_similaridade = st.selectbox(
        "Método de Similaridade",
        ["Cosseno", "Jaccard", "Correlação"],
        help="Escolha o método para calcular similaridade entre respostas"
    )
    
    limiar = st.slider(
        "Limiar de Similaridade",
        min_value=0.0,
        max_value=1.0,
        value=0.65,
        step=0.05,
        help="Define o mínimo de similaridade para criar conexões entre alunos"
    )
    
    st.markdown("### 👁️ Visualização")
    layout_rede = st.selectbox(
        "Layout da Rede",
        ["Spring", "Circular", "Kamada-Kawai", "Spectral"],
        help="Algoritmo de posicionamento dos nós"
    )
    
    color_by = st.selectbox(
        "Colorir nós por",
        ["Grau de Conexão", "Cluster", "Desempenho", "Centralidade"],
        help="Escolha a métrica para colorir os nós"
    )
    
    with st.expander("⚡ Opções Avançadas"):
        min_cluster_size = st.slider("Tamanho mínimo de cluster", 3, 10, 5)
        mostrar_isolados = st.checkbox("Mostrar alunos isolados", value=True)
        normalizar_similaridade = st.checkbox("Normalizar similaridade", value=True)

# [O RESTANTE DO CÓDIGO PERMANECE IGUAL - funções de análise e interface principal]
# [Copiar aqui todas as outras funções e a interface principal do código anterior]

# Funções de análise (mantidas do código anterior)
def calcular_desempenho(respostas, gabarito=None):
    """
    Calcula desempenho dos alunos
    Se gabarito fornecido, calcula acertos, senão calcula consistência
    """
    if gabarito is not None:
        acertos = (respostas == gabarito).sum(axis=1)
        desempenho = acertos / len(respostas.columns)
    else:
        respostas_numeric = respostas.applymap(lambda x: ord(str(x)) - 64 if str(x).isalpha() else 0)
        min_val = respostas_numeric.min().min()
        max_val = respostas_numeric.max().max()
        if max_val > min_val:
            respostas_norm = (respostas_numeric - min_val) / (max_val - min_val)
            consistencia = 1 - respostas_norm.std(axis=1)
        else:
            consistencia = pd.Series(1, index=respostas.index)
        desempenho = consistencia.values
    
    return desempenho

def detectar_clusters_educacionais(G, min_size=5):
    """
    Detecta clusters de alunos com padrões de resposta similares
    """
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(G)
    except:
        partition = {}
        for i, component in enumerate(nx.connected_components(G)):
            for node in component:
                partition[node] = i
    
    if partition:
        cluster_counts = pd.Series(list(partition.values())).value_counts()
        clusters_validos = cluster_counts[cluster_counts >= min_size].index
        
        cluster_final = {}
        for node, cluster_id in partition.items():
            if cluster_id in clusters_validos:
                cluster_final[node] = cluster_id
            else:
                cluster_final[node] = -1
    else:
        cluster_final = {node: -1 for node in G.nodes()}
    
    return cluster_final

def analise_pedagogica(df_respostas, clusters):
    """
    Realiza análise pedagógica dos clusters detectados
    """
    analises = {}
    
    for cluster_id in set(clusters.values()):
        if cluster_id == -1:
            continue
            
        alunos_cluster = [aluno for aluno, cid in clusters.items() if cid == cluster_id]
        respostas_cluster = df_respostas.loc[df_respostas['Aluno'].isin(alunos_cluster)]
        
        padroes = {}
        for questao in df_respostas.columns[1:]:
            distribuicao = respostas_cluster[questao].value_counts(normalize=True)
            if not distribuicao.empty:
                alternativa_mais_comum = distribuicao.idxmax()
                consistencia = distribuicao.max()
            else:
                alternativa_mais_comum = None
                consistencia = 0
                
            padroes[questao] = {
                'alternativa_mais_comum': alternativa_mais_comum,
                'consistencia': consistencia,
                'distribuicao': dict(distribuicao)
            }
        
        desempenho_cluster = respostas_cluster.drop('Aluno', axis=1).apply(
            lambda x: pd.Series(x).value_counts(normalize=True).max() if not x.empty else 0, 
            axis=0
        ).mean()
        
        analises[cluster_id] = {
            'n_alunos': len(alunos_cluster),
            'padroes_resposta': padroes,
            'alunos': alunos_cluster,
            'desempenho_medio': desempenho_cluster,
            'questoes_consistentes': sum(1 for p in padroes.values() if p['consistencia'] > 0.7)
        }
    
    return analises

def calcular_matriz_similaridade(respostas, metodo="Cosseno"):
    """
    Calcula matriz de similaridade baseada no método escolhido
    """
    n_alunos = len(respostas)
    
    if metodo == "Cosseno":
        respostas_encoded = pd.get_dummies(respostas, prefix='', prefix_sep='')
        matriz_sim = cosine_similarity(respostas_encoded.values)
    
    elif metodo == "Jaccard":
        matriz_sim = np.zeros((n_alunos, n_alunos))
        for i in range(n_alunos):
            for j in range(n_alunos):
                if i == j:
                    matriz_sim[i, j] = 1.0
                else:
                    resp_i = respostas.iloc[i]
                    resp_j = respostas.iloc[j]
                    
                    set_i = set((idx, val) for idx, val in enumerate(resp_i))
                    set_j = set((idx, val) for idx, val in enumerate(resp_j))
                    
                    intersecao = len(set_i.intersection(set_j))
                    uniao = len(set_i.union(set_j))
                    
                    if uniao > 0:
                        matriz_sim[i, j] = intersecao / uniao
                    else:
                        matriz_sim[i, j] = 0.0
    
    elif metodo == "Correlação":
        respostas_numeric = respostas.applymap(
            lambda x: ord(str(x)) - 64 if str(x).isalpha() else 0
        )
        matriz_sim = np.corrcoef(respostas_numeric.values)
        matriz_sim = (matriz_sim + 1) / 2
    
    else:
        raise ValueError(f"Método {metodo} não reconhecido")
    
    return matriz_sim

# Interface principal
uploaded_file = st.file_uploader(
    "📤 Faça upload do arquivo CSV com as respostas dos alunos", 
    type=['csv'],
    help="Formato esperado: Coluna 'Aluno' seguida por colunas Q1, Q2, ..."
)

if uploaded_file is not None:
    # Ler e processar dados
    df = pd.read_csv(uploaded_file)
    
    # Verificar formato
    if 'Aluno' not in df.columns:
        st.error("❌ O arquivo CSV deve conter uma coluna chamada 'Aluno'")
        st.stop()
    
    # Separar identificadores e respostas
    alunos_ids = df['Aluno'].tolist()
    respostas = df.drop(columns=['Aluno'])
    
    # Calcular matriz de similaridade
    with st.spinner(f'Calculando similaridade usando método {metodo_similaridade}...'):
        matriz_sim = calcular_matriz_similaridade(respostas, metodo_similaridade)
    
    if normalizar_similaridade:
        min_sim = matriz_sim.min()
        max_sim = matriz_sim.max()
        if max_sim > min_sim:
            matriz_sim = (matriz_sim - min_sim) / (max_sim - min_sim)
    
    # Construir grafo
    G = nx.Graph()
    
    # Adicionar nós com atributos
    desempenho = calcular_desempenho(respostas)
    for i, aluno in enumerate(alunos_ids):
        G.add_node(aluno, 
                  desempenho=desempenho[i],
                  index=i)
    
    # Adicionar arestas baseadas no limiar
    conexoes_criadas = 0
    for i in range(len(alunos_ids)):
        for j in range(i+1, len(alunos_ids)):
            if matriz_sim[i, j] >= limiar:
                G.add_edge(alunos_ids[i], alunos_ids[j], 
                          weight=matriz_sim[i, j],
                          thickness=matriz_sim[i, j] * 3)
                conexoes_criadas += 1
    
    # Detectar clusters
    clusters = detectar_clusters_educacionais(G, min_cluster_size)
    
    # Análise pedagógica
    analises_clusters = {}
    if conexoes_criadas > 0:
        analises_clusters = analise_pedagogica(df, clusters)
    
    # Calcular métricas da rede
    metricas_rede = {}
    if conexoes_criadas > 0:
        metricas_rede['densidade'] = nx.density(G)
        metricas_rede['clustering_coef'] = nx.average_clustering(G)
        metricas_rede['n_componentes'] = nx.number_connected_components(G)
        metricas_rede['grau_medio'] = np.mean([d for _, d in G.degree()])
    
    # Preparar métricas por aluno
    df_metricas = pd.DataFrame({
        'Aluno': alunos_ids,
        'Grau': [G.degree(aluno) for aluno in alunos_ids],
        'Cluster': [clusters.get(aluno, -1) for aluno in alunos_ids],
        'Desempenho': desempenho
    })
    
    # ========== VISUALIZAÇÃO INTERATIVA ==========
    st.markdown('<h2 class="sub-header">🕸️ Visualização da Rede</h2>', unsafe_allow_html=True)
    
    if conexoes_criadas > 0:
        # Layout da rede
        if layout_rede == "Spring":
            pos = nx.spring_layout(G, seed=42, k=2)
        elif layout_rede == "Circular":
            pos = nx.circular_layout(G)
        elif layout_rede == "Kamada-Kawai":
            pos = nx.kamada_kawai_layout(G)
        else:  # Spectral
            pos = nx.spectral_layout(G)
        
        # Preparar dados das arestas
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(edge[2]['weight'])
        
        # Preparar dados dos nós
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        node_hover = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Informações do nó
            grau = G.degree(node)
            cluster_id = clusters.get(node, -1)
            
            node_text.append(f"{node}")
            node_size.append(15 + grau * 3)
            
            # Cor baseada na métrica selecionada
            if color_by == "Grau de Conexão":
                node_color.append(grau)
                color_title = "Grau de Conexão"
            elif color_by == "Cluster":
                node_color.append(cluster_id if cluster_id != -1 else -2)
                color_title = "Cluster"
            elif color_by == "Desempenho":
                node_color.append(G.nodes[node].get('desempenho', 0.5))
                color_title = "Desempenho"
            else:  # Centralidade
                if nx.is_connected(G):
                    centrality = nx.betweenness_centrality(G).get(node, 0)
                else:
                    centrality = 0
                node_color.append(centrality)
                color_title = "Centralidade"
            
            # Texto hover
            similaridade_media_val = np.mean([G[node][nbr]['weight'] for nbr in G.neighbors(node)]) if grau > 0 else None
            similaridade_media_str = f"{similaridade_media_val:.3f}" if similaridade_media_val is not None else "N/A"
            
            hover_text = f"""
            <b>Aluno:</b> {node}<br>
            <b>Conexões:</b> {grau}<br>
            <b>Cluster:</b> {cluster_id if cluster_id != -1 else 'Nenhum'}<br>
            <b>Desempenho:</b> {G.nodes[node].get('desempenho', 0):.3f}<br>
            <b>Similaridade Média:</b> {similaridade_media_str}
            """
            node_hover.append(hover_text)
        
        # Criar figura da rede
        fig_rede = go.Figure()
        
        # Adicionar arestas
        if edge_x:
            fig_rede.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='rgba(100, 100, 100, 0.3)'),
                hoverinfo='none',
                mode='lines',
                name='Conexões'
            ))
        
        # Adicionar nós
        fig_rede.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=color_title),
                line=dict(width=2, color='white')
            ),
            text=node_text,
            textposition="top center",
            hovertext=node_hover,
            hoverinfo='text',
            name='Alunos'
        ))
        
        fig_rede.update_layout(
            title=f"Rede de Similaridade (Limiar: {limiar}, Método: {metodo_similaridade})",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=700,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_rede, use_container_width=True)
    else:
        st.warning(f"⚠️ Nenhuma conexão criada com o limiar atual ({limiar}). Tente reduzir o limiar.")
        pos = None
    
    # ========== MÉTRICAS E ANÁLISES ==========
    st.markdown('<h2 class="sub-header">📊 Métricas da Análise</h2>', unsafe_allow_html=True)
    
    if conexoes_criadas > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Densidade", f"{metricas_rede.get('densidade', 0):.4f}")
        with col2:
            st.metric("Coef. Aglomeração", f"{metricas_rede.get('clustering_coef', 0):.3f}")
        with col3:
            st.metric("Componentes", metricas_rede.get('n_componentes', 0))
        with col4:
            st.metric("Grau Médio", f"{metricas_rede.get('grau_medio', 0):.1f}")
    
    # ========== BOTÃO PARA GERAR RELATÓRIO HTML ==========
    st.markdown('<h2 class="sub-header">📋 Exportar Relatório Completo</h2>', unsafe_allow_html=True)
    
    # Preparar dados para o relatório
    analise_data = {
        'df': df,
        'alunos_ids': alunos_ids,
        'respostas': respostas,
        'grafo': G,
        'matriz_similaridade': matriz_sim,
        'clusters': clusters,
        'desempenho': desempenho,
        'metricas_rede': metricas_rede,
        'df_metricas': df_metricas,
        'analises_clusters': analises_clusters,
        'pos': pos if 'pos' in locals() else None
    }
    
    config = {
        'metodo': metodo_similaridade,
        'limiar': limiar,
        'layout': layout_rede,
        'color_by': color_by,
        'min_cluster_size': min_cluster_size,
        'normalizar_similaridade': normalizar_similaridade
    }
    
    # Botão para gerar relatório
    if st.button("📄 Gerar Relatório HTML Completo", type="primary", use_container_width=True):
        with st.spinner("Gerando relatório completo com imagem da rede..."):
            try:
                # Gerar HTML com imagem
                html_content = gerar_relatorio_html(analise_data, config)
                
                # Nome do arquivo
                nome_arquivo = f"relatorio_redes_educacionais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                
                # Mostrar preview do relatório
                with st.expander("👁️ Prévia do Relatório", expanded=True):
                    st.markdown("""
                    **O relatório inclui:**
                    - 📊 Resumo geral da análise
                    - 🕸️ **Imagem da rede** em alta qualidade
                    - 👥 Análise detalhada dos clusters
                    - 🏆 Ranking dos alunos mais conectados
                    - 🔍 Identificação de alunos isolados
                    - 💡 Insights pedagógicos
                    - 📈 Estatísticas de similaridade
                    - ⚙️ Configurações técnicas
                    
                    *Clique no botão abaixo para baixar o relatório completo em HTML*
                    """)
                
                # Botão para download
                st.download_button(
                    label="⬇️ Baixar Relatório HTML (com imagem)",
                    data=html_content,
                    file_name=nome_arquivo,
                    mime="text/html",
                    help="Baixe um relatório HTML completo com imagem da rede incluída",
                    type="secondary",
                    use_container_width=True
                )
                
                st.success("✅ Relatório gerado com sucesso! Todas as fontes agora são visíveis.")
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar relatório: {e}")
    
    # ========== DOWNLOADS ADICIONAIS ==========
    col_down1, col_down2, col_down3 = st.columns(3)
    
    with col_down1:
        # Métricas por aluno
        csv_metricas = df_metricas.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📊 Baixar Métricas CSV",
            data=csv_metricas,
            file_name="metricas_alunos.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_down2:
        # Matriz de similaridade
        df_matriz = pd.DataFrame(matriz_sim, index=alunos_ids, columns=alunos_ids)
        csv_matriz = df_matriz.to_csv(encoding='utf-8-sig')
        st.download_button(
            label="🔗 Baixar Matriz Similaridade",
            data=csv_matriz,
            file_name="matriz_similaridade.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_down3:
        # Imagem da rede
        if conexoes_criadas > 0 and 'pos' in locals():
            # Gerar imagem
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Configurar cores
            if color_by == "Grau de Conexão":
                node_color = [G.degree(node) for node in G.nodes()]
                cmap = plt.cm.viridis
            elif color_by == "Cluster":
                node_color = [clusters.get(node, -1) for node in G.nodes()]
                cmap = plt.cm.Set3
            elif color_by == "Desempenho":
                node_color = [G.nodes[node].get('desempenho', 0.5) for node in G.nodes()]
                cmap = plt.cm.plasma
            else:
                node_color = [0 for node in G.nodes()]
                cmap = plt.cm.coolwarm
            
            node_size = [300 + G.degree(node) * 50 for node in G.nodes()]
            
            nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                                  node_color=node_color, cmap=cmap, 
                                  alpha=0.8, ax=ax)
            nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=9, ax=ax)
            
            plt.title(f"Rede de Similaridade\n{metodo_similaridade}, Limiar: {limiar}")
            plt.axis('off')
            
            # Salvar para buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            buf.seek(0)
            
            st.download_button(
                label="🖼️ Baixar Imagem da Rede",
                data=buf,
                file_name="rede_similaridade.png",
                mime="image/png",
                use_container_width=True
            )

else:
    # Tela inicial quando não há arquivo
    st.info("👆 **Faça upload de um arquivo CSV para começar a análise**")
    
    # Exemplo de formato
    with st.expander("📋 Exemplo do formato esperado", expanded=True):
        st.code("""
        Aluno,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10
        A1,A,B,C,D,A,B,C,D,A,B
        A2,B,C,D,A,B,C,D,A,B,C
        A3,A,B,C,D,A,B,C,D,A,B
        A4,C,D,A,B,C,D,A,B,C,D
        A5,D,A,B,C,D,A,B,C,D,A
        ...""", language="csv")
        
        st.markdown("""
        **Requisitos do arquivo:**
        - Primeira coluna deve chamar-se `Aluno`
        - Demais colunas são as questões (Q1, Q2, ...)
        - Respostas podem ser A, B, C, D ou qualquer letra/número
        - Não pode haver linhas vazias
        """)

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    🎓 <b>Análise de Redes Educacionais</b> | 
    Ferramenta para análise pedagógica baseada em dados | 
    Desenvolvido para educadores e pesquisadores
</div>
""", unsafe_allow_html=True)