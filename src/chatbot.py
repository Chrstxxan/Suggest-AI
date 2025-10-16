import unicodedata
import os
import random
import pandas as pd
from src.recommender import InteractiveRecommender
import uuid

# =====================
# Variáveis globais
# =====================
filmes_recomendados_global = set()
rejeitados_file = "D:/Dev/PyCharm Projects/SuggestAI/data/usuarios_rejeitados.csv"


# =====================
# Funções auxiliares
# =====================
def normalizar_texto(txt: str) -> str:
    txt = txt.lower().strip()
    return unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")


def interpretar_frase(frase: str, generos_disponiveis):
    frase_norm = normalizar_texto(frase)
    gostos, aversoes = [], []
    positivos = ["gosto de", "curto", "adoro", "amo", "prefiro", "quero"]
    negativos = ["nao gosto de", "evito", "dispenso", "nao curto", "odeio", "detesto", "odiar"]
    frase_norm = frase_norm.replace(",", " e ")
    contexto = None
    palavras = frase_norm.split()
    buffer = []
    for i, palavra in enumerate(palavras):
        buffer.append(palavra)
        trecho = " ".join(buffer)
        if any(trecho.endswith(p) for p in positivos):
            contexto = "positivo"
            buffer = []
            continue
        elif any(trecho.endswith(n) for n in negativos):
            contexto = "negativo"
            buffer = []
            continue
        for genero in generos_disponiveis:
            genero_norm = normalizar_texto(genero)
            if genero_norm in trecho:
                if contexto == "positivo" and genero not in gostos:
                    gostos.append(genero)
                elif contexto == "negativo" and genero not in aversoes:
                    aversoes.append(genero)
    return gostos, aversoes


def registrar_rejeitados(user_id, nome, filmes_rejeitados):
    if not filmes_rejeitados:
        return
    try:
        os.makedirs(os.path.dirname(rejeitados_file), exist_ok=True)
        if not os.path.exists(rejeitados_file):
            pd.DataFrame(columns=["user_id", "nome"] + [f"filme{i + 1}" for i in range(len(filmes_rejeitados))]).to_csv(
                rejeitados_file, index=False)
        df = pd.read_csv(rejeitados_file)
        linha = {"user_id": user_id, "nome": nome}
        for i, filme in enumerate(filmes_rejeitados, 1):
            linha[f"filme{i}"] = filme
        for i in range(1, len(filmes_rejeitados) + 1):
            col = f"filme{i}"
            if col not in df.columns:
                df[col] = ""
        df = pd.concat([df, pd.DataFrame([linha])], ignore_index=True)
        df.to_csv(rejeitados_file, index=False, encoding="utf-8")
    except Exception as e:
        print(f"⚠️ Erro ao salvar rejeições: {e}")


# =====================
# Funções do terminal
# =====================
def gerar_filmes_por_genero(gostos, aversoes, movies_map, excluidos=[]):
    filmes = []
    for filme, genero in movies_map.items():
        if genero in gostos and genero not in aversoes and filme not in excluidos:
            filmes.append(filme)
    return filmes


def reforcar_por_genero(recomendacoes, gostos, movies_map, top_n=5):
    compativeis = [f for f in recomendacoes if movies_map.get(f) in gostos]
    if len(compativeis) >= 3:
        return compativeis[:top_n]
    elif compativeis:
        restantes = [f for f in recomendacoes if f not in compativeis]
        return (compativeis + restantes)[:top_n]
    return recomendacoes[:top_n]


def recomendar_filmes_por_genero(generos_usuario, filmes_df, qtd):
    filmes_por_genero = {}
    for genero in generos_usuario:
        subset = filmes_df[filmes_df["genero"].str.contains(genero, case=False, na=False)]
        lista_filmes = subset["titulo"].tolist()
        random.shuffle(lista_filmes)
        lista_filmes = [f for f in lista_filmes if f not in filmes_recomendados_global]
        if lista_filmes:
            filmes_por_genero[genero] = lista_filmes
    if not filmes_por_genero:
        return []
    recomendacoes = []
    while len(recomendacoes) < qtd:
        for genero, lista in filmes_por_genero.items():
            if lista:
                filme = lista.pop(0)
                if filme not in recomendacoes:
                    recomendacoes.append(filme)
                if len(recomendacoes) >= qtd:
                    break
        if all(len(lista) == 0 for lista in filmes_por_genero.values()):
            break
    random.shuffle(recomendacoes)
    filmes_recomendados_global.update(recomendacoes)
    return recomendacoes


