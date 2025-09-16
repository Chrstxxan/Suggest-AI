import pandas as pd
import unicodedata
import os

# normalizacao do texto para a base ficar limpa
def normalizar(texto):
    if not isinstance(texto, str):
        return texto
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto

# limpa o csv normalizando os nomes dos filmes
def limpar_usuario_filmes(csv_path):
    if not os.path.exists(csv_path):
        print(f"Arquivo {csv_path} não encontrado.")
        return

    df = pd.read_csv(csv_path)

    # normaliza todos os filmes
    for col in df.columns:
        if "filme" in col:
            df[col] = df[col].apply(lambda x: normalizar(str(x)) if pd.notna(x) else "")

    for i in range(1, 10):
        col = f"filme{i}"
        df[col] = df[col].str.strip()

    # salva o CSV limpo
    df.to_csv(csv_path, index=False)
    print(f"CSV de usuários limpo e salvo em {csv_path}")

def limpar_filmes(csv_path):
    """Normaliza os nomes dos filmes e gêneros no CSV de filmes."""
    if not os.path.exists(csv_path):
        print(f"Arquivo {csv_path} não encontrado.")
        return

    df = pd.read_csv(csv_path)
    df["filme"] = df["filme"].apply(normalizar)
    df["genero"] = df["genero"].apply(normalizar)
    df.to_csv(csv_path, index=False)
    print(f"CSV de filmes limpo e salvo em {csv_path}")

if __name__ == "__main__":
    base_dir = "D:/Dev/projetos vscode/SuggestAI/data"
    limpar_usuario_filmes(os.path.join(base_dir, "usuarios_filmes.csv"))
    limpar_filmes(os.path.join(base_dir, "filmes.csv"))
