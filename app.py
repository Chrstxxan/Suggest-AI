from src.recommender import InteractiveRecommender

if __name__ == "__main__":
    recommender = InteractiveRecommender(r"D:\Dev\projetos vscode\SuggestAI\data\usuarios_filmes.csv")

    print("=== Suggest AI - Sistema de Recomendação Interativo ===")

    while True:
        nome = input("\nDigite seu nome (ou 'sair' para encerrar): ").strip()
        if nome.lower() == "sair":
            break

        filmes_input = input("Digite os filmes que você gosta, separados por vírgula ou ponto e vírgula: ")
        filmes_list = [f.strip() for f in filmes_input.replace(';', ',').split(',') if f.strip()]

        user_id = recommender.add_user_preferences(nome, filmes_list)

        top_n = int(input("Quantos filmes quer que eu recomende? "))
        tipo = input("Tipo de recomendação (simples/similaridade): ").strip().lower()

        if tipo == "similaridade":
            recs = recommender.recommend_by_similarity(user_id, top_n=top_n)
        else:
            recs = recommender.recommend(user_id, top_n=top_n)

        if recs:
            print(f"\n🎯 Recomendações para {nome}:")
            for i, filme in enumerate(recs, 1):
                print(f"{i}. {filme}")
        else:
            print("Não encontrei recomendações com base nos filmes informados.")

    print("\nSessão encerrada. As alterações foram salvas no CSV.")