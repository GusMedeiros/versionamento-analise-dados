import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# --- 1. Carregar e Preparar os Dados ---
print("1. Lendo os dados de sentimento classificados do arquivo CSV...")
try:
    df = pd.read_csv('analise_sentimento.csv')
except FileNotFoundError:
    print("ERRO: O arquivo 'analise_sentimento.csv' não foi encontrado. Por favor, crie-o primeiro.")
    exit()

# Definir a ordem correta para as faixas e categorias para o gráfico
FAIXA_ORDER = ['E', 'D', 'C', 'B', 'A']
CATEGORIA_ORDER = ['A', 'B', 'C', 'D', 'E']
CATEGORIA_LABELS = {
    'A': 'A. Construtivo/Diretivo',
    'B': 'B. Positivo/Encorajador',
    'C': 'C. Crítico/Negativo',
    'D': 'D. Questionador/Exploratório',
    'E': 'E. Informativo/Contextual'
}
# Criar uma coluna combinada para o eixo X para facilitar a plotagem
df['estrato'] = df['faixa_autor'] + ' | ' + df['resultado_pr']

# --- 2. Calcular as Proporções ---
print("2. Calculando as proporções de cada categoria de sentimento...")
# Contar o número de ocorrências de cada categoria dentro de cada estrato
counts = df.groupby(['estrato', 'categoria_sentimento']).size().unstack(fill_value=0)

# Normalizar para obter porcentagens (somar cada linha para 100%)
counts_pct = counts.div(counts.sum(axis=1), axis=0) * 100

# Ordenar o índice e as colunas para o gráfico
ordem_estratos = [f'{faixa} | {res}' for res in ['Aceito', 'Recusado'] for faixa in FAIXA_ORDER]
counts_pct = counts_pct.reindex(index=ordem_estratos, columns=CATEGORIA_ORDER)

# --- 3. Gerar o Gráfico ---
print("3. Gerando o gráfico de barras empilhadas 100%...")
sns.set_theme(style="whitegrid")
ordem_faixas = ["A", "B", "C", "D", "E"]
cores_husl = sns.color_palette("husl", len(ordem_faixas))
paleta_consistente = dict(zip(ordem_faixas, cores_husl))
ax = counts_pct.plot(
    kind='bar',
    stacked=True,
    figsize=(20, 10),
    colormap='viridis_r', # Uma paleta de cores agradável
    width=0.8
)

# --- 4. Adicionar Rótulos e Títulos ---
plt.title('Distribuição Proporcional do Sentimento dos Comentários por Faixa e Resultado do PR', fontsize=20, pad=20)
plt.xlabel('Estrato (Faixa do Autor | Resultado do PR)', fontsize=14)
plt.ylabel('Proporção de Comentários (%)', fontsize=14)
plt.xticks(rotation=45, ha='right') # Rotaciona os labels do eixo X para melhor legibilidade
ax.yaxis.set_major_formatter(PercentFormatter()) # Formata o eixo Y como porcentagem

# Adicionar a legenda
handles, labels = ax.get_legend_handles_labels()
ax.legend(
    handles,
    [CATEGORIA_LABELS[label] for label in labels], # Usa os nomes completos na legenda
    title='Categoria do Sentimento',
    bbox_to_anchor=(1.02, 1),
    loc='upper left'
)

plt.tight_layout(rect=[0, 0, 0.85, 1]) # Ajusta o layout para a legenda caber
plt.show()