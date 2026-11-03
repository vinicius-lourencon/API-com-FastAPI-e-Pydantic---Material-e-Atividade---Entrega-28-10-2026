# API de tarefas

Atividade de API com FastAPI e Pydantic. CRUD de tarefas, agora salvando num banco SQLite com SQLAlchemy e as tabelas criadas pelo Alembic.

Dupla: Nicolas Wolf e Vinicius Antonio Lourençon

## Como rodar

precisa ter python instalado (3.10 pra cima)

clonar o repositorio e entrar na pasta, depois:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

no linux/mac pra ativar o venv é `source venv/bin/activate`

o `alembic upgrade head` cria o arquivo tarefas.db com a tabela, tem que rodar antes de subir a api senao da erro

depois abrir http://127.0.0.1:8000/docs que ta tudo no swagger

## Rotas

- GET /tarefas - lista as tarefas (da pra filtrar com ?concluida=true)
- POST /tarefas - cria tarefa
- GET /tarefas/{id} - busca por id
- PUT /tarefas/{id} - atualiza
- DELETE /tarefas/{id} - deleta

## Arquivos

- main.py - rotas
- database.py - conexao com o banco
- models.py - tabela do banco
- schemas.py - modelos do pydantic
- alembic/ - migracoes do banco