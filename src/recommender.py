import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
from sklearn.cluster import KMeans

class InteractiveRecommender:
    def __init__(self, csv_path=None):
        self.csv_path = csv_path
        self.usuarios = {}
        self.next_id = 1
        self.todos_filmes = []
        self.kmeans_model = None
        self.clusters = {}

        if csv_path:
            self.load_csv(csv_path)
            self._atualizar_clusters()

    def load_csv(self, csv_path):
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            user_id = int(row['user_id'])
            nome = row['nome']
            filmes = [f for f in row[2:].dropna().tolist()]
            self.usuarios[user_id] = {"nome": nome, "filmes": set(filmes)}
            self.next_id = max(self.next_id, user_id + 1)

    def save_csv(self):
        if not self.csv_path:
            return

        max_len = max(len(u["filmes"]) for u in self.usuarios.values())
        data = []
        for user_id, info in self.usuarios.items():
            row = [user_id, info["nome"]] + list(info["filmes"]) + [None]*(max_len - len(info["filmes"]))
            data.append(row)

        colunas = ["user_id", "nome"] + [f"filme{i+1}" for i in range(max_len)]
        df = pd.DataFrame(data, columns=colunas)
        df.to_csv(self.csv_path, index=False)

    def add_user_preferences(self, nome, filmes):
        user_id = self.next_id
        self.next_id += 1
        self.usuarios[user_id] = {"nome": nome, "filmes": set(filmes)}
        self._atualizar_clusters()
        self.save_csv()
        return user_id

    def recommend(self, user_id, top_n=5):
        if user_id not in self.usuarios:
            return []

        filmes_digitados = self.usuarios[user_id]["filmes"]
        recomendacoes = {}

        for outro_id, info in self.usuarios.items():
            if outro_id == user_id:
                continue
            intersecao = filmes_digitados & info["filmes"]
            if intersecao:
                recs = info["filmes"] - filmes_digitados
                if recs:
                    recomendacoes[outro_id] = recs

        todas_recs = set()
        for r in recomendacoes.values():
            todas_recs |= r

        return list(todas_recs)[:top_n]

    def recommend_by_similarity(self, user_id, top_n=5):
        if user_id not in self.usuarios:
            return []

        todos_filmes = list({filme for u in self.usuarios.values() for filme in u["filmes"]})
        target_vector = np.array([1 if filme in self.usuarios[user_id]["filmes"] else 0 for filme in todos_filmes])

        similaridades = []
        for outro_id, info in self.usuarios.items():
            if outro_id == user_id:
                continue
            outro_vector = np.array([1 if filme in info["filmes"] else 0 for filme in todos_filmes])
            score = jaccard_score(target_vector, outro_vector)
            similaridades.append((outro_id, score))

        similaridades.sort(key=lambda x: x[1], reverse=True)

        recomendacoes = set()
        for outro_id, _ in similaridades[:3]:
            recomendacoes |= self.usuarios[outro_id]["filmes"] - self.usuarios[user_id]["filmes"]

        return list(recomendacoes)[:top_n]

    def media_similaridade(self, user_id):
        todos_filmes = list({filme for u in self.usuarios.values() for filme in u["filmes"]})
        target_vector = np.array([1 if filme in self.usuarios[user_id]["filmes"] else 0 for filme in todos_filmes])

        scores = []
        for outro_id, info in self.usuarios.items():
            if outro_id == user_id:
                continue
            outro_vector = np.array([1 if filme in info["filmes"] else 0 for filme in todos_filmes])
            scores.append(jaccard_score(target_vector, outro_vector))

        return np.mean(scores)

    def _atualizar_clusters(self, n_clusters=3):
        if len(self.usuarios) < n_clusters:
            self.clusters = {}
            self.kmeans_model = None
            return

        self.todos_filmes = list({filme for u in self.usuarios.values() for filme in u["filmes"]})
        vetores = []

        for user_id in self.usuarios:
            vetor = [1 if filme in self.usuarios[user_id]["filmes"] else 0 for filme in self.todos_filmes]
            vetores.append(vetor)

        X = np.array(vetores)
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42)
        labels = self.kmeans_model.fit_predict(X)

        self.clusters = {user_id: cluster for user_id, cluster in zip(self.usuarios.keys(), labels)}

    def recommend_by_cluster(self, user_id, top_n=5):
        if user_id not in self.usuarios or user_id not in self.clusters:
            return []

        cluster_id = self.clusters[user_id]
        filmes_cluster = []

        for outro_id, info in self.usuarios.items():
            if outro_id != user_id and self.clusters.get(outro_id) == cluster_id:
                filmes_cluster.extend(info["filmes"])

        filmes_recomendados = list(set(filmes_cluster) - self.usuarios[user_id]["filmes"])
        return filmes_recomendados[:top_n]