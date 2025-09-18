from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat

print("=== Suggest AI - Sistema de Recomendação Interativo ===\n")

print("Escolha o modo de entrada:")
print("1 - Manual: você digita os filmes que já gosta e seu gênero principal")
print("2 - Chat: você descreve o tipo de filme que gosta (ex: 'gosto de ação, evito comédia')")

modo = input("\nDigite '1' para Manual ou '2' para Chat: ").strip().lower()

if modo in ["1", "manual"]:
    modo = "manual"
elif modo in ["2", "chat"]:
    modo = "chat"
else:
    print("Modo inválido. Encerrando.")
    exit()

# Caminho absoluto para os arquivos
base_dir = "D:/Dev/projetos vscode/SuggestAI/data"
recommender = InteractiveRecommender(base_dir=base_dir)

if modo == "manual":
    nome = input("Digite seu nome: ").strip()

    print("\nFormato esperado:")
    print("• Separe cada filme por vírgula")
    print("• Use hífen para separar o nome do filme do gênero principal")
    print("Exemplo: Matrix - ação, Titanic - drama, Avatar 2 - ficção científica\n")

    entrada = input("Digite os filmes e gêneros separados por vírgula: ").strip()
    user_id = recommender.add_user_with_genres(nome, entrada)

    recomendacoes = recommender.get_recommendations(user_id, top_n=3)
    if recomendacoes:
        print(f"\nRecomendações para você: {', '.join(recomendacoes)}")
    else:
        print("\nNão encontrei recomendações suficientes. Tente adicionar mais filmes.")

else:  # modo chat
    while True:
        frase = input("\nEscreva o que você gosta ou quer evitar (ou 'sair' para encerrar): ").strip()
        if frase.lower() == "sair":
            break
        resposta = recomendar_por_chat(frase, recommender, top_n=3)
        if resposta:
            print(f"\n{resposta}")
