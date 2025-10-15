import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from src.recommender import InteractiveRecommender

# === Caminhos fixos ===
APPROVED_FILE = r"D:\Dev\PyCharm Projects\SuggestAI\data\usuarios_filmes.csv"
REJECTED_FILE = r"D:\Dev\PyCharm Projects\SuggestAI\data\usuarios_rejeitados.csv"
MOVIES_FILE = r"D:\Dev\PyCharm Projects\SuggestAI\data\filmes.csv"


def evaluate_real_model(top_n=5):
    model = InteractiveRecommender(
        users_file=APPROVED_FILE,
        movies_file=MOVIES_FILE
    )

    approved_df = pd.read_csv(APPROVED_FILE)
    rejected_df = pd.read_csv(REJECTED_FILE)

    y_true, y_pred = [], []

    # Avalia por usuário
    for _, row in approved_df.iterrows():
        user_id = str(row["user_id"])
        user_movies = set(row.dropna().tolist()[2:])  # filmes aprovados
        if not user_movies:
            continue

        # divide filmes do usuário em treino e teste
        train_movies, test_movies = train_test_split(list(user_movies), test_size=0.4, random_state=42)

        # simula treino (o modelo aprende com os filmes de treino)
        model.users[user_id] = {"movies": train_movies}

        # rejeitados (negativos)
        rejected_movies = set()
        if int(user_id) in rejected_df["user_id"].values:
            rejected_movies = set(rejected_df[rejected_df["user_id"] == int(user_id)].dropna(axis=1).iloc[0, 2:].values)

        # recomendações com base no que ele aprendeu
        recs = set(model.get_recommendations(user_id, top_n=top_n))

        # filmes de teste são os verdadeiros positivos (1)
        for filme in test_movies:
            y_true.append(1)
            y_pred.append(1 if filme in recs else 0)

        # rejeitados são os verdadeiros negativos (0)
        for filme in rejected_movies:
            y_true.append(0)
            y_pred.append(1 if filme in recs else 0)

    cm = confusion_matrix(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print("=== Avaliação Realista (Treino/Teste por Filmes) ===")
    print(f"Total de amostras: {len(y_true)}")
    print("Matriz de Confusão:\n", cm)
    print(f"Precisão: {precision:.2f}, Recall: {recall:.2f}, F1-Score: {f1:.2f}")

    # --- Visualização ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.heatmap(cm, annot=True, fmt="d", cmap="Purples", ax=axes[0])
    axes[0].set_title("Matriz de Confusão (Modelo Real)")
    axes[0].set_xlabel("Predito")
    axes[0].set_ylabel("Verdadeiro")

    metrics_df = pd.DataFrame({
        "Métrica": ["Precisão", "Recall", "F1-Score"],
        "Valor": [precision, recall, f1]
    })
    sns.barplot(data=metrics_df, x="Métrica", y="Valor", palette="mako", ax=axes[1])
    axes[1].set_ylim(0, 1)
    axes[1].set_title("Métricas do Modelo")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    evaluate_real_model(top_n=5)
