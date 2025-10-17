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

**filmes.csv: é a base que armazena todos os filmes que foram inseridos no modo manual por usuários e será usada para fazer recomendações**

**filme** | **genero**

Titanic	| romance

Matrix | ficcao cientifica

Gladiador | acao

O Iluminado	| terror

=====================

**usuarios_filmes.csv: contém os usuários que escolheram ser salvos na base, seus filmes aprovados com feedback positivo e seus pesos de preferência por gênero.**

**user_id**	| **nome**	| **filme1**	| ...	| **acao**	| **comedia**	| **drama**	| **ficcao cientifica**	| **romance**	| **terror**

1	        | Paula	    | Diário de Bridget Jones	| ...	| 0.017	| 0.017	| 0.017	    | 0.017	                | 0.91	        | 0.017

=====================

**usuarios_rejeitados.csv: contém os mesmos dados do arquivo .csv acima, porém este arquivo salva os filmes que os usuários rejeitaram com feedback negativo.**

**user_id**	| **nome**	| **filme1**	| **filme2** | ...

1           | Paula     | O Fabuloso Destino de Amelie Poulain | ...

---

## Como reproduzir:
- O primeiro passo é fazer a clonagem do presente repositório: 

git clone https://github.com/usuario/suggestai.git

cd suggestai

- O segundo passo é criar o seu ambiente virtual e instalar as dependências necessárias:

python -m venv .venv  - **criação do seu ambiente virtual**

pip install -r requirements.txt - **instalação das dependências necessárias para a execução do sistema**

- O terceiro passo requer atenção pois os códigos do sistema utilizam caminhos absolutos, por favor adapte-os para a estrutura da sua máquina.
**Segue exemplo do app.py:**

users_path = "D:/Dev/PyCharm Projects/SuggestAI/data/usuarios_filmes.csv"

movies_path = "D:/Dev/PyCharm Projects/SuggestAI/data/filmes.csv"

- No quarto passo você deve rodar o arquivo **web_app.py** que se encontra na pasta raiz do projeto para que tenha a experiência de rodar o sistema na web

O navegador abrirá automaticamente em http://127.0.0.1:5000.

---

## Resultados do projeto:
**preencher com métricas e mais 2-3 linhas de interpretação**

**colocar a estrutura:**

**SuggestAI/**

**── data/**

│   ├── filmes.csv

│   ├── usuarios_filmes.csv

│   └── usuarios_rejeitados.csv

**── src/**
│   
├── recommender.py          # Núcleo do sistema de recomendação

│   └── chatbot.py              # Funções do modo chatbot e registro de feedback

**── templates/**

│   ├── index.html              # Tela inicial

│   ├── manual.html             # Modo manual

│   ├── chat.html               # Modo chatbot

│   └── result.html             # Tela de resultados e feedback

│
├── app.py                      # Versão de terminal (CLI)

├── web_app.py                  # Versão Flask (interface web)

└── README.md
