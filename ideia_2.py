# 2. Análise de Eficiência e Fluxo de Trabalho
# Esta análise busca entender se a experiência leva a um processo de integração mais suave e rápido.
# Métricas a extrair:
# Tempo para o merge (Time to Merge): Calcule a diferença entre merged_at e created_at para cada PR. PRs de desenvolvedores da Faixa A são mesclados mais rapidamente?
# Taxa de sucesso da Integração Contínua (CI): Analise o campo ci_status_on_head. Calcule a porcentagem de PRs que tinham um status "success" na primeira vez em que foram submetidos. Desenvolvedores experientes quebram a build com menos frequência?
# Padrões de trabalho: Analise a distribuição de created_at por hora do dia e dia da semana. Existem diferenças nos padrões de trabalho entre as faixas? (Esta é uma análise mais exploratória).
# Visualizações sugeridas:
# Gráficos de barras com a média do "tempo para o merge" para cada faixa, com barras de erro para indicar a variância.
# Um gráfico de pizza ou barras empilhadas mostrando a proporção de status de CI (success, failure, pending) por faixa de desenvolvedor.