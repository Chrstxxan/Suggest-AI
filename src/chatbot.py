import unicodedata
from src.recommender import InteractiveRecommender
import random

# === Normalização básica de texto ===
def normalizar_texto(txt: str) -> str:
    txt = txt.lower().strip()
    return unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")

# === Dicionário global para armazenar filmes já recomendados nesta execução ===
filmes_recomendados_global = set()

# === Interpreta frase do usuário (gostos e aversões) ===
def interpretar_frase(frase: str, generos_disponiveis):
    frase_norm = normalizar_texto(frase)
    gostos, aversoes = [], []

    positivos = ["gosto de", "curto", "adoro", "amo", "prefiro", "quero"]
    negativos = ["nao gosto de", "evito", "dispenso", "nao curto", "odeio", "detesto", "odiar"]

    # Normaliza e substitui vírgulas por " e " para evitar perda de contexto
    frase_norm = frase_norm.replace(",", " e ")

    # Mapeia contexto (positivo/negativo) para cada trecho
    contexto = None
    palavras = frase_norm.split()

    buffer = []
    for i, palavra in enumerate(palavras):
        buffer.append(palavra)
        trecho = " ".join(buffer)

        # Atualiza contexto
        if any(trecho.endswith(p) for p in positivos):
            contexto = "positivo"
            buffer = []  # zera o buffer após marcar o contexto
            continue
        elif any(trecho.endswith(n) for n in negativos):
            contexto = "negativo"
            buffer = []
            continue

        # Quando encontramos um gênero, associamos com o contexto atual
        for genero in generos_disponiveis:
            genero_norm = normalizar_texto(genero)
            # Agora verifica se o gênero está contido em qualquer trecho
            if genero_norm in trecho:
                if contexto == "positivo" and genero not in gostos:
                    gostos.append(genero)
                elif contexto == "negativo" and genero not in aversoes:
                    aversoes.append(genero)

    return gostos, aversoes

# === Gera lista de filmes por gênero ===
def gerar_filmes_por_genero(gostos, aversoes, movies_map, excluidos=[]):
    filmes = []
    for filme, genero in movies_map.items():
        if genero in gostos and genero not in aversoes and filme not in excluidos:
            filmes.append(filme)
    return filmes

# === Reforça recomendações com gêneros compatíveis ===
def reforcar_por_genero(recomendacoes, gostos, movies_map, top_n=5):
    compativeis = [f for f in recomendacoes if movies_map.get(f) in gostos]
    if len(compativeis) >= 3:
        return compativeis[:top_n]
    elif compativeis:
        restantes = [f for f in recomendacoes if f not in compativeis]
        return (compativeis + restantes)[:top_n]
    return recomendacoes[:top_n]

# === Função de recomendação misturando gêneros com embaralhamento ===
def recomendar_filmes_por_genero(generos_usuario, filmes_df, qtd):
    """Gera recomendações misturando vários gêneros com embaralhamento e memória anti-repetição."""
    filmes_por_genero = {}

    for genero in generos_usuario:
        subset = filmes_df[filmes_df["genero"].str.contains(genero, case=False, na=False)]
        lista_filmes = subset["titulo"].tolist()

        # Embaralha cada gênero pra variar
        random.shuffle(lista_filmes)

        # Remove filmes já recomendados em sessões anteriores
        lista_filmes = [f for f in lista_filmes if f not in filmes_recomendados_global]

        if lista_filmes:
            filmes_por_genero[genero] = lista_filmes

    # Se não achar nada, retorna vazio
    if not filmes_por_genero:
        return []

    # Intercala os filmes (round-robin)
    recomendacoes = []
    while len(recomendacoes) < qtd:
        for genero, lista in filmes_por_genero.items():
            if lista:
                filme = lista.pop(0)
                if filme not in recomendacoes:
                    recomendacoes.append(filme)
                if len(recomendacoes) >= qtd:
                    break
        # Sai se todas as listas esvaziarem
        if all(len(lista) == 0 for lista in filmes_por_genero.values()):
            break

    # Embaralha as recomendações finais para não ficarem sempre na mesma ordem
    random.shuffle(recomendacoes)

    # Atualiza o registro global de filmes recomendados
    filmes_recomendados_global.update(recomendacoes)

    return recomendacoes

