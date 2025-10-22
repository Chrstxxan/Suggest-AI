# SuggestAI

Um sistema de recomendação de filmes interativo que pode ser usado tanto no **modo manual (inserção de seus filmes favoritos)** quanto pelo **modo chatbot**.  
O projeto inclui interface web com **Flask + TailwindCSS** e também uma versão **CLI (terminal)**.

---
## Equipe Responsável:
- **Christian Delucca Vieira Rodrigues** - **RA:** 2224204268
- Turma: 41 SA | Curso: Ciência da Computação | Período: Noturno | Ano: 2025
---

## Funcionalidades:
- **Modo Manual:** usuário digita filmes e gêneros preferidos.  
- **Modo Chatbot:** usuário descreve o que gosta (ex: “gosto de ação e evito comédia”).  
- **Feedback Interativo:** like/dislike em cada filme recomendado.  
- **Salvamento opcional:** o usuário escolhe se quer salvar seus dados para melhorar o modelo.  
- **Interface web moderna**, responsiva e intuitiva.
---

## Problema:
- Hoje, plataformas de streaming oferecem milhares de filmes, e o usuário muitas vezes não sabe o que assistir.
O SuggestAI propõe resolver essa dor recomendando filmes com base nas preferências declaradas do usuário (filmes ou gêneros que gosta e não gosta).

O sistema busca oferecer recomendações personalizadas e um processo interativo de feedback, onde o usuário informa se gostou ou não dos filmes sugeridos —
e o modelo aprende progressivamente com essas respostas.

---

## Abordagem de IA:
- O projeto utiliza uma abordagem baseada em perfil de usuário, com um modelo de recomendação por similaridade de gênero.
Cada usuário é representado por um vetor de pesos associados aos gêneros de filmes (ação, comédia, drama, etc.), ajustados com base em feedback positivo ou negativo.

Essa técnica foi escolhida porque:

**É simples, interpretável e leve, ideal para protótipos.**

Permite atualizar preferências em tempo real, sem re-treinar o modelo.

**Métrica principal: nível de aderência percebida nas recomendações (medida pelos feedbacks positivos).**

---
## Dados:
**O sistema utiliza bases criadas pelo próprio desenvolvedor durante o desenvolvimento do modelo, armazenadas localmente em CSVs:**

- **filmes.csv: é a base que armazena todos os filmes que foram inseridos no modo manual por usuários e será usada para fazer recomendações**

| **filme**       | **genero**           |
|------------------|----------------------|
| Titanic          | romance              |
| Matrix           | ficcao cientifica    |
| Gladiador        | acao                 |
| O Iluminado      | terror               |


---

- **usuarios_filmes.csv: contém os usuários que escolheram ser salvos na base, seus filmes aprovados com feedback positivo e seus pesos de preferência por gênero.**

| **user_id** | **nome** | **filme1**                 | ... | **acao** | **comedia** | **drama** | **ficcao cientifica** | **romance** | **terror** |
|--------------|-----------|----------------------------|------|-----------|--------------|-----------|------------------------|--------------|-------------|
| 1            | Paula     | Diário de Bridget Jones    | ...  | 0.017     | 0.017        | 0.017     | 0.017                 | 0.910        | 0.017       |


---

- **usuarios_rejeitados.csv: contém os mesmos dados do arquivo .csv acima, porém este arquivo salva os filmes que os usuários rejeitaram com feedback negativo.**

| **user_id** | **nome** | **filme1**                             | **filme2** | **filme3** | ... |
|--------------|-----------|----------------------------------------|------------|------------|-----|
| 1            | Paula     | O Fabuloso Destino de Amélie Poulain  | ...        | ...        | ... |

---

## Como reproduzir:
- O primeiro passo é fazer a clonagem do presente repositório: 

```git clone https://github.com/usuario/suggestai.git```

```cd suggestai```

- O segundo passo é criar o seu ambiente virtual e instalar as dependências necessárias:

```python -m venv .venv```   # criação do seu ambiente virtual

