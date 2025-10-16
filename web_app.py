from flask import Flask, render_template, request, redirect, url_for
from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat_web, registrar_rejeitados
import webbrowser
import threading

app = Flask(__name__)

# --- Carrega modelo e dados ---
recommender = InteractiveRecommender(
    users_file="data/usuarios_filmes.csv",
    movies_file="data/filmes.csv"
)

# --- Abre navegador automaticamente ---
def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

@app.route("/")
def index():
    return render_template("index.html")

# --- Modo Manual ---
@app.route("/manual", methods=["GET", "POST"])
def manual():
    if request.method == "POST":
        nome = request.form.get("nome")
        entrada = request.form.get("entrada")
        top_n = int(request.form.get("top_n", 5))
        salvar = request.form.get("salvar", "n").lower()

        try:
            if salvar == "s":
                # Salva usuário na base e recomenda
                user_id = recommender.add_user_with_genres(nome, entrada)
                recs = recommender.get_recommendations(user_id, top_n)
                return render_template("result.html", nome=nome, recs=recs, modo="manual", user_id=user_id, salvar=salvar)
            else:
                # Não salva nada, só gera recomendações temporárias
                user_id = "temp_manual"

                # Simula recomendações temporárias sem salvar o usuário
                try:
                    # Cria um usuário fake apenas na memória, sem escrever no CSV
                    temp_id = "temp_" + nome.replace(" ", "_").lower()
                    recommender.users[temp_id] = {"nome": nome, "movies": []}

                    # Extrai gêneros dos filmes digitados
                    generos_usuario = []
                    for par in entrada.split(","):
                        partes = par.strip().split("-")
                        if len(partes) == 2:
                            generos_usuario.append(partes[1].strip().lower())

                    # Filtra filmes compatíveis com esses gêneros
                    recs = [
                        f for f, g in recommender.movies.items()
                        if any(gen in g.lower() for gen in generos_usuario)
                    ][:top_n]

                except Exception as e:
                    recs = []
                    print(f"[manual temporário] Erro ao gerar recomendações: {e}")
                return render_template("result.html", nome=nome, recs=recs, modo="manual", user_id=user_id, salvar=salvar)

        except Exception as e:
            return render_template("manual.html", erro=f"Erro: {str(e)}")

    return render_template("manual.html")

# --- Modo Chatbot ---
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        frase = request.form.get("frase")
        nome = request.form.get("nome")
        top_n = int(request.form.get("top_n", 3))
        salvar = request.form.get("salvar", "n").lower()

        # Gera recomendações + user_id
        recs, user_id = recomendar_por_chat_web(
            frase=frase,
            nome=nome,
            recommender=recommender,
            top_n=top_n,
            quantos_por_rodada=top_n
        )

        # Se o usuário NÃO quiser salvar, marcaremos como temporário
        if salvar != "s":
            user_id = f"temp_{user_id}"

        return render_template(
            "result.html",
            nome=nome,
            recs=recs,
            modo="chat",
            user_id=user_id,
            salvar=salvar if salvar else "n"  # garante que o valor original persista
        )

    return render_template("chat.html")

# --- Feedback ---
@app.route("/feedback", methods=["POST"])
def feedback():
    user_id = request.form.get("user_id")
    nome = request.form.get("nome", "Usuário")
    salvar = request.form.get("salvar", "n").lower()
    filmes_rejeitados = []

    print(f"[debug feedback] user_id={user_id}, salvar={salvar}")

    # Percorre feedbacks
    for key, fb in request.form.items():
        if key in ["user_id", "nome", "salvar"]:
            continue
        if key.startswith("filme_"):
            filme = key.replace("filme_", "")
            if fb == "n":
                filmes_rejeitados.append(filme)

            # Salva nas notas apenas se o user foi salvo na base
            if salvar == "s" and user_id and not user_id.startswith("temp_"):
                try:
                    recommender.update_weights(user_id, filme, fb)
                    print(f"[feedback] Atualizado peso para {filme}: {fb}")
                except Exception as e:
                    print(f"[feedback] Erro ao atualizar {filme}: {e}")

    # Salva rejeitados apenas se o user for da base
    if salvar == "s" and filmes_rejeitados:
        try:
            registrar_rejeitados(user_id, nome, filmes_rejeitados)
            print(f"[feedback] Rejeitados salvos: {filmes_rejeitados}")
        except Exception as e:
            print(f"[feedback] Erro ao registrar rejeitados: {e}")
    else:
        print(f"[feedback] Nada salvo (salvar={salvar}, filmes_rejeitados={filmes_rejeitados})")

    return redirect(url_for("index"))

if __name__ == "__main__":
    threading.Timer(1.0, abrir_navegador).start()
    app.run(debug=True, use_reloader=False)
