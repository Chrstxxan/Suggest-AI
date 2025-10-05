import os
import pandas as pd
import numpy as np
from collections import defaultdict
import unicodedata
from sklearn.neighbors import NearestNeighbors

# -------- util --------
def _normalizar(texto: str) -> str:
    t = texto.lower().strip()
    return unicodedata.normalize("NFKD", t).encode("ASCII", "ignore").decode("utf-8")

def _cosine_similarity_vec(a: np.ndarray, B: np.ndarray):
    """a : (d,), B: (n, d) -> returns (n,) cosine similarity a·B_i / (|a||B_i|)"""
    if B.size == 0:
        return np.array([])
    a = a.astype(float)
    B = B.astype(float)
    a_norm = np.linalg.norm(a)
    B_norm = np.linalg.norm(B, axis=1)
    denom = a_norm * B_norm
    denom[denom == 0] = 1e-9
    sims = (B @ a) / denom
    return sims

class InteractiveRecommender:
    def __init__(self,
                 users_file="D:/Dev/projetos vscode/SuggestAI/data/usuarios_filmes.csv",
                 movies_file="D:/Dev/projetos vscode/SuggestAI/data/filmes.csv"):
        self.users_file = users_file
        self.movies_file = movies_file

        self.users = {}
        self.movies = {}

        self._load_movies()
        self._load_users()

    # ----------------- IO -----------------
    def _load_movies(self):
        if os.path.exists(self.movies_file):
            df = pd.read_csv(self.movies_file)
            for _, row in df.iterrows():
                title = str(row["filme"]).strip()
                genre = str(row["genero"]).strip().lower()
                self.movies[title] = _normalizar(genre)
        else:
            pd.DataFrame(columns=["filme", "genero"]).to_csv(self.movies_file, index=False)

    def _load_users(self):
        if os.path.exists(self.users_file):
            df = pd.read_csv(self.users_file)
            for _, row in df.iterrows():
                uid = str(row["user_id"])
                nome = row.get("nome", "") if not pd.isna(row.get("nome", "")) else ""
                filmes = []
                for c in df.columns:
                    if c.lower().startswith("filme") and not pd.isna(row.get(c)):
                        filmes.append(str(row.get(c)).strip())
                prefs = {}
                for c in df.columns:
                    lc = c.lower()
                    if not (lc == "user_id" or lc == "nome" or lc.startswith("filme")):
                        val = row.get(c)
                        if pd.isna(val):
                            continue
                        try:
                            prefs[_normalizar(c)] = float(val)
                        except:
                            pass
                if not prefs:
                    genres = set(self.movies.values())
                    prefs = {g: 0.0 for g in genres}

                self.users[uid] = {"nome": nome, "movies": filmes, "preferences": prefs}
        else:
            pd.DataFrame(columns=["user_id", "nome"]).to_csv(self.users_file, index=False)

    def _ensure_genre_columns(self, prefs_keys):
        if os.path.exists(self.users_file):
            df = pd.read_csv(self.users_file)
        else:
            df = pd.DataFrame(columns=["user_id", "nome"])
        for i in range(1, 10):
            col = f"filme{i}"
            if col not in df.columns:
                df[col] = pd.NA
        for g in prefs_keys:
            if g not in df.columns:
                df[g] = pd.NA
        return df

    def save_users(self):
        all_genres = set()
        for u in self.users.values():
            all_genres.update(u["preferences"].keys())

        base_df = self._ensure_genre_columns(all_genres)
        rows = []
        for uid, u in self.users.items():
            linha = {"user_id": uid, "nome": u.get("nome", "")}
            for i, f in enumerate(u.get("movies", [])[:9]):
                linha[f"filme{i+1}"] = f
            for g in all_genres:
                linha[g] = u["preferences"].get(g, 0.0)
            rows.append(linha)

        out_df = pd.DataFrame(rows)
        final_df = pd.concat([out_df], ignore_index=True, sort=False)
        cols = ["user_id", "nome"] + [f"filme{i}" for i in range(1, 10)] + sorted(list(all_genres))
        final_df = final_df.reindex(columns=cols)
        final_df.to_csv(self.users_file, index=False)

    def save_movies(self):
        df = pd.DataFrame([{"filme": f, "genero": g} for f, g in self.movies.items()])
        df["genero"] = df["genero"].apply(lambda x: _normalizar(x))
        df.to_csv(self.movies_file, index=False)

    # ----------------- user management -----------------
    def add_user_with_genres(self, nome: str, entrada: str) -> str:
        filmes_do_usuario = []
        generos_novos = {}

        for item in entrada.split(","):
            if "-" in item:
                filme, genero = item.split("-", 1)
                filme = filme.strip()
                genero = _normalizar(genero.strip())
                filmes_do_usuario.append(filme)
                generos_novos[filme] = genero

        if len(filmes_do_usuario) < 3:
            raise ValueError("O usuário deve ter pelo menos 3 filmes.")

        for f, g in generos_novos.items():
            if f not in self.movies:
                self.movies[f] = g

        all_genres = set(self.movies.values())
        prefs = {g: 0.0 for g in all_genres}
        for g in generos_novos.values():
            prefs[g] = prefs.get(g, 0.0) + 1.0

        for g in prefs:
            prefs[g] = 0.1 + prefs[g]  # adiciona peso mínimo
        total = sum(prefs.values()) or 1.0
        for g in prefs:
            prefs[g] /= total

        uid = str(len(self.users) + 1)
        self.users[uid] = {"nome": nome, "movies": filmes_do_usuario, "preferences": prefs}

        self.save_movies()
        self.save_users()
        return uid

    # ----------------- recommenders -----------------
    def recommend_by_weights(self, user_id: str, top_n: int = 3):
        if user_id not in self.users:
            return []
        u = self.users[user_id]
        recs = {}
        for f, g in self.movies.items():
            if f in u["movies"]:
                continue
            score = u["preferences"].get(g, 0.0)
            if score > 0:
                recs[f] = score
        sorted_items = sorted(recs.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_items[:top_n]]

    def recommend_by_knn(self, user_id: str, top_n: int = 5, k: int = 2):
        if user_id not in self.users:
            return []

        all_genres = sorted(set(self.movies.values()))
        ids = []
        U = []
        for uid, u in self.users.items():
            ids.append(uid)
            vec = [u["preferences"].get(g, 0.0) for g in all_genres]
            U.append(vec)
        U = np.array(U)

        idx_target = ids.index(user_id)
        target_vec = U[idx_target].reshape(1, -1)

        k_adj = min(k, len(U)-1) or 1
        knn = NearestNeighbors(n_neighbors=k_adj+1, metric='cosine')
        knn.fit(U)
        distances, neighbors_idx = knn.kneighbors(target_vec)

        recomm = []
        for i in neighbors_idx[0]:
            if i == idx_target:
                continue
            uid = ids[i]
            for f in self.users[uid]["movies"]:
                if f not in self.users[user_id]["movies"]:
                    recomm.append(f)
        if not recomm:
            return []
        series = pd.Series(recomm).value_counts()
        return list(series.index[:top_n])

    def recommend_by_matrix_factorization(self, user_id: str, top_n: int = 5, n_factors: int = 3):
        if user_id not in self.users:
            return []

        movies_list = list(self.movies.keys())
        users_list = list(self.users.keys())

        R = np.zeros((len(users_list), len(movies_list)), dtype=float)
        for i, uid in enumerate(users_list):
            for j, m in enumerate(movies_list):
                if m in self.users[uid]["movies"]:
                    R[i, j] = 1.0

        try:
            U, s, Vt = np.linalg.svd(R, full_matrices=False)
        except np.linalg.LinAlgError:
            return self.recommend_by_popularity(user_id, top_n)

        k = min(n_factors, U.shape[1])
        U_k = U[:, :k]
        S_k = np.diag(s[:k])
        Vt_k = Vt[:k, :]

        R_hat = (U_k @ S_k) @ Vt_k
        idx_u = users_list.index(user_id)
        scores = R_hat[idx_u]

        recs = {}
        for j, m in enumerate(movies_list):
            if m not in self.users[user_id]["movies"]:
                recs[m] = scores[j]

        if not recs:
            return []

        sorted_items = sorted(recs.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_items[:top_n]]

    def recommend_by_user_similarity(self, user_id: str, top_n: int = 3):
        if user_id not in self.users:
            return []
        target = self.users[user_id]
        target_genres = set([self.movies[f] for f in target["movies"] if f in self.movies])
        candidates = []
        for uid, u in self.users.items():
            if uid == user_id:
                continue
            u_genres = set([self.movies[f] for f in u["movies"] if f in self.movies])
            if target_genres & u_genres:
                candidates.extend([f for f in u["movies"] if f not in target["movies"]])
        if not candidates:
            return []
        series = pd.Series(candidates).value_counts()
        return list(series.index[:top_n])

    def recommend_by_cluster(self, user_id: str, top_n: int = 3):
        if user_id not in self.users:
            return []
        target_movies = set(self.users[user_id]["movies"])
        recomm = set()
        for uid, u in self.users.items():
            if uid == user_id:
                continue
            inter = target_movies & set(u["movies"])
            if inter:
                recomm.update(set(u["movies"]) - target_movies)
        return list(recomm)[:top_n]

    def recommend_by_popularity(self, user_id: str, top_n: int = 3):
        all_films = []
        for u in self.users.values():
            all_films.extend(u["movies"])
        if not all_films:
            return []
        counts = pd.Series(all_films).value_counts()
        recs = [f for f in counts.index if f not in self.users[user_id]["movies"]][:top_n]
        return recs

    # ----------------- get_recommendations atualizado -----------------
    def get_recommendations(self, user_id: str, top_n: int = 5):
        if user_id not in self.users:
            return []

        scores = {}
        recomendadores = [
            self.recommend_by_weights,
            self.recommend_by_knn,
            self.recommend_by_matrix_factorization,
            self.recommend_by_user_similarity,
            self.recommend_by_cluster,
            self.recommend_by_popularity
        ]

        for metodo in recomendadores:
            try:
                recs = metodo(user_id, top_n=top_n)
            except TypeError:
                recs = metodo(user_id)

            for i, f in enumerate(recs):
                scores[f] = scores.get(f, 0) + (top_n - i)

        if not scores:
            return []

        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [f for f, _ in sorted_items[:top_n]]

    # ----------------- feedback -----------------
    def update_weights(self, user_id: str, filme: str, feedback: str):
        if user_id not in self.users:
            return
        filme_key = None
        for f in self.movies.keys():
            if f.lower() == filme.lower():
                filme_key = f
                break
        if not filme_key:
            return
        genero = self.movies[filme_key]
        u = self.users[user_id]
        if genero not in u["preferences"]:
            u["preferences"][genero] = 0.0
        if feedback.lower() == "s":
            u["preferences"][genero] += 0.1
        else:
            u["preferences"][genero] = max(0.0, u["preferences"][genero] - 0.1)
        if feedback.lower() == "s" and filme_key not in u["movies"]:
            u["movies"].append(filme_key)
        total = sum(u["preferences"].values()) or 1.0
        for g in u["preferences"]:
            u["preferences"][g] = u["preferences"][g] / total
        self.save_users()
