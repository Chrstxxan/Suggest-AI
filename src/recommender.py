import pandas as pd
import os

class InteractiveRecommender:
    def __init__(self, base_dir="D:/Dev/projetos vscode/SuggestAI/data"):
        self.base_dir = base_dir
        self.csv_path = os.path.join(base_dir, "usuarios_filmes.csv")
        self.filmes_path = os.path.join(base_dir, "filmes.csv")
        self.usuarios = []
        self.load_csv(self.csv_path)

    def load_csv(self, path):
        if os.path.exists(path):
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                filmes = [row[f"filme{i}"] for i in range(1, 10) if pd.notna(row.get(f"filme{i}"))]
                self.usuarios.append({
                    "user_id": str(row["user_id"]),
                    "nome": row["nome"],
                    "filmes": filmes
                })

    def add_user_with_genres(self, nome, entrada):
        filmes_do_usuario = []
        generos_novos = {}

        for item in entrada.split(","):
            if "-" in item:
                nome_filme, genero = item.split("-", 1)
                nome_filme = nome_filme.strip()
                genero = genero.strip().lower()
                filmes_do_usuario.append(nome_filme)
                generos_novos[nome_filme] = [genero]

        user_id = str(len(self.usuarios) + 1)
        self.usuarios.append({
            "user_id": user_id,
            "nome": nome,
            "filmes": filmes_do_usuario
        })

        self.salvar_csv(user_id, nome, filmes_do_usuario)
        self.atualizar_filmes_csv(generos_novos)

        return user_id

    def salvar_csv(self, user_id, nome, filmes):
        linha = {"user_id": user_id, "nome": nome}
        for i, filme in enumerate(filmes[:9]):
            linha[f"filme{i+1}"] = filme

        df = pd.DataFrame([linha])
        if os.path.exists(self.csv_path):
            df.to_csv(self.csv_path, mode="a", header=False, index=False)
        else:
            df.to_csv(self.csv_path, index=False)

    def atualizar_filmes_csv(self, novos_filmes):
        if os.path.exists(self.filmes_path):
            df = pd.read_csv(self.filmes_path)
        else:
            df = pd.DataFrame(columns=["filme", "genero"])

        filmes_existentes = set(df["filme"].str.lower())
        novos = []

        for filme, generos in novos_filmes.items():
            if filme.lower() not in filmes_existentes:
                novos.append({"filme": filme, "genero": generos[0]})

        if novos:
            df_novos = pd.DataFrame(novos)
            df = pd.concat([df, df_novos], ignore_index=True)
            df.to_csv(self.filmes_path, index=False)

    def recommend_by_cluster(self, user_id):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario:
            return []

        filmes_usuario = set(usuario["filmes"])
        recomendacoes = set()

        for outro in self.usuarios:
            if outro["user_id"] == user_id:
                continue
            filmes_outro = set(outro["filmes"])
            intersecao = filmes_usuario & filmes_outro
            if intersecao:
                recomendacoes.update(filmes_outro - filmes_usuario)

        return list(recomendacoes)[:5]

    def recommend_by_user_similarity(self, user_id):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario or not os.path.exists(self.filmes_path):
            return []

        df = pd.read_csv(self.filmes_path)
        generos_usuario = set()

        for filme in usuario["filmes"]:
            linha = df[df["filme"].str.lower() == filme.lower()]
            if not linha.empty:
                generos_usuario.add(linha.iloc[0]["genero"])

        candidatos = []
        for outro in self.usuarios:
            if outro["user_id"] == user_id:
                continue
            generos_outro = set()
            for filme in outro["filmes"]:
                linha = df[df["filme"].str.lower() == filme.lower()]
                if not linha.empty:
                    generos_outro.add(linha.iloc[0]["genero"])
            if generos_usuario & generos_outro:
                candidatos.extend([f for f in outro["filmes"] if f not in usuario["filmes"]])

        return list(pd.Series(candidatos).value_counts().index[:5])

    def recommend_by_genre_similarity(self, user_id):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario or not os.path.exists(self.filmes_path):
            return []

        df = pd.read_csv(self.filmes_path)
        generos_usuario = set()

        for filme in usuario["filmes"]:
            linha = df[df["filme"].str.lower() == filme.lower()]
            if not linha.empty:
                generos_usuario.add(linha.iloc[0]["genero"])

        pontuacao = {}
        for _, row in df.iterrows():
            filme = row["filme"]
            if filme in usuario["filmes"]:
                continue
            genero_filme = row["genero"]
            if genero_filme in generos_usuario:
                pontuacao[filme] = pontuacao.get(filme, 0) + 1

        recomendados = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)
        return [filme for filme, _ in recomendados[:5]]

    def recommend(self, user_id):
        todos_filmes = []
        for u in self.usuarios:
            todos_filmes.extend(u["filmes"])
        mais_comuns = pd.Series(todos_filmes).value_counts()
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario:
            return []
        return [f for f in mais_comuns.index if f not in usuario["filmes"]][:5]

    def get_recommendations(self, user_id):
        for metodo in [
            self.recommend_by_cluster,
            self.recommend_by_user_similarity,
            self.recommend_by_genre_similarity,
            self.recommend
        ]:
            recomendacoes = metodo(user_id)
            if recomendacoes:
                return recomendacoes
        return []