# === Função principal do modo Chatbot ===
def recomendar_por_chat(frase: str, recommender: InteractiveRecommender, top_n: int = 3):
    generos = set(recommender.movies.values())
    gostos, aversoes = interpretar_frase(frase, generos)

    nome = input("Qual é seu nome? ").strip()

    # Entrada de quantos filmes por rodada (mesmo para casos só de aversão)
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

    # === Caso 1: só aversões ===
    if not gostos and aversoes:
        print("Você mencionou apenas gêneros que não gosta.")
        print("Vou te recomendar os filmes mais populares que não sejam desses gêneros.\n")

        filmes_disponiveis = [f for f, g in recommender.movies.items() if g not in aversoes]
        if not filmes_disponiveis:
            return "Não há filmes disponíveis fora dos gêneros que você rejeitou."

        # ✅ Embaralha antes de recomendar (para variar os resultados)
        random.shuffle(filmes_disponiveis)

        # mantém fluxo normal (feedback + salvamento)
        recs = filmes_disponiveis[:quantos_por_rodada]
        print(f"Recomendações neutras pra você: {', '.join(recs)}\n")

        for f in recs:
            while True:
                fb = input(f"Você gostou do filme '{f}'? digite 's' para sim ou 'n' para não: ").strip().lower()
                if fb in ["s", "n"]:
                    break
                print("Entrada inválida! Digite 's' para sim ou 'n' para não.")
            if fb == "s":
                aprovados.append(f)

        if aprovados:
            salvar = input("Deseja salvar seus filmes na base de dados? (s/n): ").strip().lower()
            if salvar == "s":
                entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados])
                recommender.add_user_with_genres(nome, entrada_final)
                return "Usuário salvo com base nas preferências neutras! Obrigado."
            return "Você optou por não salvar seus filmes. Obrigado."
        return "Nenhum filme foi aprovado, usuário não salvo."

    # === Caso 2: sem gostos nem aversões reconhecidos ===
    if not gostos:
        return "Não encontrei gêneros válidos para o que você escreveu. Tente algo como 'gosto de ação e evito comédia'."

    print(f"Você tem até {max_tentativas} tentativas para aprovar pelo menos 3 filmes para que seu usuário seja salvo.\n")

    # Usuário temporário
    temp_user = {
        "user_id": "temp",
        "nome": nome,
        "movies": [],
        "preferences": {g: (1.0 if g in gostos else 0.0) for g in generos}
    }

    # === Caso 3: gostos (e talvez aversões misturadas) ===
    while len(aprovados) < 3 and tentativas < max_tentativas:
        tentativas += 1

        # Divide recomendações equilibradas entre gêneros
        filmes_por_genero = {
            g: [f for f, gen in recommender.movies.items() if gen == g and gen not in aversoes and f not in mostrados]
            for g in gostos
        }

        # ✅ Embaralha filmes de cada gênero antes de misturar
        for g in filmes_por_genero:
            random.shuffle(filmes_por_genero[g])

        filmes_equilibrados = []
        while len(filmes_equilibrados) < quantos_por_rodada and any(filmes_por_genero.values()):
            for g in gostos:
                if filmes_por_genero[g]:
                    filmes_equilibrados.append(filmes_por_genero[g].pop(0))
                if len(filmes_equilibrados) >= quantos_por_rodada:
                    break

        if not filmes_equilibrados:
            print("Não há mais filmes disponíveis nesses gêneros.")
            break

        # ✅ Embaralha o conjunto final antes de exibir
        random.shuffle(filmes_equilibrados)

        recs_filtradas = reforcar_por_genero(filmes_equilibrados, gostos, recommender.movies, top_n=quantos_por_rodada)
        print(f"\nBaseado no que você disse, recomendo: {', '.join(recs_filtradas)}\n")

        for f in recs_filtradas:
            if f in mostrados:
                continue

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
                temp_user["preferences"][genero] += 0.1
            elif fb == "n":
                temp_user["preferences"][genero] = max(0.0, temp_user["preferences"][genero] - 0.05)

        total = sum(temp_user["preferences"].values()) or 1.0
        for g in temp_user["preferences"]:
            temp_user["preferences"][g] /= total

    if aprovados:
        print(f"\nVocê aprovou {len(aprovados)} filme(s).")
        salvar = input("Deseja salvar seus filmes na base de dados? (s/n): ").strip().lower()
        if salvar == "s":
            entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados])
            recommender.add_user_with_genres(nome, entrada_final)
            return "Recomendações atualizadas com base no seu feedback e usuário salvo! Obrigado."
        else:
            return "Você optou por não salvar seus filmes. Obrigado."
    else:
        return "Feedback registrado, mas como menos de 3 filmes foram aprovados, o usuário não foi salvo."
