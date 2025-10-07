from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat

def main():
    print("=== Suggest AI - Sistema de Recomendação Interativo ===\n")
    print("1 - Modo Manual: digite seus filmes favoritos e seus gêneros (até 7 filmes)")
    print("2 - Modo Chatbot: descreva o que gosta (ex: 'gosto de ação, evito comédia')\n")

    modo = input("Digite '1' para Manual ou '2' para Chat: ").strip()

    users_path = "D:/Dev/projetos vscode/SuggestAI/data/usuarios_filmes.csv"
    movies_path = "D:/Dev/projetos vscode/SuggestAI/data/filmes.csv"

    recommender = InteractiveRecommender(users_file=users_path, movies_file=movies_path)

    if modo == "1" or modo.lower() == "manual":
        nome = input("Digite seu nome: ").strip()
        print("\nFormato esperado (máximo de 7 filmes):")
        print("Ex: Matrix - acao, Titanic - drama, Avatar - ficcao\n")
        entrada = input("Digite seus filmes e gêneros: ").strip()

        if len(entrada.split(",")) > 7:
            print("Atenção: você inseriu mais de 7 filmes. Serão considerados apenas os 7 primeiros.")
            entrada = ",".join(entrada.split(",")[:7])

        salvar = input("Deseja salvar seus filmes na base de dados? [s/n]: ").strip().lower()
        if salvar == "s":
            try:
                uid = recommender.add_user_with_genres(nome, entrada)
                print("Seus filmes foram salvos com sucesso!")
                recs = recommender.get_recommendations(uid, top_n=3)
                if recs:
                    print(f"\nRecomendações pra você: {', '.join(recs)}")
                else:
                    print("\nNão encontrei recomendações suficientes. Tente adicionar mais filmes.")
            except ValueError as e:
                print(f"Erro: {e}")
        else:
            print("Você optou por não salvar seus filmes na base de dados.")

    elif modo == "2" or modo.lower() == "chat":
        while True:
            frase = input("\nDescreva o que você gosta para mais recomendações, ou digite 'sair' para encerrar: ").strip()
            if frase.lower() == "sair":
                break
            resp = recomendar_por_chat(frase, recommender, top_n=3)
            print(f"\n{resp}\n")
    else:
        print("Modo inválido. Rode de novo e escolha 1 ou 2.")


if __name__ == "__main__":
    main()
