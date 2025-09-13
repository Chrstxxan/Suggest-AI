# src/recommender.py
import pandas as pd

class InteractiveRecommender:
    def __init__(self, csv_path=None):
        """
        Inicializa o recomendador interativo.
        - csv_path: caminho opcional para CSV inicial com IDs, nomes e filmes
        """
        self.csv_path = csv_path
        self.usuarios = {}  # user_id -> {"nome": nome, "filmes": set([...])}
        self.next_id = 1  # contador de IDs automáticos

        if csv_path:
            self.load_csv(csv_path)

    def load_csv(self, csv_path):
        """Carrega usuários do CSV inicial"""
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            user_id = int(row['user_id'])
            nome = row['nome']
            filmes = [f for f in row[2:].dropna().tolist()]
            self.usuarios[user_id] = {"nome": nome, "filmes": set(filmes)}
            self.next_id = max(self.next_id, user_id + 1)

    def save_csv(self):
        """Salva a base atualizada no CSV"""
        if not self.csv_path:
            return

        max_len = max(len(u["filmes"]) for u in self.usuarios.values())
        data = []
        for user_id, info in self.usuarios.items():
            row = [user_id, info["nome"]] + list(info["filmes"]) + [None]*(max_len - len(info["filmes"]))
            data.append(row)

        df = pd.DataFrame(data)
        df.to_csv(self.csv_path, index=False)

    def add_user_preferences(self, nome, filmes):
        """Adiciona usuário novo ou atualiza existentes"""
        # Verifica se já existe algum usuário com mesmo nome (opcional: permite duplicados)
        # Sempre cria um novo user_id para simplificar
        user_id = self.next_id
        self.next_id += 1
        self.usuarios[user_id] = {"nome": nome, "filmes": set(filmes)}
        self.save_csv()
        return user_id

    def recommend(self, user_id, top_n=5):
        """Recomenda filmes para um usuário pelo ID"""
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
