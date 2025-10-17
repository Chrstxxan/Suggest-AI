from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat

def main():
    print("=== Suggest AI - Sistema de Recomendação Interativo ===\n")
    print("1 - Modo Manual: digite seus filmes favoritos e seus gêneros (até 7 filmes)")
    print("2 - Modo Chatbot: descreva o que gosta (ex: 'gosto de ação, evito comédia')\n")

    modo = input("Digite '1' para Manual ou '2' para Chat: ").strip()

    users_path = "D:/Dev/PyCharm Projects/SuggestAI/data/usuarios_filmes.csv"
    movies_path = "D:/Dev/PyCharm Projects/SuggestAI/data/filmes.csv"

    recommender = InteractiveRecommender(users_file=users_path, movies_file=movies_path)

    if modo == "1" or modo.lower() == "manual":
        from src.chatbot import registrar_rejeitados  # certifique-se de ter a função atualizada
        nome = input("Digite seu nome: ").strip()
        print("\nFormato esperado (máximo de 7 filmes):")
        print("Ex: Matrix - acao, Titanic - drama, Avatar - ficcao\n")
        entrada = input("Digite seus filmes e gêneros: ").strip()

        if len(entrada.split(",")) > 7:
            print("Atenção: você inseriu mais de 7 filmes. Serão considerados apenas os 7 primeiros.")
            entrada = ",".join(entrada.split(",")[:7])

        while True:
            try:
                top_n = int(input("\nQuantas recomendações você quer receber? (3 a 7): ").strip())
                if 3 <= top_n <= 7:
                    break
                else:
                    print("Escolha um número entre 3 e 7.")
            except ValueError:
                print("Entrada inválida! Digite um número entre 3 e 7.")

        salvar = input("\nDeseja salvar seus filmes na base de dados? Digite 's' para sim e 'n' para não: ").strip().lower()
        filmes_usuario = [f.split("-")[0].strip() for f in entrada.split(",")]

        if salvar == "s":
            try:
                uid = recommender.add_user_with_genres(nome, entrada)
                print("Seus filmes foram salvos com sucesso! Obrigado.")

                recs = recommender.get_recommendations(uid, top_n=top_n)
                if recs:
                    if len(recs) < top_n:
                        print(f"\nAtenção: foram encontradas apenas {len(recs)} recomendações disponíveis.")
                    print(f"\nRecomendações pra você: {', '.join(recs)}")

                    filmes_rejeitados = []
                    # ✅ Coleta feedback e registra rejeitados
                    for f in recs:
                        while True:
                            fb = input(
                                f"Você gostou do filme '{f}'? digite 's' para sim ou 'n' para não: ").strip().lower()
                            if fb in ["s", "n"]:
                                break
                            print("Entrada inválida! Digite 's' para sim ou 'n' para não.")
                        recommender.update_weights(uid, f, fb)
                        if fb == "n":
                            filmes_rejeitados.append(f)

                    if filmes_rejeitados:
                        registrar_rejeitados(uid, nome, filmes_rejeitados)

                else:
                    print("\nNão encontrei recomendações suficientes. Tente adicionar mais filmes.")
            except ValueError as e:
                print(f"Erro: {e}")
        else:
            print("Você optou por não salvar seus filmes na base de dados. Obrigado.")

    elif modo == "2" or modo.lower() == "chat":
        primeira_rodada = True
        while True:
            if primeira_rodada:
                frase = input("\nDescreva o que você gosta para obter recomendações, ou digite 'sair' para encerrar: ").strip()
                primeira_rodada = False
            else:
                frase = input("\nDescreva o que você gosta para obter mais recomendações, ou digite 'sair' para encerrar: ").strip()

            if frase.lower() == "sair":
                break

            resp = recomendar_por_chat(frase, recommender, top_n=3)
            print(f"\n{resp}\n")

    else:
        print("Modo inválido. Rode de novo e escolha 1 ou 2.")

if __name__ == "__main__":
    main()