import pandas as pd
import os

class InteractiveRecommender:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.usuarios = {}
        self.load_csv(csv_path)

    def load_csv(self, path):
        if not os.path.exists(path):
            self.usuarios = {}
            return

        df = pd.read_csv(path)
        for _, row in df.iterrows():
            user_id = row["user_id"]
            nome = row["nome"]
            filmes = [str(row[f]) for f in row.index if f.startswith("filme") and pd.notna(row[f])]
            self.usuarios[user_id] = {"nome": nome, "filmes": set(filmes)}

    def save_csv(self):
        linhas = []
        for user_id, dados in self.usuarios.items():
            linha = {"user_id": user_id, "nome": dados["nome"]}
            for i, filme in enumerate(dados["filmes"]):
                linha[f"filme{i+1}"] = filme
            linhas.append(linha)
        df = pd.DataFrame(linhas)
        df.to_csv(self.csv_path, index=False)

    def add_user_preferences(self, nome, filmes):
        user_id = str(len(self.usuarios) + 1)
        self.usuarios[user_id] = {"nome": nome, "filmes": set(filmes)}
        self.save_csv()
        return user_id

    def add_user_with_genres(self, nome, entrada):
        filmes_do_usuario = []
        generos_novos = {}

        for item in entrada.split(","):
            if "-" in item:
                nome_filme, genero = item.split("-", 1)
                nome_filme = nome_filme.strip()
                filmes_do_usuario.append(nome_filme)
                generos_novos[nome_filme] = [g.strip() for g in genero.split(";")]

        user_id = self.add_user_preferences(nome, filmes_do_usuario)

        # Atualiza filmes.csv
        filmes_path = "D:/Dev/projetos vscode/SuggestAI/data/filmes.csv"
        try:
            filmes_df = pd.read_csv(filmes_path)
        except FileNotFoundError:
            filmes_df = pd.DataFrame(columns=["filme", "generos"])

        filmes_existentes = set(filmes_df["filme"])
        novas_linhas = []

        for filme, generos in generos_novos.items():
            if filme not in filmes_existentes:
                novas_linhas.append({"filme": filme, "generos": ";".join(generos)})

        if novas_linhas:
            filmes_df = pd.concat([filmes_df, pd.DataFrame(novas_linhas)], ignore_index=True)
            filmes_df.to_csv(filmes_path, index=False)

        return user_id

    def recommend_by_cluster(self, user_id, top_n=5):
        # Simulação simples: recomenda filmes populares entre usuários com filmes em comum
        filmes_usuario = self.usuarios[user_id]["filmes"]
        contagem = {}

        for uid, dados in self.usuarios.items():
            if uid == user_id:
                continue
            intersecao = filmes_usuario.intersection(dados["filmes"])
            if intersecao:
                for filme in dados["filmes"]:
                    if filme not in filmes_usuario:
                        contagem[filme] = contagem.get(filme, 0) + 1

        recomendados = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        return [f[0] for f in recomendados[:top_n]]

    def recommend_by_similarity(self, user_id, top_n=5):
        # Simulação: recomenda filmes de usuários com maior número de filmes em comum
        filmes_usuario = self.usuarios[user_id]["filmes"]
        similaridade = {}

        for uid, dados in self.usuarios.items():
            if uid == user_id:
                continue
            intersecao = filmes_usuario.intersection(dados["filmes"])
            similaridade[uid] = len(intersecao)

        mais_similares = sorted(similaridade.items(), key=lambda x: x[1], reverse=True)
        recomendados = []

        for uid, _ in mais_similares:
            for filme in self.usuarios[uid]["filmes"]:
                if filme not in filmes_usuario and filme not in recomendados:
                    recomendados.append(filme)
                if len(recomendados) >= top_n:
                    break
            if len(recomendados) >= top_n:
                break

        return recomendados

    def recommend(self, user_id, top_n=5):
        # Recomenda filmes mais frequentes entre todos os usuários
        filmes_usuario = self.usuarios[user_id]["filmes"]
        contagem = {}

        for dados in self.usuarios.values():
            for filme in dados["filmes"]:
                if filme not in filmes_usuario:
                    contagem[filme] = contagem.get(filme, 0) + 1

        recomendados = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        return [f[0] for f in recomendados[:top_n]]