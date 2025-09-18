import pandas as pd
import unicodedata

# Função para normalizar nomes de colunas
def normalizar(col):
    col = col.strip().lower()
    col = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8')
    col = col.replace(" ", "_")
    return col

# Carrega o CSV
df = pd.read_csv("D:/Dev/projetos vscode/SuggestAI/data/usuarios_filmes.csv")

# Cria um mapeamento de colunas normalizadas
col_map = {}
for col in df.columns:
    norm = normalizar(col)
    if norm in col_map:
        col_map[norm].append(col)
    else:
        col_map[norm] = [col]

# Mescla colunas duplicadas
df_limpo = pd.DataFrame()
for norm, cols in col_map.items():
    if len(cols) == 1:
        df_limpo[cols[0]] = df[cols[0]]
    else:
        # Soma os valores se forem numéricos, ou mantém o primeiro não nulo
        base = df[cols[0]].copy()
        for col in cols[1:]:
            if pd.api.types.is_numeric_dtype(df[col]):
                base = base.fillna(0) + df[col].fillna(0)
            else:
                base = base.combine_first(df[col])
        df_limpo[cols[0]] = base

# Remove colunas completamente vazias
df_limpo.dropna(axis=1, how="all", inplace=True)

# Salva o CSV limpo
df_limpo.to_csv("usuarios_filmes_corrigido.csv", index=False)