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
import pandas as pd
from datetime import datetime
import os
import json

def carregar_dados_de_pull_requests(diretorio_base):
    """
    Percorre a estrutura de pastas especificada, carrega os JSONs dos PRs
    e enriquece os dados com informações do repositório e autor extraídas do caminho.
    """
    lista_de_prs = []
    print(f"Iniciando varredura em: {diretorio_base}")

    # os.walk é ideal para navegar na árvore de diretórios
    for root, dirs, files in os.walk(diretorio_base):
        # A pasta 'results' é o nosso alvo
        if root.endswith('/results') or root.endswith('\\results'):
            for nome_arquivo in files:
                if nome_arquivo.endswith('.json'):
                    caminho_completo = os.path.join(root, nome_arquivo)
                    try:
                        # Extrai metadados do caminho do arquivo
                        # Ex: .../repo-legal/developer/dev-joao/results/123.json
                        partes_caminho = caminho_completo.replace('\\', '/').split('/')
                        
                        # Ajuste os índices negativos se a profundidade do seu diretorio_base variar
                        repo_nome = partes_caminho[-5]
                        dev_nome = partes_caminho[-3]
                        
                        with open(caminho_completo, 'r', encoding='utf-8') as f:
                            pr_data = json.load(f)
                        
                        # Adiciona os metadados extraídos diretamente no dicionário do PR
                        # Isso garante que a informação não se perca
                        pr_data['repo'] = repo_nome
                        pr_data['author'] = dev_nome
                        
                        lista_de_prs.append(pr_data)

                    except (IOError, json.JSONDecodeError, IndexError) as e:
                        print(f"Erro ao processar o arquivo {caminho_completo}: {e}")
                        
    print(f"Carregamento concluído. Total de {len(lista_de_prs)} PRs encontrados.")
    return lista_de_prs

def analisar_qualidade_e_revisao(meus_dados_json):
    """
    Processa uma lista de PRs para extrair métricas de qualidade e revisão.
    """
    resultados = []
    
    for pr in meus_dados_json:
        if pr['faixa'] == 'Desconhecida' or not pr.get('counts'):
            continue
            
        # 1. Quantidade de feedback
        num_reviews = pr['counts'].get('reviews', 0)
        num_review_comments = pr['counts'].get('review_comments', 0)
        
        # 2. Densidade de comentários
        total_changes = sum(file.get('additions', 0) + file.get('deletions', 0) for file in pr.get('files', []))
        densidade_comentarios = 0
        if total_changes > 0:
            densidade_comentarios = num_review_comments / total_changes
            
        # 3. Ciclos de revisão (Rework)
        # Encontrar a data do primeiro comentário de revisão
        primeiro_comentario_dt = None
        if pr.get('review_comments'):
            datas_comentarios = [
                datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) 
                for c in pr['review_comments'] if c.get('created_at')
            ]
            if datas_comentarios:
                primeiro_comentario_dt = min(datas_comentarios)

        rework_commits = 0
        if primeiro_comentario_dt and pr.get('commits'):
            # Contar commits feitos APÓS o primeiro comentário
            for commit in pr['commits']:
                # O formato do timestamp do commit pode variar. Ajuste se necessário.
                # Assumindo que o JSON do commit tem um timestamp. Se não tiver, essa métrica não pode ser calculada.
                # Vamos supor que esteja em commit['commit']['author']['date'] ou similar.
                # Para este exemplo, vamos assumir que o seu JSON de commit tem um campo 'date'.
                if 'date' in commit: # Você precisará confirmar este campo no seu JSON
                    commit_dt = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                    if commit_dt > primeiro_comentario_dt:
                        rework_commits += 1

        # 4. Tipo de feedback
        num_approved = 0
        num_changes_requested = 0
        if pr.get('reviews'):
            for review in pr['reviews']:
                if review.get('state') == 'APPROVED':
                    num_approved += 1
                elif review.get('state') == 'CHANGES_REQUESTED':
                    num_changes_requested += 1
        
        total_reviews_com_estado = num_approved + num_changes_requested
        proporcao_changes_requested = 0
        if total_reviews_com_estado > 0:
            proporcao_changes_requested = num_changes_requested / total_reviews_com_estado

        resultados.append({
            'pr_number': pr['pr_number'],
            'autor': pr['author'],
            'faixa': pr['faixa'],
            'num_review_comments': num_review_comments,
            'tamanho_pr': total_changes,
            'densidade_comentarios': densidade_comentarios,
            'rework_commits': rework_commits,
            'proporcao_changes_requested': proporcao_changes_requested
        })
        
    return pd.DataFrame(resultados)

# Execute a análise nos seus dados
meus_dados_json = carregar_dados_de_pull_requests("repositories-mined")
# Supondo que seus dados já foram carregados na variável 'meus_dados_json'
# (Se você já converteu para DataFrame, use-o. Se não, esta é uma boa hora.)

if not meus_dados_json:
    print("Nenhum PR para analisar. Encerrando o script.")
    exit()

df_prs = pd.DataFrame(meus_dados_json)

# --- INÍCIO DO BLOCO DE CÓDIGO FALTANTE ---

# 1. Contar quantos PRs cada autor tem no nosso conjunto de dados
contagem_de_prs_por_autor = df_prs['author'].value_counts()

