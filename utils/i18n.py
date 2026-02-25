"""
Módulo de internacionalização (i18n) para o Laboratório de Dados Públicos.
Suporta Português (pt) e Inglês (en).
"""

TRANSLATIONS = {
    "pt": {
        # ===== Hub =====
        "app_title": "Laboratório de Dados Públicos",
        "app_subtitle": "Portal de Dados Abertos do Banco Central do Brasil",
        "app_description": (
            "Explore, visualize e exporte dados do Portal de Dados Abertos do Banco Central do Brasil. "
            "Consulte APIs oficiais e gere relatórios personalizados em poucos cliques."
        ),
        "badge_api": "API DADOS ABERTOS BCB",
        "select_module": "Selecione um módulo para começar:",
        "active": "ATIVO",
        "coming_soon": "EM BREVE",
        "source": "Fonte",
        "built_with": "Desenvolvido com python-bcb & Streamlit",
        "author": "Autor: José Américo Antunes - BCB/Coppead/FGV/UCAM", 
        "language": "Idioma",

        # ===== Module names & descriptions =====
        "spi_title": "⚡ SPI — Pix",
        "spi_desc": (
            "Estatísticas diárias do Sistema de Pagamentos Instantâneos: "
            "quantidade, volume e média das transações Pix."
        ),
        "sgs_title": "📈 SGS — Séries Temporais",
        "sgs_desc": (
            "Acesse o Sistema Gerenciador de Séries Temporais "
            "com milhares de indicadores econômicos."
        ),
        "exp_title": "🔮 Expectativas",
        "exp_desc": (
            "Projeções do mercado para indicadores como "
            "IPCA, Selic, PIB e câmbio via Focus."
        ),
        "ifdata_title": "🏦 IF.Data",
        "ifdata_desc": (
            "Dados contábeis e financeiros de instituições financeiras "
            "supervisionadas pelo BCB."
        ),
        "taxas_title": "💹 Taxas de Juros",
        "taxas_desc": (
            "Taxas de juros praticadas por instituições financeiras "
            "em diversas modalidades de crédito."
        ),

        # ===== SPI Module =====
        "spi_page_title": "⚡ SPI — Sistema de Pagamentos Instantâneos",
        "spi_page_desc": (
            "Consulte estatísticas diárias de transações Pix liquidadas"
        ),
        "back_to_hub": "← Voltar ao Hub",
        "start_date": "Data inicial",
        "end_date": "Data final (opcional)",
        "query_api": "🔍 Consultar API",
        "loading": "Consultando API do Banco Central...",
        "api_error": "❌ Erro ao consultar a API",
        "api_error_detail": (
            "Não foi possível conectar à API do Banco Central. "
            "Verifique sua conexão com a internet e tente novamente."
        ),
        "no_data": "Nenhum dado encontrado para o período selecionado.",

        # KPIs
        "kpi_days": "Total de Dias",
        "kpi_days_sub": "dias com dados",
        "kpi_qty": "Qtd. Total Transações",
        "kpi_qty_sub": "acumulado no período",
        "kpi_volume": "Volume Total (R$)",
        "kpi_volume_sub": "acumulado no período",
        "kpi_avg": "Média Diária (R$)",
        "kpi_avg_sub": "média do período",

        # Charts
        "chart_qty_title": "📊 Quantidade Diária de Transações",
        "chart_vol_title": "💰 Volume Total Diário (R$)",
        "chart_date": "Data",
        "chart_quantity": "Quantidade",
        "chart_total": "Total (R$)",

        # Comparison
        "comparison_title": "⚖️ Comparação entre Períodos",
        "period_a": "Período A",
        "period_b": "Período B",
        "comp_avg_qty": "Média Qtd. Diária",
        "comp_avg_vol": "Volume Médio Diário",
        "comp_avg_ticket": "Ticket Médio",
        "variation": "Variação",
        "no_data_period": "Sem dados para este período.",
        "compare_btn": "Comparar",

        # Stats
        "stats_title": "📋 Estatísticas Descritivas",
        "stat_metric": "Métrica",
        "stat_qty": "Quantidade",
        "stat_total": "Total (R$)",
        "stat_avg": "Média (R$)",
        "stat_mean": "Média",
        "stat_median": "Mediana",
        "stat_std": "Desvio Padrão",
        "stat_min": "Mínimo",
        "stat_max": "Máximo",
        "stat_q1": "Q1 (25%)",
        "stat_q3": "Q3 (75%)",

        # Data table
        "data_title": "🗂️ Dados Extraídos",
        "data_showing": "Exibindo {n} registros",
        "download_csv": "📥 Baixar CSV",
        "download_xlsx": "📥 Baixar XLSX",
        "col_date": "Data",
        "col_quantity": "Quantidade",
        "col_total": "Total (R$)",
        "col_average": "Média (R$)",

        # ===== SGS Module =====
        "sgs_page_title": "📈 SGS — Sistema Gerenciador de Séries Temporais",
        "sgs_page_desc": (
            "Consulte séries temporais do Banco Central · "
            "Milhares de dados econômicos disponíveis"
        ),
        "sgs_input_mode": "Modo de entrada",
        "sgs_mode_search": "🔍 Buscar por nome",
        "sgs_mode_codes": "⌨️ Digitar códigos",
        "sgs_mode_popular": "⭐ Séries populares",
        "sgs_search_placeholder": "Digite o nome da série (ex: IPCA, Selic, Câmbio...)",
        "sgs_codes_placeholder": "Digite os códigos separados por vírgula (ex: 192, 433, 11)",
        "sgs_codes_help": "Insira os códigos numéricos das séries do SGS separados por vírgula.",
        "sgs_popular_title": "⭐ Séries Populares",
        "sgs_popular_desc": "Clique para adicionar séries à sua consulta:",
        "sgs_selected_series": "📋 Séries selecionadas",
        "sgs_no_series": "Nenhuma série selecionada. Use as opções acima para adicionar séries.",
        "sgs_code": "Código",
        "sgs_name_label": "Nome (opcional)",
        "sgs_name_placeholder": "Ex: IPCA",
        "sgs_remove": "Remover",
        "sgs_clear_all": "🗑️ Limpar tudo",
        "sgs_add": "Adicionar",
        "sgs_frequency": "Frequência",
        "sgs_freq_original": "Original",
        "sgs_freq_daily": "Diária",
        "sgs_freq_monthly": "Mensal",
        "sgs_freq_annual": "Anual",
        "sgs_warn_periodicity": (
            "⚠️ **Atenção:** O ideal é que as séries consultadas tenham a "
            "mesma periodicidade. Séries com frequências diferentes podem gerar "
            "valores ausentes (NaN) ao serem combinadas."
        ),
        "sgs_warn_10y": (
            "⚠️ **Atenção:** A API permite coletar no máximo 10 anos "
            "de dados para séries diárias. Considere reduzir o intervalo."
        ),
        "sgs_warn_max_chart": (
            "ℹ️ Apenas as **3 primeiras séries** serão exibidas nos gráficos. "
            "Todas as séries estarão disponíveis na tabela de dados e para download."
        ),
        "sgs_chart_title": "📊 Séries Temporais",
        "sgs_chart_individual": "📊 Gráficos Individuais",
        "sgs_chart_combined": "📊 Gráfico Combinado",
        "sgs_primary_axis": "Eixo Y Primário",
        "sgs_secondary_axis": "Eixo Y Secundário",
        "sgs_correlation_title": "🔗 Análise de Correlação",
        "sgs_heatmap_title": "Matriz de Correlação (Pearson)",
        "sgs_scatter_title": "Dispersão entre Séries",
        "sgs_scatter_select_x": "Eixo X",
        "sgs_scatter_select_y": "Eixo Y",
        "sgs_stats_per_series": "📋 Estatísticas por Série",
        "sgs_observations": "Observações",
        "sgs_first_date": "Primeira data",
        "sgs_last_date": "Última data",
        "sgs_missing": "Valores ausentes",
        "sgs_search_results": "Resultados da busca:",
        "sgs_no_results": "Nenhuma série encontrada para esta busca.",
        "sgs_cat_inflation": "📊 Inflação",
        "sgs_cat_interest": "💰 Juros",
        "sgs_cat_exchange": "💱 Câmbio",
        "sgs_cat_activity": "🏭 Atividade Econômica",
        "sgs_cat_credit": "🏦 Crédito",
        "sgs_cat_fiscal": "📋 Fiscal",
        "sgs_cat_external": "🌍 Setor Externo",

        # ===== Expectativas Module =====
        "exp_page_title": "🔮 Expectativas de Mercado",
        "exp_page_desc": (
            "Projeções do mercado para os próximos anos"
        ),
        "exp_select_vars": "Selecione os indicadores:",
        "exp_query": "🔍 Consultar Expectativas",
        "exp_survey_date": "Data da pesquisa",
        "exp_ref_years": "Anos de referência",
        "exp_col_ref": "Data Referência",
        "exp_col_mean": "Média",
        "exp_col_median": "Mediana",
        "exp_col_std": "Desvio Padrão",
        "exp_col_min": "Mínimo",
        "exp_col_max": "Máximo",
        "exp_chart_title": "Expectativas: {var}",
        "exp_no_data_var": "Sem dados para {var}.",
        "exp_respondents": "respondentes",

        # ===== IF.Data Module =====
        "ifd_page_title": "🏦 IF.Data — Dados de Instituições Financeiras",
        "ifd_page_desc": (
            "Dados contábeis e regulatórios de IFs supervisionadas pelo BCB · Segmentos 1 a 4"
            "<br>Filtros de Materialidade: PL > 100 mi · Op. Crédito > 200 mi · Ativo Total > 1 bi"
        ),
        "ifd_tab_ranking": "🏆 Ranking",
        "ifd_tab_bank": "🔍 Banco Individual",
        "ifd_tab_download": "📥 Download de Dados",
        "ifd_select_vars": "Selecione as variáveis:",
        "ifd_query": "🔍 Consultar IF.Data",
        "ifd_period": "Período",
        "ifd_period_auto": "Data mais recente disponível",
        "ifd_largest": "Maiores",
        "ifd_smallest": "Menores",
        "ifd_largest_pec": "Menores",
        "ifd_smallest_pec": "Maiores",
        "ifd_rank_col": "#",
        "ifd_institution": "Instituição",
        "ifd_value": "Valor",
        "ifd_select_bank": "Selecione a instituição:",
        "ifd_bank_overview": "Visão Geral",
        "ifd_variable": "Variável",
        "ifd_position": "Posição",
        "ifd_of_ifs": "de {n} IFs",
        "ifd_download_title": "📥 Download — Suporte à Pesquisa",
        "ifd_download_desc": (
            "Baixe dados de todas as IFs para um intervalo de datas. "
            "Limite: 24 meses (8 trimestres). Dados trimestrais."
        ),
        "ifd_download_start": "Trimestre inicial (AAAAMM)",
        "ifd_download_end": "Trimestre final (AAAAMM)",
        "ifd_download_btn": "📥 Baixar Dados",
        "ifd_downloading": "Baixando dados do IF.Data...",
        "ifd_download_warn_24m": "⚠️ O intervalo máximo é de 24 meses.",
        "ifd_total_ifs": "Total de IFs",
        "ifd_ref_date": "Data-base",

        # ===== Taxas de Juros Module =====
        "tax_page_title": "💹 Taxas de Juros de Operações de Crédito",
        "tax_page_desc": "Taxas praticadas por IFs em diversas modalidades de crédito",
        "tax_tab_ranking": "🏆 Ranking",
        "tax_tab_bank": "🔍 Banco Individual",
        "tax_tab_charts": "📊 Gráficos",
        "tax_tab_download": "📥 Download",
        "tax_select_modalities": "Selecione as modalidades:",
        "tax_query": "🔍 Consultar Taxas",
        "tax_largest": "Maiores Taxas",
        "tax_smallest": "Menores Taxas",
        "tax_institution": "Instituição",
        "tax_rate": "Taxa (% a.a.)",
        "tax_select_bank": "Selecione a instituição:",
        "tax_modality": "Modalidade",
        "tax_position": "Posição",
        "tax_of_banks": "de {n} bancos",
        "tax_select_chart_mod": "Selecione a modalidade para o gráfico:",
        "tax_chart_title": "{mod} — Taxa a.a. por IF",
        "tax_chart_yaxis": "Taxa (% a.a.)",
        "tax_chart_xaxis": "Data",
        "tax_download_title": "📥 Download — Suporte à Pesquisa",
        "tax_download_desc": "Baixe dados de taxas de juros para todas as IFs em um intervalo de datas.",
        "tax_download_btn": "📥 Baixar Dados",
        "tax_downloading": "Baixando dados de taxas...",
        "tax_ref_date": "Data de referência",
        "tax_total_banks": "Total de bancos",
        "tax_cat_daily": "📅 Modalidades Diárias",
        "tax_cat_monthly": "📅 Modalidades Mensais",

        # ===== Inadimplência Module =====
        "inad_page_title": "📍 Inadimplência de Operações de Crédito",
        "inad_page_desc": "Inadimplência por região e estado — Pessoa Física e Jurídica",
        "inad_tab_map": "🗺️ Inadimplência Brasil",
        "inad_tab_download": "📥 Download",
        "inad_query": "🔍 Consultar Dados",
        "inad_map_title": "Mapa de Inadimplência por Região",
        "inad_click_state": "Clique em um estado para ver detalhes",
        "inad_pf": "Pessoa Física",
        "inad_pj": "Pessoa Jurídica",
        "inad_region": "Região",
        "inad_state": "Estado",
        "inad_region_pf": "Inadimplência PF por Região (% — últimos 48 meses)",
        "inad_region_pj": "Inadimplência PJ por Região (% — últimos 48 meses)",
        "inad_state_detail": "Detalhe: {uf}",
        "inad_state_vs_region": "{uf} vs Região {reg}",
        "inad_download_title": "📥 Download — Suporte à Pesquisa",
        "inad_download_desc": "Baixe dados de inadimplência por região ou estado.",
        "inad_download_btn": "📥 Baixar Dados",
        "inad_downloading": "Baixando dados de inadimplência...",
        "inad_scope": "Escopo",
        "inad_scope_regions": "Regiões",
        "inad_scope_states": "Estados",
        "inad_last_value": "Último valor",
    },

    "en": {
        # ===== Hub =====
        "app_title": "Public Data Lab",
        "app_subtitle": "Open Data Portal - Central Bank of Brazil",
        "app_description": (
            "Explore, visualize and export data from the Central Bank of Brazil. "
            "Query official APIs and generate custom reports in a few clicks."
        ),
        "badge_api": "BCB OPEN DATA API",
        "select_module": "Select a module to get started:",
        "active": "ACTIVE",
        "coming_soon": "COMING SOON",
        "source": "Source",
        "built_with": "Built with python-bcb & Streamlit",
        "author": "Author: José Américo Antunes - BCB/Coppead/FGV/UCAM", 
        "language": "Language",

        # ===== Module names & descriptions =====
        "spi_title": "⚡ SPI — Pix",
        "spi_desc": (
            "Daily statistics of the Instant Payment System: "
            "transaction count, volume and average of Pix transfers."
        ),
        "sgs_title": "📈 SGS — Time Series",
        "sgs_desc": (
            "Access the Time Series Management System "
            "with thousands of economic indicators."
        ),
        "exp_title": "🔮 Expectations",
        "exp_desc": (
            "Market projections for indicators such as "
            "CPI, Selic rate, GDP and exchange rate via Focus."
        ),
        "ifdata_title": "🏦 IF.Data",
        "ifdata_desc": (
            "Accounting and financial data of financial institutions "
            "supervised by the BCB."
        ),
        "taxas_title": "💹 Interest Rates",
        "taxas_desc": (
            "Interest rates charged by financial institutions "
            "across various credit modalities."
        ),

        # ===== SPI Module =====
        "spi_page_title": "⚡ SPI — Instant Payment System",
        "spi_page_desc": (
            "Query daily statistics of settled Pix transactions"
        ),
        "back_to_hub": "← Back to Hub",
        "start_date": "Start date",
        "end_date": "End date (optional)",
        "query_api": "🔍 Query API",
        "loading": "Querying Central Bank API...",
        "api_error": "❌ API Error",
        "api_error_detail": (
            "Could not connect to the Central Bank API. "
            "Please check your internet connection and try again."
        ),
        "no_data": "No data found for the selected period.",

        # KPIs
        "kpi_days": "Total Days",
        "kpi_days_sub": "days with data",
        "kpi_qty": "Total Transactions",
        "kpi_qty_sub": "accumulated in period",
        "kpi_volume": "Total Volume (R$)",
        "kpi_volume_sub": "accumulated in period",
        "kpi_avg": "Daily Average (R$)",
        "kpi_avg_sub": "period average",

        # Charts
        "chart_qty_title": "📊 Daily Transaction Count",
        "chart_vol_title": "💰 Daily Total Volume (R$)",
        "chart_date": "Date",
        "chart_quantity": "Quantity",
        "chart_total": "Total (R$)",

        # Comparison
        "comparison_title": "⚖️ Period Comparison",
        "period_a": "Period A",
        "period_b": "Period B",
        "comp_avg_qty": "Avg. Daily Count",
        "comp_avg_vol": "Avg. Daily Volume",
        "comp_avg_ticket": "Avg. Ticket",
        "variation": "Change",
        "no_data_period": "No data for this period.",
        "compare_btn": "Compare",

        # Stats
        "stats_title": "📋 Descriptive Statistics",
        "stat_metric": "Metric",
        "stat_qty": "Quantity",
        "stat_total": "Total (R$)",
        "stat_avg": "Average (R$)",
        "stat_mean": "Mean",
        "stat_median": "Median",
        "stat_std": "Std. Deviation",
        "stat_min": "Minimum",
        "stat_max": "Maximum",
        "stat_q1": "Q1 (25%)",
        "stat_q3": "Q3 (75%)",

        # Data table
        "data_title": "🗂️ Extracted Data",
        "data_showing": "Showing {n} records",
        "download_csv": "📥 Download CSV",
        "download_xlsx": "📥 Download XLSX",
        "col_date": "Date",
        "col_quantity": "Quantity",
        "col_total": "Total (R$)",
        "col_average": "Average (R$)",

        # ===== SGS Module =====
        "sgs_page_title": "📈 SGS — Time Series Management System",
        "sgs_page_desc": (
            "Query time series from the Central Bank · "
            "Thousands of economic data available"
        ),
        "sgs_input_mode": "Input mode",
        "sgs_mode_search": "🔍 Search by name",
        "sgs_mode_codes": "⌨️ Enter codes",
        "sgs_mode_popular": "⭐ Popular series",
        "sgs_search_placeholder": "Type series name (e.g., CPI, Selic, Exchange rate...)",
        "sgs_codes_placeholder": "Enter codes separated by commas (e.g., 192, 433, 11)",
        "sgs_codes_help": "Enter SGS series numeric codes separated by commas.",
        "sgs_popular_title": "⭐ Popular Series",
        "sgs_popular_desc": "Click to add series to your query:",
        "sgs_selected_series": "📋 Selected Series",
        "sgs_no_series": "No series selected. Use the options above to add series.",
        "sgs_code": "Code",
        "sgs_name_label": "Name (optional)",
        "sgs_name_placeholder": "E.g., CPI",
        "sgs_remove": "Remove",
        "sgs_clear_all": "🗑️ Clear all",
        "sgs_add": "Add",
        "sgs_frequency": "Frequency",
        "sgs_freq_original": "Original",
        "sgs_freq_daily": "Daily",
        "sgs_freq_monthly": "Monthly",
        "sgs_freq_annual": "Annual",
        "sgs_warn_periodicity": (
            "⚠️ **Note:** It is recommended that queried series share the same "
            "periodicity. Series with different frequencies may generate "
            "missing values (NaN) when combined."
        ),
        "sgs_warn_10y": (
            "⚠️ **Note:** The API allows a maximum of 10 years "
            "of data for daily series. Consider reducing the date range."
        ),
        "sgs_warn_max_chart": (
            "ℹ️ Only the **first 3 series** will be displayed in charts. "
            "All series will be available in the data table and for download."
        ),
        "sgs_chart_title": "📊 Time Series",
        "sgs_chart_individual": "📊 Individual Charts",
        "sgs_chart_combined": "📊 Combined Chart",
        "sgs_primary_axis": "Primary Y-Axis",
        "sgs_secondary_axis": "Secondary Y-Axis",
        "sgs_correlation_title": "🔗 Correlation Analysis",
        "sgs_heatmap_title": "Correlation Matrix (Pearson)",
        "sgs_scatter_title": "Series Scatter Plot",
        "sgs_scatter_select_x": "X-Axis",
        "sgs_scatter_select_y": "Y-Axis",
        "sgs_stats_per_series": "📋 Statistics per Series",
        "sgs_observations": "Observations",
        "sgs_first_date": "First date",
        "sgs_last_date": "Last date",
        "sgs_missing": "Missing values",
        "sgs_search_results": "Search results:",
        "sgs_no_results": "No series found for this search.",
        "sgs_cat_inflation": "📊 Inflation",
        "sgs_cat_interest": "💰 Interest Rates",
        "sgs_cat_exchange": "💱 Exchange Rate",
        "sgs_cat_activity": "🏭 Economic Activity",
        "sgs_cat_credit": "🏦 Credit",
        "sgs_cat_fiscal": "📋 Fiscal",
        "sgs_cat_external": "🌍 External Sector",

        # ===== Expectations Module =====
        "exp_page_title": "🔮 Market Expectations",
        "exp_page_desc": (
            "Market projections for the coming years"
        ),
        "exp_select_vars": "Select indicators:",
        "exp_query": "🔍 Query Expectations",
        "exp_survey_date": "Survey date",
        "exp_ref_years": "Reference years",
        "exp_col_ref": "Reference Year",
        "exp_col_mean": "Mean",
        "exp_col_median": "Median",
        "exp_col_std": "Std. Deviation",
        "exp_col_min": "Minimum",
        "exp_col_max": "Maximum",
        "exp_chart_title": "Expectations: {var}",
        "exp_no_data_var": "No data for {var}.",
        "exp_respondents": "respondents",

        # ===== IF.Data Module =====
        "ifd_page_title": "🏦 IF.Data — Financial Institutions Data",
        "ifd_page_desc": (
            "Accounting and regulatory data of FIs supervised by BCB · Segments 1 to 4"
            "<br>Materiality Filters: Equity > 100 mi · Credit Portfolio > 200 mi · Total Assets > 1 bi"
        ),              
        "ifd_tab_ranking": "🏆 Ranking",
        "ifd_tab_bank": "🔍 Individual Bank",
        "ifd_tab_download": "📥 Data Download",
        "ifd_select_vars": "Select variables:",
        "ifd_query": "🔍 Query IF.Data",
        "ifd_period": "Period",
        "ifd_period_auto": "Latest available date",
        "ifd_largest": "Largest",
        "ifd_smallest": "Smallest",
        "ifd_largest_pec": "Smallest",
        "ifd_smallest_pec": "Largest",
        "ifd_rank_col": "#",
        "ifd_institution": "Institution",
        "ifd_value": "Value",
        "ifd_select_bank": "Select institution:",
        "ifd_bank_overview": "Overview",
        "ifd_variable": "Variable",
        "ifd_position": "Position",
        "ifd_of_ifs": "of {n} FIs",
        "ifd_download_title": "📥 Download — Research Support",
        "ifd_download_desc": (
            "Download data for all FIs within a date range. "
            "Limit: 24 months (8 quarters). Quarterly data."
        ),
        "ifd_download_start": "Start quarter (YYYYMM)",
        "ifd_download_end": "End quarter (YYYYMM)",
        "ifd_download_btn": "📥 Download Data",
        "ifd_downloading": "Downloading IF.Data...",
        "ifd_download_warn_24m": "⚠️ Maximum range is 24 months.",
        "ifd_total_ifs": "Total FIs",
        "ifd_ref_date": "Reference date",

        # ===== Interest Rates Module =====
        "tax_page_title": "💹 Credit Interest Rates",
        "tax_page_desc": "Interest rates charged by FIs across credit modalities",
        "tax_tab_ranking": "🏆 Ranking",
        "tax_tab_bank": "🔍 Individual Bank",
        "tax_tab_charts": "📊 Charts",
        "tax_tab_download": "📥 Download",
        "tax_select_modalities": "Select modalities:",
        "tax_query": "🔍 Query Rates",
        "tax_largest": "Highest Rates",
        "tax_smallest": "Lowest Rates",
        "tax_institution": "Institution",
        "tax_rate": "Rate (% p.a.)",
        "tax_select_bank": "Select institution:",
        "tax_modality": "Modality",
        "tax_position": "Position",
        "tax_of_banks": "of {n} banks",
        "tax_select_chart_mod": "Select modality for chart:",
        "tax_chart_title": "{mod} — Rate p.a. per FI",
        "tax_chart_yaxis": "Rate (% p.a.)",
        "tax_chart_xaxis": "Date",
        "tax_download_title": "📥 Download — Research Support",
        "tax_download_desc": "Download interest rate data for all FIs within a date range.",
        "tax_download_btn": "📥 Download Data",
        "tax_downloading": "Downloading rate data...",
        "tax_ref_date": "Reference date",
        "tax_total_banks": "Total banks",
        "tax_cat_daily": "📅 Daily Modalities",
        "tax_cat_monthly": "📅 Monthly Modalities",

        # ===== Non-Performing Loans Module =====
        "inad_page_title": "📍 Credit Non-Performing Loans",
        "inad_page_desc": "Non-performing loans by region and state — Households and Enterprises",
        "inad_tab_map": "🗺️ Brazil NPL Map",
        "inad_tab_download": "📥 Download",
        "inad_query": "🔍 Query Data",
        "inad_map_title": "Non-Performing Loans Map by Region",
        "inad_click_state": "Click a state to see details",
        "inad_pf": "Individuals",
        "inad_pj": "Corporates",
        "inad_region": "Region",
        "inad_state": "State",
        "inad_region_pf": "NPL Individuals by Region (% — last 48 months)",
        "inad_region_pj": "NPL Corporates by Region (% — last 48 months)",
        "inad_state_detail": "Detail: {uf}",
        "inad_state_vs_region": "{uf} vs Region {reg}",
        "inad_download_title": "📥 Download — Research Support",
        "inad_download_desc": "Download non-performing loan data by region or state.",
        "inad_download_btn": "📥 Download Data",
        "inad_downloading": "Downloading NPL data...",
        "inad_scope": "Scope",
        "inad_scope_regions": "Regions",
        "inad_scope_states": "States",
        "inad_last_value": "Latest value",
    },
}


def t(key: str, lang: str = "pt", **kwargs) -> str:
    """Retorna a tradução para a chave informada."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["pt"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
