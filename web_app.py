from flask import Flask, render_template, request, redirect, url_for
from src.recommender import InteractiveRecommender
from src.chatbot import recomendar_por_chat_web
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

        # Cria usuário temporário e obtém recomendações
        try:
            user_id = recommender.add_user_with_genres(nome, entrada)
            recs = recommender.get_recommendations(user_id, top_n)
            return render_template("result.html", nome=nome, recs=recs, modo="manual", user_id=user_id)
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

        # chama a função web do chatbot
        recs = recomendar_por_chat_web(
            frase=frase,
            nome=nome,
            recommender=recommender,
            top_n=top_n,
            quantos_por_rodada=top_n
        )

        return render_template("result.html", nome=nome, recs=recs, modo="chat", user_id=None)

    return render_template("chat.html")

# --- Feedback ---
@app.route("/feedback", methods=["POST"])
def feedback():
    user_id = request.form.get("user_id")
    if user_id:  # só atualiza se o usuário foi salvo
        for key, fb in request.form.items():
            if key.startswith("filme_"):
                filme = key.replace("filme_", "")
                recommender.update_weights(user_id, filme, fb)
    # se não houver user_id (usuário temporário), não faz nada
    return redirect(url_for("index"))

if __name__ == "__main__":
    threading.Timer(1.0, abrir_navegador).start()
    app.run(debug=True, use_reloader=False)
