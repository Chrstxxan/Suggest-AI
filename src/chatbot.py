import unicodedata
from src.recommender import InteractiveRecommender

# vou fazer o codigo comentado pra não me perdrer
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

def reforcar_por_genero(recomendacoes, gostos, movies_map, top_n=5):
    compativeis = []
    for filme in recomendacoes:
        genero = movies_map.get(filme)
        if genero in gostos:
            compativeis.append(filme)
    if len(compativeis) >= 3:
        return compativeis[:top_n]
    elif compativeis:
        restantes = [f for f in recomendacoes if f not in compativeis]
        return (compativeis + restantes)[:top_n]
    return recomendacoes[:top_n]

def recomendar_por_chat(frase: str, recommender: InteractiveRecommender, top_n: int = 3):
    generos = set(recommender.movies.values())
    gostos, aversoes = interpretar_frase(frase, generos)

    if not gostos:
        return "Não encontrei gêneros válidos para o que você escreveu. Tente de novo com algo como 'gosto de ação e evito comédia'."

    nome = input("Qual é seu nome? ").strip()

    # entrada do usuario para quahntos filmes por rodada
    while True:
        try:
            quantos_por_rodada = int(input("Quantos filmes você quer que sejam recomendados por rodada? (3 a 7): ").strip())
            if 3 <= quantos_por_rodada <= 7:
                break
            else:
                print("Escolha um número entre 3 e 7.")
        except ValueError:
            print("Entrada inválida! Digite um número entre 3 e 7.")

    aprovados = []
    mostrados = set()
    tentativas = 0
    max_tentativas = 3
    print(f"Você tem até {max_tentativas} para aprovar pelo menos 3 filmes para que seu usuário seja salvo na base do modelo.")

    # criei usuaruio temporario pra poder salvar depois so o que ele aprovar no feedback
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

        recs = filmes_disponiveis[:quantos_por_rodada]
        recs_filtradas = reforcar_por_genero(recs, gostos, recommender.movies, top_n=quantos_por_rodada)

        print(f"\nBaseado no que você disse, recomendo: {', '.join(recs_filtradas)}\n")

        for f in recs_filtradas:
            if f in mostrados:
                continue

            # laço pra obrigar o usuario a responder o feedback e nao deixar vazio
            while True:
                fb = input(f"Você gostou do filme '{f}'? digite 's' para sim ou 'n' para não: ").strip().lower()
                if fb in ["s", "n"]:
                    break
                print("Entrada inválida! Digite 's' para sim ou 'n' para não.")

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

        # normalizando os pesos pra somar 1
        total = sum(temp_user["preferences"].values()) or 1.0
        for g in temp_user["preferences"]:
            temp_user["preferences"][g] /= total

    if aprovados:
        print(f"\nVocê aprovou {len(aprovados)} filme(s).")
        salvar = input("Deseja salvar seus filmes na base de dados para que o modelo aprenda com você? Digite 's' para sim e 'n' para não: ").strip().lower()
        if salvar == "s":
            entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados])
            recommender.add_user_with_genres(nome, entrada_final)
            return "Recomendações atualizadas com base no seu feedback e usuário salvo no sistema! Obrigado."
        else:
            return "Você optou por não salvar seus filmes na base de dados. Obrigado."
    else:
        return "Feedback registrado, mas como menos de 3 filmes foram aprovados seu usuário não foi salvo."
