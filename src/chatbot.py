import unicodedata
from src.recommender import InteractiveRecommender

def normalizar_texto(txt: str) -> str:
    txt = txt.lower().strip()
    return unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")

def interpretar_frase(frase: str, generos_disponiveis):
    frase_norm = normalizar_texto(frase)
    gostos, aversoes = [], []
    negativos = ["nao gosto de", "evito", "dispenso", "nao curto", "odiar", "odeio"]
    positivos = ["gosto de", "curto", "quero", "prefiro", "adoro"]

    for g in generos_disponiveis:
        if any(neg in frase_norm and g in frase_norm for neg in negativos):
            aversoes.append(g)
        elif any(pos in frase_norm and g in frase_norm for pos in positivos):
            gostos.append(g)
    return gostos, aversoes

def gerar_filmes_por_genero(gostos, aversoes, movies_map, excluidos=[]):
    filmes = []
    for filme, genero in movies_map.items():
        if genero in gostos and genero not in aversoes and filme not in excluidos:
            filmes.append(filme)
    return filmes

def reforcar_por_genero(recomendacoes, gostos, movies_map):
    compativeis = []
    for filme in recomendacoes:
        genero = movies_map.get(filme)
        if genero in gostos:
            compativeis.append(filme)
    if len(compativeis) >= 3:
        return compativeis[:5]
    elif compativeis:
        restantes = [f for f in recomendacoes if f not in compativeis]
        return (compativeis + restantes)[:5]
    return recomendacoes[:5]

def recomendar_por_chat(frase: str, recommender: InteractiveRecommender, top_n: int = 3):
    generos = set(recommender.movies.values())
    gostos, aversoes = interpretar_frase(frase, generos)

    if not gostos:
        return "Não encontrei gêneros válidos na sua descrição. Tente algo como 'gosto de ação e evito comédia'."

    nome = input("Qual é seu nome? ").strip()
    aprovados = []
    mostrados = set()
    tentativas = 0
    max_tentativas = 5

    # Usuário temporário em memória
    temp_user = {
        "user_id": "temp",
        "nome": nome,
        "movies": [],
        "preferences": {g: (1.0 if g in gostos else 0.0) for g in generos}
    }

    while len(aprovados) < 3 and tentativas < max_tentativas:
        tentativas += 1
        filmes_disponiveis = gerar_filmes_por_genero(gostos, aversoes, recommender.movies, excluidos=mostrados)
        if not filmes_disponiveis:
            break

        recs = filmes_disponiveis[:5]
        recs_filtradas = reforcar_por_genero(recs, gostos, recommender.movies)

        print(f"\nBaseado no que você disse, recomendo: {', '.join(recs_filtradas)}\n")

        for f in recs_filtradas:
            if f in mostrados:
                continue
            fb = input(f"Você gostou do filme '{f}'? [s/n]: ").strip().lower()
            mostrados.add(f)

            genero = recommender.movies.get(f)
            if not genero:
                continue

            if fb == "s":
                aprovados.append(f)
                temp_user["movies"].append(f)
                temp_user["preferences"][genero] += 0.1  # reforço positivo
            elif fb == "n":
                temp_user["preferences"][genero] = max(0.0, temp_user["preferences"][genero] - 0.05)  # penalidade leve

        # normaliza os pesos para somar 1
        total = sum(temp_user["preferences"].values()) or 1.0
        for g in temp_user["preferences"]:
            temp_user["preferences"][g] /= total

    if aprovados:
        entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados])
        recommender.add_user_with_genres(nome, entrada_final)
        return f"Recomendações atualizadas com base no seu feedback e usuário salvo no sistema! Você aprovou {len(aprovados)} filme(s)."
    else:
        return "Feedback registrado, mas nenhum filme foi aprovado. Usuário não foi salvo."
