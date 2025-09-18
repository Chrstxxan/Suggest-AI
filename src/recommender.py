import pandas as pd
import os
from collections import defaultdict

class InteractiveRecommender:
    def __init__(self, base_dir="D:/Dev/projetos vscode/SuggestAI/data"):
        self.base_dir = base_dir
        self.csv_path = os.path.join(base_dir, "usuarios_filmes.csv")
        self.filmes_path = os.path.join(base_dir, "filmes.csv")
        self.generos = self.carregar_generos()
        self.usuarios = []
        self.load_csv(self.csv_path)
        self.user_index = {}  # map user_id → índice na lista para KNN/MF
        self.build_user_index()

    def carregar_generos(self):
        df = pd.read_csv(os.path.join(self.base_dir, "filmes.csv"))
        return sorted(df["genero"].unique())

    def load_csv(self, path):
        if os.path.exists(path):
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                filmes = [row[f"filme{i}"] for i in range(1, 10) if pd.notna(row.get(f"filme{i}")) and row.get(f"filme{i}") != ""]
                pesos = {g: row.get(g, 0.0) for g in self.generos}
                self.usuarios.append({
                    "user_id": str(row["user_id"]),
                    "nome": row["nome"],
                    "filmes": filmes,
                    "pesos": pesos
                })

    def build_user_index(self):
        self.user_index = {u["user_id"]: idx for idx, u in enumerate(self.usuarios)}

    def add_user_with_genres(self, nome, entrada):
        filmes_do_usuario = []
        generos_novos = {}

        for item in entrada.split(","):
            if "-" in item:
                nome_filme, genero = item.split("-", 1)
                nome_filme = nome_filme.strip()
                genero = genero.strip().lower()
                filmes_do_usuario.append(nome_filme)
                generos_novos[nome_filme] = genero

        if len(filmes_do_usuario) < 3:
            raise ValueError("O usuário deve ter pelo menos 3 filmes.")

        user_id = str(len(self.usuarios) + 1)
        pesos = {g: (1.0 if g in generos_novos.values() else 0.0) for g in self.generos}

        self.usuarios.append({
            "user_id": user_id,
            "nome": nome,
            "filmes": filmes_do_usuario,
            "pesos": pesos
        })
        self.user_index[user_id] = len(self.usuarios) - 1

        self.salvar_csv(user_id, nome, filmes_do_usuario, pesos)
        self.atualizar_filmes_csv(generos_novos)
        return user_id

    def salvar_csv(self, user_id, nome, filmes, pesos):
        # monta o dicionário da nova linha
        linha = {"user_id": user_id, "nome": nome}
        for i, filme in enumerate(filmes[:9]):  # até 9 filmes
            linha[f"filme{i+1}"] = filme

        # se o arquivo existe, usamos as colunas dele
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)

            # garante que só usa colunas que já existem
            for col in df.columns:
                if col in pesos:
                    linha[col] = pesos[col]

            # adiciona a nova linha ao dataframe
            df = pd.concat([df, pd.DataFrame([linha])], ignore_index=True)
        else:
            # se não existe, cria com filmes + pesos que recebemos
            linha.update(pesos)
            df = pd.DataFrame([linha])

        # salva o CSV sem duplicar cabeçalhos
        df.to_csv(self.csv_path, index=False)


    def atualizar_filmes_csv(self, novos_filmes):
        if os.path.exists(self.filmes_path):
            df = pd.read_csv(self.filmes_path)
        else:
            df = pd.DataFrame(columns=["filme", "genero"])

        filmes_existentes = set(df["filme"].str.lower())
        novos = []
        for filme, genero in novos_filmes.items():
            if filme.lower() not in filmes_existentes:
                novos.append({"filme": filme, "genero": genero})

        if novos:
            df_novos = pd.DataFrame(novos)
            df = pd.concat([df, df_novos], ignore_index=True)
            df.to_csv(self.filmes_path, index=False)

    def recommend_by_weights(self, user_id, top_n=3):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario or not os.path.exists(self.filmes_path):
            return []

        df_filmes = pd.read_csv(self.filmes_path)
        recomendacoes = {}
        for _, row in df_filmes.iterrows():
            filme = row["filme"]
            genero = row["genero"]
            if filme in usuario["filmes"]:
                continue
            score = usuario["pesos"].get(genero, 0.0)
            if score > 0:
                recomendacoes[filme] = score

        recomendados = sorted(recomendacoes.items(), key=lambda x: x[1], reverse=True)
        return [f for f, _ in recomendados[:top_n]]

    def recommend_by_user_similarity(self, user_id, top_n=3):
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

        return list(pd.Series(candidatos).value_counts().index[:top_n])

    def recommend_by_cluster(self, user_id, top_n=3):
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

        return list(recomendacoes)[:top_n]

    def recommend_by_popularity(self, user_id, top_n=3):
        todos_filmes = []
        for u in self.usuarios:
            todos_filmes.extend(u["filmes"])
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario:
            return []
        mais_comuns = pd.Series(todos_filmes).value_counts()
        return [f for f in mais_comuns.index if f not in usuario["filmes"]][:top_n]

    def update_weights(self, user_id, filme, feedback):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario:
            return
        df_filmes = pd.read_csv(self.filmes_path)
        linha = df_filmes[df_filmes["filme"].str.lower() == filme.lower()]
        if linha.empty:
            return
        genero = linha.iloc[0]["genero"]
        if feedback.lower() == "s":
            usuario["pesos"][genero] += 0.1
        else:
            usuario["pesos"][genero] = max(0.0, usuario["pesos"][genero] - 0.1)
        self._atualizar_csv_pesos(usuario)

    def _atualizar_csv_pesos(self, usuario):
        df = pd.read_csv(self.csv_path)
        idx = df.index[df["user_id"] == int(usuario["user_id"])]
        if not idx.empty:
            for g, p in usuario["pesos"].items():
                df.at[idx[0], g] = p
            df.to_csv(self.csv_path, index=False)

    def recommend_by_knn(self, user_id, top_n=3):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario:
            return []

        filmes_usuario = set(usuario["filmes"])
        similar_scores = []
        for outro in self.usuarios:
            if outro["user_id"] == user_id:
                continue
            filmes_outro = set(outro["filmes"])
            score = len(filmes_usuario & filmes_outro)
            if score > 0:
                similar_scores.append((score, outro["user_id"]))

        similar_scores.sort(reverse=True)
        recomendacoes = []
        for _, uid in similar_scores:
            outro = next(u for u in self.usuarios if u["user_id"] == uid)
            recomendacoes.extend([f for f in outro["filmes"] if f not in filmes_usuario])

        return list(pd.Series(recomendacoes).value_counts().index[:top_n])

    def recommend_by_matrix_factorization(self, user_id, top_n=3):
        usuario = next((u for u in self.usuarios if u["user_id"] == user_id), None)
        if not usuario:
            return []

        df_filmes = pd.read_csv(self.filmes_path)
        generos_usuario = [df_filmes[df_filmes["filme"].str.lower() == f.lower()]["genero"].values[0]
                           for f in usuario["filmes"] if not df_filmes[df_filmes["filme"].str.lower() == f.lower()].empty]

        todos_filmes = df_filmes[~df_filmes["filme"].isin(usuario["filmes"])]
        todos_filmes["score"] = todos_filmes["genero"].apply(lambda g: generos_usuario.count(g))
        recomendados = todos_filmes.sort_values("score", ascending=False)["filme"].tolist()
        return recomendados[:top_n]

    def get_recommendations(self, user_id, top_n=3):
        recs_pesos = self.recommend_by_weights(user_id, top_n)
        if recs_pesos:
            return recs_pesos
        recs_knn = self.recommend_by_knn(user_id, top_n)
        if recs_knn:
            return recs_knn
        recs_mf = self.recommend_by_matrix_factorization(user_id, top_n)
        if recs_mf:
            return recs_mf
        recs_user = self.recommend_by_user_similarity(user_id, top_n)
        if recs_user:
            return recs_user
        recs_cluster = self.recommend_by_cluster(user_id, top_n)
        if recs_cluster:
            return recs_cluster
        return self.recommend_by_popularity(user_id, top_n)
