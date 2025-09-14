import pandas as pd
import unicodedata

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto

def carregar_generos(path_csv):
    df = pd.read_csv(path_csv)
    generos_filmes = {}
    for _, row in df.iterrows():
        generos = [normalizar(g.strip()) for g in row["generos"].split(";")]
        generos_filmes[row["filme"]] = generos
    return generos_filmes

generos_filmes = carregar_generos(r"D:\Dev\projetos vscode\SuggestAI\data\filmes.csv")

def interpretar_frase(frase):
    frase = normalizar(frase)
    gostos = []
    aversoes = []

    todos_generos = set(g for generos in generos_filmes.values() for g in generos)
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

    for filme, generos in generos_filmes.items():
        if any(g in generos for g in gostos) and not any(a in generos for a in aversoes):
            filmes_relevantes.append(filme)

    return filmes_relevantes

def filtrar_por_genero(recomendacoes, gostos, generos_filmes):
    recomendadas_filtradas = []
    for filme in recomendacoes:
        generos = generos_filmes.get(filme, [])
        if any(g in generos for g in gostos):
            recomendadas_filtradas.append(filme)
    return recomendadas_filtradas

def recomendar_por_chat(frase, recommender, top_n=5):
    gostos, aversoes = interpretar_frase(frase)
    filmes_preferidos = gerar_filmes_por_genero(gostos, aversoes)

    '''print(f"\n Gostos: {gostos}")
    print(f" Aversões: {aversoes}")
    print(f" Filmes compatíveis: {filmes_preferidos}")'''

    if not filmes_preferidos:
        return "Não encontrei filmes com esse perfil. Pode tentar outra descrição?"

    nome = input("Qual é seu nome? ").strip()
    user_id = recommender.add_user_preferences(nome, filmes_preferidos)

    recomendacoes = recommender.recommend_by_cluster(user_id, top_n=top_n)
    if not recomendacoes:
        recomendacoes = recommender.recommend_by_similarity(user_id, top_n=top_n)
    if not recomendacoes:
        recomendacoes = recommender.recommend(user_id, top_n=top_n)

    recomendacoes = filtrar_por_genero(recomendacoes, gostos, generos_filmes)

    if not recomendacoes:
        return "Não encontrei recomendações que combinem com seus gostos. Tente outra descrição?"

    print(f"\n Baseado no que você disse, recomendo: {', '.join(recomendacoes)}")

    feedback = input("\nVocê gostou de algum desses filmes recomendados? Digite os nomes separados por vírgula ou pressione Enter para pular: ").strip()
    if feedback:
        novos_filmes = [f.strip() for f in feedback.split(",") if f.strip()]
        recommender.usuarios[user_id]["filmes"].update(novos_filmes)
        recommender.save_csv()
        print(" Preferências atualizadas com os filmes que você gostou!")

    return ""