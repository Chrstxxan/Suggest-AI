import pandas as pd
from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat

print("=== Suggest AI - Sistema de Recomendação Interativo ===\n")

print("Escolha o modo de entrada:")
print("1 - Manual: você digita os filmes que já gosta e seus gêneros")
print("2 - Chat: você descreve o tipo de filme que gosta (ex: 'gosto de ação, evito comédia')")

modo = input("\nDigite '1' para Manual ou '2' para Chat: ").strip().lower()

if modo in ["1", "manual"]:
    modo = "manual"
elif modo in ["2", "chat"]:
    modo = "chat"
else:
    print("Modo inválido. Encerrando.")
    exit()

# Caminho absoluto para o arquivo de usuários
csv_path = "D:/Dev/projetos vscode/SuggestAI/data/usuarios_filmes.csv"
recommender = InteractiveRecommender(csv_path=csv_path)

if modo == "manual":
    nome = input("Digite seu nome: ").strip()

    print("\nFormato esperado:")
    print("• Separe cada filme por vírgula")
    print("• Use hífen para separar o nome do filme dos gêneros")
    print("• Use ponto e vírgula para separar múltiplos gêneros")
    print("Exemplo: Matrix - ação;ficção científica, Titanic - romance;drama\n")

    entrada = input("Digite os filmes e gêneros separados por vírgula: ").strip()

    # Validação simples para evitar erro de separação
    if "," not in entrada:
        print("\nOps... Parece que você não separou os filmes por vírgula. Tente novamente usando o formato correto.")
        exit()

    user_id = recommender.add_user_with_genres(nome, entrada)

    recomendacoes = recommender.recommend_by_cluster(user_id)
    if not recomendacoes:
        recomendacoes = recommender.recommend_by_similarity(user_id)
    if not recomendacoes:
        recomendacoes = recommender.recommend(user_id)

    print(f"\n Recomendações para você: {', '.join(recomendacoes)}")

else:
    while True:
        frase = input("\n Escreva o que você gosta ou quer evitar (ou 'sair' para encerrar): ").strip()
        if frase.lower() == "sair":
            break
        resposta = recomendar_por_chat(frase, recommender)
        if resposta:
            print(f"\n{resposta}")