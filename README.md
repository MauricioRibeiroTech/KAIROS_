# KAIROS - Sistema de Análise de Avaliações com TRI

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 📋 Sobre o Projeto

**KAIROS** é um sistema de análise psicométrica avançada para avaliações educacionais que utiliza a **Teoria de Resposta ao Item (TRI)**. A aplicação permite que educadores analisem o desempenho de alunos de forma detalhada, identifiquem potencial tutores e exportem relatórios completos em múltiplos formatos.

### ✨ Funcionalidades Principais

- 📊 **Análise Psicométrica Completa** com parâmetros TRI
- 👨‍🏫 **Sistema de Identificação de Tutores** entre alunos
- 📝 **Exportação Multi-Formato** (TXT, CSV, Excel, JSON, ZIP)
- 🎯 **Dashboard Interativo** com visualizações avançadas
- 👤 **Análise Individual** com recomendações pedagógicas
- 💾 **Processamento Flexível** (entrada manual ou CSV)

## 🚀 Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Interface web interativa
- **Pandas** - Manipulação de dados
- **NumPy** - Cálculos numéricos
- **Plotly** - Visualizações gráficas
- **SciPy** - Análises estatísticas
- **Openpyxl** (opcional) - Exportação para Excel

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)

### Instalação dos Dependências

```bash
# Clone o repositório (ou baixe os arquivos)
git clone https://github.com/seu-usuario/kairos-analise.git
cd kairos-analise

# Instale as dependências
pip install streamlit pandas numpy plotly scipy openpyxl

# Para instalação completa com todas as dependências
pip install -r requirements.txt
```

### 📦 requirements.txt (crie o arquivo se necessário)
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
scipy>=1.11.0
openpyxl>=3.1.0
```

## 🎯 Como Usar

### 1. Configuração Inicial

Execute o aplicativo Streamlit:

```bash
streamlit run 1_V01.py
```

### 2. Configurar o Gabarito

Na barra lateral:
- Digite as respostas corretas (ex: `A, B, C, D, A, B, C, D, E, A`)
- O sistema automaticamente identifica o número de questões

### 3. Adicionar Alunos

**Duas opções disponíveis:**

#### ✍️ Inserção Manual
- Defina o número de alunos
- Preencha nome e respostas para cada aluno
- Interface organizada por colunas para fácil preenchimento

#### 📁 Upload de CSV
- Formato esperado: primeira coluna = nomes, demais colunas = respostas
- Respostas devem estar em formato de letras (A, B, C, D, E)
- O sistema converte automaticamente para análise binária

### 4. Análise dos Resultados

O sistema automaticamente processa os dados e gera:

#### 📊 Dashboard Principal
- **Métricas Gerais**: Número de alunos, proficiência média, taxa de acerto
- **Gráficos Interativos**: Distribuição de proficiências, análise multidimensional das questões
- **Ranking de Alunos**: Top 10 por proficiência
- **Panorama da Turma**: Visão geral em 4 gráficos integrados

#### 👨‍🎓 Análise Individual
- Seleção de aluno específico
- Métricas detalhadas (proficiência, pontuação, posição no ranking)
- Gráfico de desempenho por questão
- Recomendações pedagógicas personalizadas

#### 👨‍🏫 Sistema de Tutores
- Identificação automática dos 10 melhores alunos para tutoria
- Critérios: proficiência > 1.0 e taxa de acerto > 70%
- Sugestões para formação de grupos de estudo
- Exportação da lista de tutores

#### 📝 Exportação de Dados
- **TXT**: Relatório formatado em texto simples
- **CSV**: Dados estruturados com múltiplas seções
- **Excel/ZIP**: Dados completos organizados (depende do openpyxl)
- **JSON**: Estrutura de dados para integração com outros sistemas

## 📊 Parâmetros TRI Explicados

### 1. Dificuldade (b)
- **Valores negativos**: Questão fácil
- **Valores próximos a 0**: Dificuldade média
- **Valores positivos**: Questão difícil
- **Faixa típica**: -3 a +3

### 2. Discriminação (a)
- **< 0.3**: Discriminação baixa (questão problemática)
- **0.3-0.6**: Discriminação moderada
- **> 0.6**: Discriminação alta (questão excelente)
- **Valores negativos**: Questão funciona inversamente

### 3. Proficiência (θ)
- **< -1.5**: Proficiência muito baixa
- **-1.5 a -0.5**: Proficiência baixa
- **-0.5 a 0.5**: Proficiência média
- **0.5 a 1.5**: Proficiência alta
- **> 1.5**: Proficiência muito alta

## 🎨 Tema Visual

A aplicação utiliza um **tema escuro elegante** com:
- **Cores principais**: Roxo (#8B5CF6) para elementos-chave
- **Cartões interativos**: Com efeitos hover e gradientes
- **Gráficos personalizados**: Tema escuro para melhor visualização
- **Layout responsivo**: Adaptado para diferentes tamanhos de tela

## 📁 Estrutura do Código

```
kairos-analise/
│
├── 1_V01.py              # Arquivo principal da aplicação
│
├── classes/
│   ├── TRI_Simulator     # Classe para simulação TRI
│   └── (outras classes)
│
├── functions/
│   ├── analysis.py       # Funções de análise
│   ├── plots.py          # Funções para gráficos
│   ├── reports.py        # Geração de relatórios
│   └── utils.py          # Utilitários gerais
│
└── README.md             # Este arquivo
```

## 🔧 Funcionalidades Técnicas

### Análise Avançada
- Implementação do modelo 2PL (dois parâmetros) da TRI
- Cálculo de correlação bisserial pontual
- Índice de discriminação entre grupos de alta e baixa proficiência
- Curvas características de item (CCI)

### Processamento de Dados
- Conversão automática de respostas para binário
- Tratamento de valores ausentes
- Validação de consistência dos dados
- Cache de resultados para performance

### Exportação Flexível
- Fallback automático (Excel → ZIP quando openpyxl não disponível)
- Relatórios formatados em TXT com explicações pedagógicas
- CSV estruturado com múltiplas seções
- JSON para integração com outras ferramentas

## 🚨 Observações Importantes

### Dependência Opcional
- **openpyxl**: Necessário apenas para exportação em Excel
- Sem esta biblioteca, a exportação usa formato ZIP com múltiplos CSVs

### Limitações Conhecidas
- Suporta até 50 alunos em modo manual
- Respostas devem ser A, B, C, D ou E
- Requer gabarito consistente com número de questões

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Desenvolvedor

**Mauricio A. Ribeiro**
- Desenvolvedor: Sistema de análise educacional
- Contato: [LinkedIn](#) | [GitHub](#)

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📞 Suporte

Para problemas, dúvidas ou sugestões:
- Abra uma [issue](https://github.com/seu-usuario/kairos-analise/issues)
- Verifique a [documentação](#)
- Entre em contato com o desenvolvedor

---

**🎯 KAIROS - Transformando dados em insights pedagógicos**