# 2. Definir uma função para atribuir a faixa baseada na contagem de PRs
def atribuir_faixa(contagem):
    if contagem == 1:
        return 'E'
    elif 2 <= contagem <= 10:  # Exemplo de regra para Faixa D - ajuste se necessário
        return 'D'
    elif 11 <= contagem <= 30: # Exemplo de regra para Faixa C - ajuste se necessário
        return 'C'
    elif 31 <= contagem <= 50: # Exemplo de regra para Faixa B - ajuste se necessário
        return 'B'
    elif contagem > 50:
        return 'A'
    return 'Desconhecida' # Para casos não previstos

# 3. Criar o mapa de autor para faixa
#    Isso cria um dicionário como {'nome_autor': 'Faixa A', 'outro_autor': 'Faixa C'}
dev_para_faixa = contagem_de_prs_por_autor.apply(atribuir_faixa).to_dict()

# 4. Adicionar a chave 'faixa' a cada PR na lista original 'meus_dados_json'
#    Este é o passo que corrige o erro 'KeyError'
for pr in meus_dados_json:
    autor = pr.get('author')
    if autor:
        pr['faixa'] = dev_para_faixa.get(autor, 'Desconhecida')
    else:
        pr['faixa'] = 'Desconhecida'

print("Enriquecimento concluído. A chave 'faixa' foi adicionada a cada PR.")
# Verificação rápida
# print("Exemplo de PR após enriquecimento:", meus_dados_json[0]['author'], meus_dados_json[0]['faixa'])

# --- FIM DO BLOCO DE CÓDIGO FALTANTE ---


# Agora você pode chamar a função de análise sem erro
# A variável 'meus_dados_json' agora se chama 'meus_dados_json' no seu código, use o nome correto
df_qualidade = analisar_qualidade_e_revisao(meus_dados_json) # ou analisar_qualidade_e_revisao(meus_dados_json)

# O resto do seu código...
print("\nMétricas médias de Qualidade e Revisão por Faixa de Experiência:")
# ...etc
df_qualidade = analisar_qualidade_e_revisao(meus_dados_json)
print("Amostra do DataFrame resultante:")
print(df_qualidade.head())

# Supondo que 'df_qualidade' já foi criado como no seu output
# E que 'media_por_faixa' também já foi calculado (se não, aqui está o código novamente)

# --- 1. AGREGAÇÃO DOS DADOS POR FAIXA ---

# Agrupar por faixa e calcular a média para cada métrica de interesse
media_por_faixa = df_qualidade.groupby('faixa')[[
    'num_review_comments',
    'densidade_comentarios',
    'rework_commits',
    'proporcao_changes_requested'
]].mean().reindex(['E', 'D', 'C', 'B', 'A']) # Ordenar da menor para a maior experiência

print("\n--- Análise Agregada ---")
print("Métricas médias de Qualidade e Revisão por Faixa de Experiência:")
print(media_por_faixa)


# --- 2. VISUALIZAÇÃO DOS RESULTADOS ---

import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de estilo para os gráficos
sns.set(style="whitegrid", palette="viridis", font_scale=1.1)

# ----- VISUALIZAÇÃO 1: Gráfico de Barras (Densidade de Comentários) -----
# Esta é a visualização mais importante para a sua hipótese.

plt.figure(figsize=(12, 7))
barplot = sns.barplot(
    x=media_por_faixa.index,
    y=media_por_faixa['densidade_comentarios']
)
plt.title('Densidade Média de Comentários por Faixa de Experiência', fontsize=18, pad=20)
plt.xlabel('Faixa de Experiência do Desenvolvedor', fontsize=14)
plt.ylabel('Média de Comentários por Linha de Código', fontsize=14)

# Adicionar os valores exatos no topo de cada barra
for p in barplot.patches:
    barplot.annotate(format(p.get_height(), '.4f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points')

plt.savefig('grafico_densidade_comentarios.png') # Salva o gráfico como imagem
print("\nGráfico 'densidade_comentarios.png' foi salvo.")


# ----- VISUALIZAÇÃO 2: Gráfico de Dispersão (Tamanho do PR vs. Comentários) -----
# Este gráfico mostra a relação bruta, com as faixas separadas por cores.

plt.figure(figsize=(14, 9))

# Com 73k pontos, o gráfico ficaria ilegível (overplotting).
# É essencial usar uma amostra aleatória para a visualização.
amostra_df = df_qualidade.sample(n=min(len(df_qualidade), 5000), random_state=42)

scatterplot = sns.scatterplot(
    data=amostra_df,
    x='tamanho_pr',
    y='num_review_comments',
    hue='faixa',
    hue_order=['E', 'D', 'C', 'B', 'A'],
    palette='viridis_r', # Invertido para A ser escuro
    alpha=0.6,
    s=60
)
plt.title('Tamanho do PR vs. Quantidade de Comentários', fontsize=18, pad=20)
plt.xlabel('Tamanho do PR (Adições + Deleções)', fontsize=14)
plt.ylabel('Número de Comentários de Revisão', fontsize=14)

# Limitar os eixos para focar na maior parte dos dados, ignorando outliers extremos
plt.xlim(0, amostra_df['tamanho_pr'].quantile(0.95))
plt.ylim(0, amostra_df['num_review_comments'].quantile(0.95))

plt.legend(title='Faixa de Experiência')
plt.savefig('grafico_tamanho_vs_comentarios.png')
print("Gráfico 'tamanho_vs_comentarios.png' foi salvo.")

plt.show() # Mostra os gráficos na tela