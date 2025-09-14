from src.recommender import InteractiveRecommender

print("=== Suggest AI - Sistema de Recomendação Interativo ===")

recommender = InteractiveRecommender(r"D:\Dev\projetos vscode\SuggestAI\data\usuarios_filmes.csv")

while True:
    nome = input("\nDigite seu nome (ou 'sair' para encerrar): ").strip()
    if nome.lower() == "sair":
        break

    filmes_input = input("Digite os filmes que você gosta, separados por vírgula ou ponto e vírgula: ")
    filmes = [f.strip() for f in filmes_input.replace(";", ",").split(",") if f.strip()]
    qtd = int(input("Quantos filmes quer que eu recomende? "))
    tipo = input("Tipo de recomendação (simples/similaridade/cluster): ").strip().lower()

    user_id = recommender.add_user_preferences(nome, filmes)

    if tipo == "simples":
        recomendacoes = recommender.recommend(user_id, qtd)
    elif tipo == "similaridade":
        recomendacoes = recommender.recommend_by_similarity(user_id, qtd)
    elif tipo == "cluster":
        recomendacoes = recommender.recommend_by_cluster(user_id, qtd)
    else:
        print("Tipo inválido. Usando recomendação simples.")
        recomendacoes = recommender.recommend(user_id, qtd)

    print(f"\n🎯 Recomendações para {nome}:")
    for i, filme in enumerate(recomendacoes, 1):
        print(f"{i}. {filme}")