```pip install -r requirements.txt``` # instalação das dependências necessárias para a execução do sistema

- O terceiro passo requer atenção pois os códigos do sistema utilizam caminhos absolutos, por favor adapte-os para a estrutura da sua máquina.
**Segue exemplo do ```app.py```:**

```users_path = "D:/Dev/PyCharm Projects/SuggestAI/data/usuarios_filmes.csv"```

```movies_path = "D:/Dev/PyCharm Projects/SuggestAI/data/filmes.csv"```

- No quarto passo você deve rodar o arquivo **web_app.py** que se encontra na pasta raiz do projeto para que tenha a experiência de rodar o sistema na web

O navegador abrirá automaticamente em http://127.0.0.1:5000.

---

## Resultados do projeto:
**Métricas do modelo e interpretação:**

O desempenho do *SuggestAI* foi avaliado utilizando um conjunto de usuários reais e métricas clássicas de classificação.
A avaliação simulou um cenário de **treino e teste**, separando parte dos filmes de cada usuário para medir a capacidade do modelo em prever títulos relevantes.

| Métrica        | Valor | Interpretação                                                               |
|----------------|-------|-----------------------------------------------------------------------------|
| **Precisão**   | 0.74  | Entre os filmes recomendados, 74% eram realmente relevantes para o usuário. |
| **Recall**     | 0.22  | O modelo identificou 22% de todos os filmes relevantes possíveis.           |
| **F1-Score**   | 0.34  | Mostra equilíbrio moderado entre precisão e abrangência.                    |
| **AUC ROC**    | 0.57  | Indica boa capacidade de distinguir entre filmes relevantes e irrelevantes. |
| **AUC PR**     | 0.68  | Forte desempenho mesmo com base desbalanceada (mais filmes ruins que bons). |

### Interpretação dos Resultados

- O modelo **prioriza precisão** em vez de recall, ou seja, recomenda poucos filmes, mas com alta chance de agradar.  
- O **AUC PR de 0.68** mostra que o sistema mantém boas recomendações mesmo em cenários desbalanceados, típicos de catálogos de filmes.  
- O **AUC ROC de 0.57** e o **F1-score de 0.34** indicam um modelo funcional, porém ainda com margem para melhorar a cobertura — algo que pode ser aprimorado com mais dados e feedbacks.  
- A **Matriz de Confusão** (53 TN, 14 TP, 50 FN, 5 FP) reforça que o modelo é **conservador**: evita recomendar algo ruim, preferindo “errar por omissão”.

No geral, o *SuggestAI* apresenta um **comportamento estável e coerente com sistemas de recomendação baseados em conteúdo e feedback incremental**, equilibrando qualidade e confiabilidade nas sugestões.

```text
SuggestAI/
├── data/                              # Base de dados utilizada pelo sistema
│ ├── filmes.csv                       # Lista de filmes e seus respectivos gêneros
│ ├── usuarios_filmes.csv              # Histórico de filmes aprovados e preferências dos usuários
│ └── usuarios_rejeitados.csv          # Registro de filmes rejeitados pelos usuários
│
├── src/                               # Código-fonte principal da aplicação
│ ├── chatbot.py                       # Módulo de interpretação de linguagem natural e recomendação via chat
│ └── recommender.py                   # Classe InteractiveRecommender e algoritmos de recomendação híbrida
│
├── templates/                         # Arquivos HTML utilizados pela interface web (Flask)
│ ├── chat.html                        # Página do modo Chatbot
│ ├── index.html                       # Página inicial
│ ├── manual.html                      # Página do modo Manual
│ └── result.html                      # Página de resultados e feedback
│
├── app.py                             # Aplicação em modo terminal (modo manual e modo chat)
├── web_app.py                         # Aplicação web Flask (abre no navegador automaticamente)
├── visual_metrics.py                  # Script de avaliação e geração de métricas gráficas
├── requirements.txt                   # Dependências do projeto (bibliotecas necessárias)
├── README.md                          # Documentação e instruções do projeto
└── .gitignore                         # Arquivos e pastas ignorados pelo Git

```

---