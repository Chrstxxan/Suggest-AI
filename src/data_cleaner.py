import pandas as pd
import unicodedata
import os

# === Normalização do texto ===
def normalizar(texto):
    if not isinstance(texto, str):
        return texto
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    return texto

# === Limpeza da base de usuários ===
def limpar_usuario_filmes(csv_path):
    if not os.path.exists(csv_path):
        print(f"Arquivo {csv_path} não encontrado.")
        return

    df = pd.read_csv(csv_path)

    # garante que todas as colunas de filme existam até filme9
    for i in range(1, 10):
        col = f"filme{i}"
        if col not in df.columns:
            df[col] = ""

    # normaliza todos os filmes
    for col in df.columns:
        if "filme" in col:
            df[col] = df[col].apply(lambda x: normalizar(str(x)) if pd.notna(x) else "")
            df[col] = df[col].str.strip()

    # adiciona colunas de peso por gênero se não existirem
    generos = ["acao", "drama", "romance", "ficcao_cientifica", "terror", "comedia", "suspense"]
    for g in generos:
        col = f"peso_{g}"
        if col not in df.columns:
            df[col] = 1.0  # inicializa com peso neutro

    # salva de volta
    df.to_csv(csv_path, index=False)
    print(f"CSV de usuários limpo e salvo em {csv_path}")

# === Limpeza da base de filmes ===
def limpar_filmes(csv_path):
    if not os.path.exists(csv_path):
        print(f"Arquivo {csv_path} não encontrado.")
        return

    df = pd.read_csv(csv_path)

    # normaliza os nomes dos filmes e gêneros
    df["filme"] = df["filme"].apply(normalizar)
    df["genero"] = df["genero"].apply(normalizar)

    df.to_csv(csv_path, index=False)
    print(f"CSV de filmes limpo e salvo em {csv_path}")

# === Execução principal ===
if __name__ == "__main__":
    base_dir = "D:/Dev/projetos vscode/SuggestAI/data"
    limpar_usuario_filmes(os.path.join(base_dir, "usuarios_filmes.csv"))
    limpar_filmes(os.path.join(base_dir, "filmes.csv"))
