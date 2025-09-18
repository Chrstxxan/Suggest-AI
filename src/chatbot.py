import pandas as pd
import unicodedata
from src.recommender import InteractiveRecommender

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto

def carregar_generos(path_csv):
    df = pd.read_csv(path_csv)
    generos_filmes = {}
    for _, row in df.iterrows():
        genero = normalizar(row["genero"].strip())
        generos_filmes[row["filme"]] = genero
    return generos_filmes

generos_filmes = carregar_generos(r"D:/Dev/projetos vscode/SuggestAI/data/filmes.csv")

def interpretar_frase(frase):
    frase = normalizar(frase)
    gostos = []
    aversoes = []

    todos_generos = set(generos_filmes.values())
    negativos = ["nao gosto de", "evito", "dispenso"]
    positivos = ["gosto de", "curto", "quero", "prefiro"]

    for genero in todos_generos:
        if any(neg in frase and genero in frase for neg in negativos):
            aversoes.append(genero)
        elif any(pos in frase and genero in frase for pos in positivos):
            gostos.append(genero)

    return gostos, aversoes

def gerar_filmes_por_genero(gostos, aversoes):
    filmes_relevantes = []
    for filme, genero in generos_filmes.items():
        if genero in gostos and genero not in aversoes:
            filmes_relevantes.append(filme)
    return filmes_relevantes

def reforcar_por_genero(recomendacoes, gostos, generos_filmes):
    compativeis = []
    for filme in recomendacoes:
        genero = generos_filmes.get(filme)
        if genero in gostos:
            compativeis.append(filme)

    if len(compativeis) >= 3:
        return compativeis[:5]
    elif compativeis:
        restantes = [f for f in recomendacoes if f not in compativeis]
        return (compativeis + restantes)[:5]
    return recomendacoes[:5]

def recomendar_por_chat(frase, recommender, top_n=3):
    gostos, aversoes = interpretar_frase(frase)
    filmes_preferidos = gerar_filmes_por_genero(gostos, aversoes)

    if not filmes_preferidos:
        return "Não encontrei filmes com esse perfil. Pode tentar outra descrição?"

    nome = input("Qual é seu nome? ").strip()

    filmes_para_salvar = [f for f in filmes_preferidos if f in generos_filmes][:3]
    if not filmes_para_salvar:
        return "Não encontrei filmes válidos para salvar. Tente outra descrição."

    entrada_formatada = ", ".join([f"{filme} - {generos_filmes[filme]}" for filme in filmes_para_salvar])

    user_id = recommender.add_user_with_genres(nome, entrada_formatada)

    recomendacoes = recommender.get_recommendations(user_id, top_n=top_n)
    recomendacoes_filtradas = reforcar_por_genero(recomendacoes, gostos, generos_filmes)

    if not recomendacoes_filtradas:
        return "Não encontrei recomendações que combinem com seus gostos. Tente outra descrição?"

    print(f"\nBaseado no que você disse, recomendo: {', '.join(recomendacoes_filtradas)}")

    filmes_aprovados = []
    for filme in recomendacoes_filtradas:
        feedback = input(f"Você gostou do filme '{filme}'? [s/n]: ").strip().lower()
        if feedback in ["s", "n"]:
            recommender.update_weights(user_id, filme, feedback)
            if feedback == "s":
                filmes_aprovados.append(filme)

    if filmes_aprovados:
        entrada_formatada_final = ", ".join([f"{filme} - {generos_filmes[filme]}" for filme in filmes_aprovados[:3]])
        recommender.add_user_with_genres(nome, entrada_formatada_final)

    return "Recomendações atualizadas com base no seu feedback!"
