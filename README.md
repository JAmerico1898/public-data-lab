# 🏦 Laboratório de Dados Públicos

Aplicação interativa para explorar, visualizar e exportar dados do **Portal de Dados Abertos do Banco Central do Brasil**.

Construída com [Streamlit](https://streamlit.io/) e a biblioteca [python-bcb](https://github.com/wilsonfreitas/python-bcb), a aplicação oferece 6 módulos temáticos com gráficos interativos, tabelas estilizadas e download em CSV/XLSX.

> **Idiomas:** Português 🇧🇷 | English 🇺🇸 — alternável em tempo real.

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/laboratorio-dados-publicos.git
cd laboratorio-dados-publicos

# Crie um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute
streamlit run app.py
```

### Requisitos

- Python 3.9+
- Conexão com a internet (acesso às APIs do BCB)

### Dependências

| Pacote | Versão | Uso |
|--------|--------|-----|
| `streamlit` | ≥ 1.32.0 | Framework web |
| `python-bcb` | ≥ 0.2.2 | Acesso às APIs do BCB (SGS, OData, IF.Data) |
| `plotly` | ≥ 5.18.0 | Gráficos interativos |
| `pandas` | ≥ 2.0.0 | Manipulação de dados |
| `openpyxl` | ≥ 3.1.0 | Exportação para Excel |

---

## 📦 Módulos

### ⚡ SPI — Sistema de Pagamentos Instantâneos (Pix)

Consulta o endpoint **PixLiquidadosAtual** para dados de transações Pix.

- **KPIs:** dias no período, quantidade, volume (R$), ticket médio
- **Gráficos:** área (quantidade e volume ao longo do tempo)
- **Comparação:** período selecionado vs período anterior (Δ%)
- **Estatísticas descritivas** e tabela de dados
- **Download:** CSV / XLSX

### 📈 SGS — Sistema Gerenciador de Séries Temporais

Acesso a milhares de indicadores econômicos do SGS.

- **3 modos de entrada:** busca por nome, digitação de códigos, catálogo de séries populares (7 categorias, ~20 séries)
- **Gráfico combinado** com detecção automática de eixo Y duplo (algoritmo de clustering por escala logarítmica)
- **Gráficos individuais** por série
- **Correlação:** heatmap de Pearson + scatter plots
- **Estatísticas** por série (obs, datas, missing, média, desvio, etc.)
- **Frequência:** original, mensal ou anual (resampling pós-consulta)
- **Download:** CSV / XLSX

### 🔮 Expectativas de Mercado

Projeções do mercado via **ExpectativasMercadoAnuais**.

- **10 indicadores:** Câmbio, Dívida, IGP-M, Investimento, IPCA, PIB, Resultado Nominal, Resultado Primário, Selic, Taxa de Desocupação
- **Gráfico de barras** (média) por indicador
- **Tabela estilizada:** ano, média, mediana, desvio padrão, mínimo, máximo
- **Contagem de respondentes** por indicador

### 🏦 IF.Data — Dados de Instituições Financeiras

Dados contábeis e regulatórios de IFs supervisionadas (Segmentos 1–4).

- **Ranking:** Top/Bottom 10 por variável (Ativo Total, Captações, PL, Lucro Líquido, Índice de Basileia, Op. Crédito, Perda Esperada)
- **Banco Individual:** visão consolidada com posição no ranking
- **Filtros de materialidade:** PL > 100 mi · Op. Crédito > 200 mi · Ativo > 1 bi
- **Download:** dados brutos por trimestre (limite 24 meses)

### 💹 Taxas de Juros de Operações de Crédito

Taxas praticadas por IFs em diversas modalidades.

- **Ranking:** Top/Bottom 10 por modalidade (12 diárias + 2 mensais)
- **Banco Individual:** posição em cada modalidade
- **Gráficos:** mediana da taxa ao longo do tempo (scatter, últimos 10 anos)
- **Download ilimitado** com barra de progresso

### 📍 Inadimplência de Operações de Crédito

Inadimplência por região e estado — Pessoa Física e Jurídica.

- **Mapa do Brasil:** choropleth com cores por região e shading por inadimplência dentro de cada região (estados com maior NPL = tom mais escuro)
- **Hover:** PF/PJ do estado + PF/PJ da região
- **Clique no estado:** gráficos comparativos (estado vs região, 48 meses)
- **Gráficos regionais:** 2 line charts (PF e PJ), 5 regiões, 48 meses
- **Download:** dados por região ou estado, período livre

---

## 🏗️ Arquitetura

```
laboratorio_dados_publicos/
├── app.py                          # Hub central + router
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Tema dark
├── pages/
│   ├── modulo_spi.py               # ⚡ Pix
│   ├── modulo_sgs.py               # 📈 Séries Temporais
│   ├── modulo_exp.py               # 🔮 Expectativas
│   ├── modulo_ifdata.py            # 🏦 IF.Data
│   ├── modulo_taxas.py             # 💹 Taxas de Juros
│   ├── modulo_inad.py              # 📍 Inadimplência
│   └── modulo_feedback.py          # 💬 Sugestões
└── utils/
    ├── i18n.py                     # Traduções PT/EN (~300 chaves)
    ├── styles.py                   # CSS customizado (dark theme)
    └── helpers.py                  # Funções auxiliares (download, cards)
```

### Padrões de design

- **Navegação por session_state:** hub → módulo → hub (sem sidebar, sem multipage nativo)
- **Cache agressivo:** `@st.cache_data(ttl=3600)` em todas as chamadas à API
- **Dark theme** com paleta consistente (cyan, emerald, amber, rose, violet)
- **Gráficos Plotly** com layout compartilhado (`PLOTLY_LAYOUT_BASE`) e grid sutil
- **Downloads padronizados:** CSV (UTF-8 BOM, separador `;`) e XLSX

---

## ⚙️ Configuração Opcional

### Notificações por Push (Pushover)

O módulo de Feedback envia notificações via [Pushover](https://pushover.net/). Para ativar, crie o arquivo `.streamlit/secrets.toml`:

```toml
PUSHOVER_API_TOKEN = "sua_api_token"
PUSHOVER_USER_KEY = "sua_user_key"
```

Sem essas chaves, o feedback é registrado normalmente mas sem notificação push.

---

## 📊 APIs Utilizadas

| API | Endpoint | Módulo |
|-----|----------|--------|
| SPI | `PixLiquidadosAtual` | SPI |
| SGS | `sgs.dataframe()` | SGS |
| SGS Regional | `get_non_performing_loans()` | Inadimplência |
| Expectativas | `ExpectativasMercadoAnuais` | Expectativas |
| IF.Data | `IfDataCadastro`, `IfDataValores` | IF.Data |
| Taxas | `TaxasJurosMensalPorMes`, `TaxasJurosDiariaPorInicioPeriodo` | Taxas |

Todas as APIs são públicas e não requerem autenticação. Documentação: [dadosabertos.bcb.gov.br](https://dadosabertos.bcb.gov.br/)

---

## 🤝 Contribuições

Sugestões, bug reports e pull requests são bem-vindos. Use o módulo de Feedback dentro do app ou abra uma issue neste repositório.

---

## 📝 Licença

MIT

---

## 👨‍🏫 Autor

**José Américo** — Professor, COPPEAD/UFRJ Business School
