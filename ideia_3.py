# 3. Análise de Qualidade e Revisão de Código
# Aqui, a ideia é usar as interações no PR como um proxy para a qualidade do código inicial. Menos comentários de revisão podem indicar uma qualidade inicial maior.
# Métricas a extrair:
# Quantidade de feedback: Compare counts.reviews e counts.review_comments entre as faixas. Desenvolvedores da Faixa E recebem mais comentários?
# Densidade de comentários: Normalize o número de comentários pelo tamanho do PR (ex: review_comments / (additions + deletions)). Isso controla o fato de que PRs maiores naturalmente recebem mais comentários.
# Ciclos de revisão (Rework): Conte o número de commits feitos após o primeiro comentário de revisão. Isso pode indicar quanto trabalho de correção foi necessário. Você pode identificar isso analisando as timestamps em commits e review_comments.
# Tipo de feedback: Analise reviews[].state. Calcule a proporção de reviews "APPROVED" vs. "CHANGES_REQUESTED" para cada faixa.
# Visualizações sugeridas:
# Scatter plot (gráfico de dispersão) mostrando a relação entre o tamanho do PR e o número de comentários de revisão, com cores diferentes para cada faixa de desenvolvedor.
# Gráfico de barras comparando a densidade média de comentários por faixa.