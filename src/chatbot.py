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

def gerar_filmes_por_genero(gostos, aversoes, movies_map):
    filmes = []
    for filme, genero in movies_map.items():
        if genero in gostos and genero not in aversoes:
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
    filmes_relevantes = gerar_filmes_por_genero(gostos, aversoes, recommender.movies)[:5]
    if not filmes_relevantes:
        return "Não encontrei filmes com esse perfil no catálogo."

    # Inicializa um usuário temporário apenas na memória
    temp_user = {
        "user_id": "temp",
        "nome": nome,
        "movies": filmes_relevantes[:3],
        "preferences": {g: (1.0 if g in gostos else 0.0) for g in generos}
    }

    # Função auxiliar para gerar recomendações para usuário temporário
    def get_recs_temp(temp_user_dict, top_n=3):
        recs = {}
        for f, g in recommender.movies.items():
            if f in temp_user_dict["movies"]:
                continue
            score = temp_user_dict["preferences"].get(g, 0.0)
            if score > 0:
                recs[f] = score
        sorted_items = sorted(recs.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_items[:top_n]]

    recs = get_recs_temp(temp_user, top_n=top_n)
    recs_filtradas = reforcar_por_genero(recs, gostos, recommender.movies)

    if not recs_filtradas:
        return "Não encontrei recomendações que combinem com seus gostos. Tente descrever de outro jeito."

    print(f"\nBaseado no que você disse, recomendo: {', '.join(recs_filtradas)}\n")

    aprovados = []
    for f in recs_filtradas:
        fb = input(f"Você gostou do filme '{f}'? [s/n]: ").strip().lower()
        if fb in ["s", "n"]:
            if fb == "s":
                aprovados.append(f)
            # Atualiza pesos temporários apenas na memória
            genero = recommender.movies.get(f)
            if genero:
                if fb == "s":
                    temp_user["preferences"][genero] += 0.1
                else:
                    temp_user["preferences"][genero] = max(0.0, temp_user["preferences"][genero] - 0.1)

    # Somente salva o usuário real se aprovou pelo menos um filme
    if aprovados:
        entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados[:3]])
        recommender.add_user_with_genres(nome, entrada_final)
        return "Recomendações atualizadas com base no seu feedback e usuário salvo no sistema!"
    else:
        return "Feedback registrado, mas nenhum filme foi aprovado. Usuário não foi salvo."