def recomendar_por_chat(frase: str, recommender: InteractiveRecommender, top_n: int = 3):
    generos = set(recommender.movies.values())
    gostos, aversoes = interpretar_frase(frase, generos)

    nome = input("Qual é seu nome? ").strip()
    while True:
        try:
            quantos_por_rodada = int(
                input("Quantos filmes você quer que sejam recomendados por rodada? (3 a 7): ").strip())
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

    if not gostos and aversoes:
        print("Você mencionou apenas gêneros que não gosta.")
        filmes_disponiveis = [f for f, g in recommender.movies.items() if g not in aversoes]
        if not filmes_disponiveis:
            return "Não há filmes disponíveis fora dos gêneros que você rejeitou."
        random.shuffle(filmes_disponiveis)
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
            salvar = input(
                "Deseja salvar seus filmes na base de dados? Digite 's' para sim e 'n' para não: ").strip().lower()
            if salvar == "s":
                entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados])
                user_id_real = recommender.add_user_with_genres(nome, entrada_final)
                filmes_rejeitados = [f for f in recs if f not in aprovados]
                registrar_rejeitados(user_id_real, nome, filmes_rejeitados)
                return "Usuário salvo com base nas preferências neutras! Obrigado."
            return "Você optou por não salvar seus filmes. Nada foi registrado. Obrigado"
        return "Nenhum filme foi aprovado, usuário não salvo."

    if not gostos:
        return "Não encontrei gêneros válidos para o que você escreveu. Tente algo como 'gosto de ação e evito comédia'."

    print(
        f"Você tem até {max_tentativas} tentativas para aprovar pelo menos 3 filmes para que seu usuário seja salvo.\n")
    temp_user = {
        "user_id": "temp",
        "nome": nome,
        "movies": [],
        "preferences": {g: (1.0 if g in gostos else 0.0) for g in generos}
    }

    while len(aprovados) < 3 and tentativas < max_tentativas:
        tentativas += 1
        filmes_por_genero = {
            g: [f for f, gen in recommender.movies.items() if gen == g and gen not in aversoes and f not in mostrados]
            for g in gostos
        }
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
        salvar = input(
            "Deseja salvar seus filmes na base de dados? Digite 's' para sim e 'n' para não: ").strip().lower()
        if salvar == "s":
            entrada_final = ", ".join([f"{f} - {recommender.movies[f]}" for f in aprovados])
            user_id_real = recommender.add_user_with_genres(nome, entrada_final)
            filmes_rejeitados = [f for f in mostrados if f not in aprovados]
            registrar_rejeitados(user_id_real, nome, filmes_rejeitados)
            return "Recomendações atualizadas com base no seu feedback e usuário salvo! Obrigado."
        else:
            return "Você optou por não salvar seus filmes. Nada foi registrado. Obrigado."
    else:
        return "Feedback registrado, mas como menos de 3 filmes foram aprovados, o usuário não foi salvo."


# =====================
# Função adicional para web
# =====================
def recomendar_por_chat_web(frase, nome, recommender, top_n=3, quantos_por_rodada=3, user_id=None):
    """
    Versão do chatbot para web.
    Agora retorna (recs, user_id): cria um usuário temporário em recommender.users
    e devolve o user_id para que o formulário de feedback possa persistir alterações.
    """
    generos = set(recommender.movies.values())
    gostos, aversoes = interpretar_frase(frase, generos)

    if not gostos:
        return ["Não encontrei gêneros válidos para o que você escreveu."], None

    aprovados = []
    mostrados = set()
    tentativas = 0
    max_tentativas = 3

    # cria um user_id temporário (numérico se possível)
    # tenta gerar id numérico sequencial para manter formato do CSV
    try:
        existing_ids = [int(uid) for uid in recommender.users.keys() if str(uid).isdigit()]
        new_id = str(max(existing_ids) + 1) if existing_ids else "1"
    except Exception:
        # fallback random id
        new_id = f"temp_{uuid.uuid4().hex[:8]}"

    # cria usuário temporário em memória (não grava no CSV ainda)
    temp_user = {
        "nome": nome or "",
        "movies": [],
        "preferences": {g: (1.0 if g in gostos else 0.0) for g in generos}
    }
    recommender.users[new_id] = temp_user

    # gera recomendações balanceadas por gênero (até coletar top_n)
    while len(aprovados) < top_n and tentativas < max_tentativas:
        tentativas += 1
        filmes_por_genero = {
            g: [f for f, gen in recommender.movies.items() if gen == g and gen not in aversoes and f not in mostrados]
            for g in gostos
        }
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
            break

        random.shuffle(filmes_equilibrados)
        recs_filtradas = reforcar_por_genero(filmes_equilibrados, gostos, recommender.movies, top_n=quantos_por_rodada)

        # adiciona sem duplicar
        for r in recs_filtradas:
            if r not in aprovados:
                aprovados.append(r)
            mostrados.add(r)
        # atualiza temp_user (em memória) com os filmes mostrados
        temp_user["movies"].extend([r for r in recs_filtradas if r not in temp_user["movies"]])
        for f in recs_filtradas:
            gen = recommender.movies.get(f)
            if gen:
                temp_user["preferences"][gen] = temp_user["preferences"].get(gen, 0.0) + 0.1

    # devolve a lista de recomendações e o user_id temporário (string)
    return aprovados[:top_n], new_id