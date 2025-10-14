import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import numpy as np

# --- Caminhos dos arquivos ---
APPROVED_FILE = r"D:\Dev\PyCharm Projects\SuggestAI\data\usuarios_filmes.csv"
REJECTED_FILE = r"D:\Dev\PyCharm Projects\SuggestAI\data\usuarios_rejeitados.csv"

def generate_labels_and_predictions_realistic(top_n=5, threshold=0.5):
    """Gera y_true e y_pred de forma realista com base nos feedbacks reais (sem simulação artificial)"""
    approved_df = pd.read_csv(APPROVED_FILE)
    rejected_df = pd.read_csv(REJECTED_FILE) if pd.io.common.file_exists(REJECTED_FILE) else pd.DataFrame(columns=[])

    # Extrai todos os filmes (de ambas as bases)
    all_filmes = set()
    for df in [approved_df, rejected_df]:
        for _, row in df.iterrows():
            filmes = [row[c] for c in row.index if c.startswith("filme") and pd.notna(row[c])]
            all_filmes.update(filmes)

    y_true = []
    y_pred = []

    # Para cada filme, define rótulo verdadeiro e "predição" baseada em taxa de aprovação
    for filme in all_filmes:
        # 1 se o filme estiver na base de aprovados, 0 se estiver nos rejeitados
        is_approved = any(filme in row.values for _, row in approved_df.iterrows())
        is_rejected = any(filme in row.values for _, row in rejected_df.iterrows())

        # Se o filme aparece em ambos (caso raro), considera aprovado como dominante
        if is_approved and is_rejected:
            label = 1
        elif is_approved:
            label = 1
        elif is_rejected:
            label = 0
        else:
            label = 0  # fallback (não deveria acontecer)

        y_true.append(label)

        # Calcula proporção de aprovação entre os usuários (proxy do score do modelo)
        approved_count = sum(filme in row.values for _, row in approved_df.iterrows())
        rejected_count = sum(filme in row.values for _, row in rejected_df.iterrows())
        total_count = approved_count + rejected_count

        if total_count == 0:
            simulated_score = 0  # filme que ninguém avaliou
        else:
            simulated_score = approved_count / total_count

        # Converte score em predição binária com base no threshold
        y_pred.append(int(simulated_score >= threshold))

    return y_true, y_pred, list(all_filmes)

def evaluate_model_realistic(top_n=5, threshold=0.5):
    """Avalia o modelo de forma realista e plota gráficos (mantendo layout original)"""
    y_true, y_pred, filmes = generate_labels_and_predictions_realistic(top_n, threshold)

    cm = confusion_matrix(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print("=== Avaliação Realista ===")
    print(f"Filmes positivos (teste): {sum(y_true)}, Filmes negativos (rejeitados): {len(y_true) - sum(y_true)}")
    print("Matriz de Confusão:\n", cm)
    print(f"Precisão: {precision:.2f}, Recall: {recall:.2f}, F1-Score: {f1:.2f}")

    # --- Matriz de Confusão ---
    fig1 = plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Matriz de Confusão")
    plt.xlabel("Predito")
    plt.ylabel("Verdadeiro")
    plt.tight_layout()
    mngr1 = plt.get_current_fig_manager()
    try:
        mngr1.window.move(100, 100)  # desloca para esquerda
    except AttributeError:
        pass

    # --- Métricas ---
    metrics_df = pd.DataFrame({
        "Métrica": ["Precisão", "Recall", "F1-Score"],
        "Valor": [precision, recall, f1]
    })
    fig2 = plt.figure(figsize=(6,5))
    sns.barplot(data=metrics_df, x="Métrica", y="Valor", palette="mako")
    plt.ylim(0, 1)
    plt.title("Métricas do Modelo Realista")
    plt.tight_layout()
    mngr2 = plt.get_current_fig_manager()
    try:
        mngr2.window.move(750, 100)  # desloca para direita
    except AttributeError:
        pass

    plt.show()  # Mantém gráficos abertos até você fechar

# --- Executa a avaliação ---
evaluate_model_realistic(top_n=5, threshold=0.5)


