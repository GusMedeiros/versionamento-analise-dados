# 1. Análise de Tamanho e Complexidade dos Pull Requests
# A hipótese aqui é que desenvolvedores mais experientes (Faixa A) podem submeter PRs mais atômicos e focados, enquanto os novatos (Faixa E) podem submeter mudanças maiores e menos coesas.
# Métricas a extrair:
# Linhas de código por PR: Calcule a soma de additions e deletions para cada PR. Compare a média e a mediana entre as faixas.
# Número de arquivos por PR: Use counts.files. Desenvolvedores experientes tendem a modificar menos arquivos em um único PR para manter o escopo limitado?
# Distribuição do "churn": Analise a proporção entre additions e deletions. Um PR que só adiciona código (um novo recurso) é diferente de um que refatora (muitas adições e deleções)? Essa proporção muda com a experiência?
# Visualizações sugeridas:
# Box plots comparando o número de linhas de código e o número de arquivos por PR para cada faixa de desenvolvedor (A a E). Isso mostrará não apenas a média, mas também a dispersão e os outliers.