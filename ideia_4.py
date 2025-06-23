# 4. Análise de Comunicação e Colaboração
# Como a forma de comunicação dentro de um PR muda com a experiência?
# Métricas a extrair:
# Tamanho do texto: Meça o comprimento (número de caracteres ou palavras) do title do PR e dos body dos comentários (reviews, review_comments, issue_comments). Desenvolvedores experientes são mais concisos ou mais detalhados?
# Análise de sentimento (avançado): Se tiver as ferramentas, pode rodar uma análise de sentimento nos textos dos comentários. A comunicação se torna mais neutra/positiva com a experiência?
# Responsividade: Analise o tempo entre um comentário de revisão (review_comments[].created_at) e um novo commit ou um comentário de resposta pelo autor do PR.
# Visualizações sugeridas:
# Box plots para o comprimento dos títulos e descrições dos PRs por faixa.