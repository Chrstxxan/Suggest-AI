import matplotlib
#matplotlib.use("Agg")  # usa backend não interativo (sem jupyter)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.model_selection import train_test_split

# ----------------- Config -----------------
PATH_USUARIOS = r"D:/Dev/projetos vscode/SuggestAI/data/usuarios_filmes.csv"
PATH_FILMES = r"D:/Dev/projetos vscode/SuggestAI/data/filmes.csv"

# ----------------- Leitura dos CSVs -----------------
df_usuarios = pd.read_csv(PATH_USUARIOS)
df_filmes = pd.read_csv(PATH_FILMES)

df_usuarios.columns = [c.strip() for c in df_usuarios.columns]
df_filmes.columns = [c.strip() for c in df_filmes.columns]

# ----------------- Colunas de gêneros -----------------
generos_cols = ['acao','comedia','drama','ficcao cientifica','romance','terror','suspense']

# ----------------- Criar estrutura de usuários -----------------
usuarios = {}
for _, row in df_usuarios.iterrows():
    filmes = [f for f in row[['filme1','filme2','filme3','filme4','filme5','filme6','filme7']] if pd.notna(f) and f.strip() != '']
    genero_scores = row[generos_cols].fillna(0).astype(float).to_dict()
    usuarios[row['user_id']] = {"movies": filmes, **genero_scores}

# ----------------- Divisão treino/teste -----------------
for uid, info in usuarios.items():
    filmes = info["movies"]
    if len(filmes) <= 1:
        usuarios[uid]["train"] = filmes
        usuarios[uid]["teste"] = []
    else:
        train, teste = train_test_split(filmes, test_size=0.4, random_state=42)
        usuarios[uid]["train"] = train
        usuarios[uid]["teste"] = teste

# ----------------- Classe Recomendador -----------------
class InteractiveRecommender:
    def __init__(self, usuarios, filmes_df):
        self.users = usuarios
        self.filmes_df = filmes_df

    def get_recommendations_inteligente(self, user_id, top_n=3):
        filmes_vistos = set(self.users[user_id]["train"])
        perfil_genero = np.array([self.users[user_id].get(g,0) for g in generos_cols], dtype=float)
        all_films = list(self.filmes_df['filme'].values)

        scores = {}
        for filme in all_films:
            if filme in filmes_vistos:
                continue
            genero = self.filmes_df.loc[self.filmes_df['filme']==filme,'genero'].values[0]
            vec_genero = np.array([1 if g==genero else 0 for g in generos_cols], dtype=float)
            score = np.dot(perfil_genero, vec_genero)
            scores[filme] = score

        recs = sorted(scores, key=lambda x: scores[x], reverse=True)[:top_n]
        return recs

    def recommend_by_knn(self, user_id, top_n=3):
        return self.get_recommendations_inteligente(user_id, top_n)

    def recommend_by_weights(self, user_id, top_n=3):
        return self.get_recommendations_inteligente(user_id, top_n)

    def recommend_by_matrix_factorization(self, user_id, top_n=3):
        return self.get_recommendations_inteligente(user_id, top_n)

# ----------------- Instancia o recomendador -----------------
recommender = InteractiveRecommender(usuarios, df_filmes)

# ----------------- Função de avaliação combinando todos os métodos -----------------
def avaliar_recomendador_combinado(recommender, top_n=3):
    y_true, y_pred = [], []

    for uid, dados in usuarios.items():
        if not dados["teste"]:
            continue

        recs_combined = set()
        recs_combined.update(recommender.get_recommendations_inteligente(uid, top_n=top_n))
        recs_combined.update(recommender.recommend_by_knn(uid, top_n=top_n))
        recs_combined.update(recommender.recommend_by_weights(uid, top_n=top_n))
        recs_combined.update(recommender.recommend_by_matrix_factorization(uid, top_n=top_n))

        for filme in dados["teste"]:
            y_true.append(1)
            y_pred.append(1 if filme in recs_combined else 0)

        for filme in recs_combined:
            if filme not in dados["teste"]:
                y_true.append(0)
                y_pred.append(1)

    cm = confusion_matrix(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    return y_true, y_pred, cm, prec, rec, f1

# ----------------- Avaliação -----------------
y_true, y_pred, cm, prec, rec, f1 = avaliar_recomendador_combinado(recommender)

print("\n=== Avaliação Combinando Todos os Métodos ===")
print("Matriz de Confusão:\n", cm)
print(f"Precisão: {prec:.2f}")
print(f"Recall: {rec:.2f}")
print(f"F1-Score: {f1:.2f}")

# ----------------- Gráficos -----------------

# 1️⃣ Matriz de confusão
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.title("Matriz de Confusão")
plt.xlabel("Previsto")
plt.ylabel("Real")
plt.tight_layout()
plt.show()

# 2️⃣ Gráfico de comparação das métricas
metrics = {"Precisão": prec, "Recall": rec, "F1-Score": f1}
plt.figure(figsize=(6,5))
sns.barplot(x=list(metrics.keys()), y=list(metrics.values()), palette="mako")
plt.ylim(0,1)
plt.title("Comparativo de Métricas")
plt.ylabel("Valor")
plt.tight_layout()
plt.show()

# 3️⃣ Curva ROC (só pra visual)
fpr, tpr, _ = roc_curve(y_true, y_pred)
roc_auc = auc(fpr, tpr)
plt.figure(figsize=(6,5))
plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (área = {roc_auc:.2f})")
plt.plot([0,1], [0,1], color="navy", lw=2, linestyle="--")
plt.xlabel("Falsos Positivos")
plt.ylabel("Verdadeiros Positivos")
plt.title("Curva ROC do Recomendador")
plt.legend(loc="lower right")
plt.tight_layout()
plt.show()
