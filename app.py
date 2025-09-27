from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat

def main():
    print("=== Suggest AI - Sistema de Recomendação Interativo ===\n")
    print("1 - Manual: você digita os filmes que já gosta e seu gênero principal")
    print("2 - Chat: descreva o que gosta (ex: 'gosto de ação, evito comédia')\n")

    modo = input("Digite '1' para Manual ou '2' para Chat: ").strip()

    users_path = "D:/Dev/projetos vscode/SuggestAI/data/usuarios_filmes.csv"
    movies_path = "D:/Dev/projetos vscode/SuggestAI/data/filmes.csv"

    recommender = InteractiveRecommender(users_file=users_path, movies_file=movies_path)

    if modo == "1" or modo.lower() == "manual":
        nome = input("Digite seu nome: ").strip()
        print("\nFormato esperado:")
        print("Ex: Matrix - acao, Titanic - drama, Avatar - ficcao\n")
        entrada = input("Digite os filmes e gêneros: ").strip()
        try:
            uid = recommender.add_user_with_genres(nome, entrada)
        except ValueError as e:
            print(f"Erro: {e}")
            return
        recs = recommender.get_recommendations(uid, top_n=3)
        if recs:
            print(f"\nRecomendações pra você: {', '.join(recs)}")
        else:
            print("\nNão encontrei recomendações suficientes. Tenta adicionar mais filmes.")
    elif modo == "2" or modo.lower() == "chat":
        while True:
            frase = input("\nDescreva o que você gosta (ou digite 'sair'): ").strip()
            if frase.lower() == "sair":
                break
            resp = recomendar_por_chat(frase, recommender, top_n=3)
            print(f"\n{resp}\n")
    else:
        print("Modo inválido. Rode de novo e escolha 1 ou 2.")

if __name__ == "__main__":
    main()
