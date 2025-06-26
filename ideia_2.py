# 2. Análise de Eficiência e Fluxo de Trabalho
# Esta análise busca entender se a experiência leva a um processo de integração mais suave e rápido.
# Métricas a extrair:
# Tempo para o merge (Time to Merge): Calcule a diferença entre merged_at e created_at para cada PR. PRs de desenvolvedores da Faixa A são mesclados mais rapidamente?
# Taxa de sucesso da Integração Contínua (CI): Analise o campo ci_status_on_head. Calcule a porcentagem de PRs que tinham um status "success" na primeira vez em que foram submetidos. Desenvolvedores experientes quebram a build com menos frequência?
# Padrões de trabalho: Analise a distribuição de created_at por hora do dia e dia da semana. Existem diferenças nos padrões de trabalho entre as faixas? (Esta é uma análise mais exploratória).
# Visualizações sugeridas:
# Gráficos de barras com a média do "tempo para o merge" para cada faixa, com barras de erro para indicar a variância.
# Um gráfico de pizza ou barras empilhadas mostrando a proporção de status de CI (success, failure, pending) por faixa de desenvolvedor.

import os
import json
import random
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Caminho base
base_path = "repositories-mined"

# Armazenamento dos dados de PRs
todos_os_prs = []

print(f"Iniciando varredura em '{base_path}'...\n")

# Percorre cada repositório
for repo in os.listdir(base_path):
    repo_path = os.path.join(base_path, repo)
    if not os.path.isdir(repo_path):
        continue

    # Lê os 75 autores
    sample_path = os.path.join(repo_path, "sample-devs.jsonl")
    if not os.path.isfile(sample_path):
        continue

    with open(sample_path, 'r', encoding='utf-8') as f:
        devs = [json.loads(line) for line in f]

    # Escolhe 15 autores aleatórios
    autores_escolhidos = random.sample(devs, min(15, len(devs)))

    for autor in autores_escolhidos:
        nome = autor['author']
        faixa = autor['faixa']
        caminho_results = os.path.join(repo_path, "developer", nome, "results")

        if not os.path.isdir(caminho_results):
            continue

        for arquivo_json in os.listdir(caminho_results):
            if not arquivo_json.endswith(".json"):
                continue

            caminho_arquivo = os.path.join(caminho_results, arquivo_json)

            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    pr = json.load(f)

                pr['author'] = nome
                pr['faixa'] = faixa
                pr['repo'] = repo
                todos_os_prs.append(pr)
            except Exception as e:
                print(f"Erro ao ler {caminho_arquivo}: {e}")

print(f"\nTotal de PRs coletados: {len(todos_os_prs)}")

# --------------------------
# Análise de Eficiência
# --------------------------
def analisar_eficiencia(prs):
    registros = []

    for pr in prs:
        try:
            created_at = datetime.fromisoformat(pr['created_at'].replace("Z", "+00:00"))
        except:
            continue

        merged_at = pr.get("merged_at")
        tempo_merge = None
        if merged_at:
            try:
                merged = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
                tempo_merge = (merged - created_at).total_seconds() / 3600
            except:
                pass

        ci = pr.get("ci_status_on_head", "unknown")
        ci_sucesso = 1 if ci == "success" else 0
        ci_valido = ci in ["success", "failure", "pending"]

        registros.append({
            "faixa": pr["faixa"],
            "tempo_merge_horas": tempo_merge,
            "ci_status": ci,
            "ci_sucesso": ci_sucesso,
            "ci_valido": ci_valido,
            "hora_criacao": created_at.hour,
            "dia_semana_criacao": created_at.weekday(),
        })

    return pd.DataFrame(registros)

df = analisar_eficiencia(todos_os_prs)

# --------------------------
# Paleta de cores consistente (husl)
# --------------------------
ordem_faixas = ["A", "B", "C", "D", "E"]
cores_husl = sns.color_palette("husl", len(ordem_faixas))
paleta_consistente = dict(zip(ordem_faixas, cores_husl))

# --------------------------
# Gráficos e Tabelas
# --------------------------
sns.set(style="whitegrid", font_scale=1.1)

def gerar_graficos(df):
    """
    Gera e salva os gráficos da análise de eficiência sem exibi-los na tela.
    """
    ordem = ["E", "D", "C", "B", "A"]

    # --- Tempo médio para merge ---
    plt.figure(figsize=(10,6))
    sns.barplot(data=df, x='faixa', y='tempo_merge_horas',
                order=ordem, errorbar='sd', palette=paleta_consistente)
    plt.title("Tempo Médio para Merge por Faixa")
    plt.xlabel("Faixa")
    plt.ylabel("Tempo (quantidade de horas)")
    plt.savefig("grafico_tempo_para_merge.png")
    print("Salvo: grafico_tempo_para_merge.png")
    plt.close()

    # --- Taxa de sucesso CI ---
    plt.figure(figsize=(10,6))
    ci = df[df["ci_valido"]].groupby("faixa")["ci_sucesso"].mean().reindex(ordem)
    sns.barplot(x=ci.index, y=ci.values, palette=paleta_consistente)
    plt.title("Taxa de Sucesso da CI por Faixa")
    plt.xlabel("Faixa")
    plt.ylabel("Taxa de Sucesso (%)")
    plt.ylim(0, 1)
    plt.yticks([i/10 for i in range(0, 11)], [f"{i*10}" for i in range(0, 11)])
    plt.savefig("grafico_ci_sucesso.png")
    print("Salvo: grafico_ci_sucesso.png")
    plt.close()

    # --- Hora de criação ---
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x='faixa', y='hora_criacao', order=ordem, palette=paleta_consistente)
    plt.title("Hora do Dia de Criação dos PRs")
    plt.xlabel("Faixa")
    plt.ylabel("Hora do Dia (h)")
    plt.savefig("grafico_hora_criacao.png")
    print("Salvo: grafico_hora_criacao.png")
    plt.close()

    # --- Dia da semana ---
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x='faixa', y='dia_semana_criacao', order=ordem, palette=paleta_consistente)
    plt.title("Dia da Semana de Criação dos PRs")
    plt.xlabel("Faixa")
    plt.ylabel("Dia da Semana")
    plt.yticks(ticks=range(7), labels=["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
    plt.savefig("grafico_dia_criacao.png")
    print("Salvo: grafico_dia_criacao.png")
    plt.close()

    return

# --------------------------
# Exibir resumo no console
# --------------------------
print("\n--- Tempo Médio para Merge por Faixa ---")
print(df.groupby('faixa')['tempo_merge_horas'].mean().reindex(["E", "D", "C", "B", "A"]))

print("\n--- Taxa de Sucesso da CI por Faixa ---")
print(df[df["ci_valido"]].groupby('faixa')['ci_sucesso'].mean().reindex(["E", "D", "C", "B", "A"]))

print("\n--- Hora Média de Criação ---")
print(df.groupby('faixa')['hora_criacao'].mean().reindex(["E", "D", "C", "B", "A"]))

print("\n--- Dia Médio de Criação (0=Segunda) ---")
print(df.groupby('faixa')['dia_semana_criacao'].mean().reindex(["E", "D", "C", "B", "A"]))

# Gerar gráficos
gerar_graficos(df)

print("Finalizado")
