# API de tarefas

Atividade de API com FastAPI, Pydantic e CRUD de tarefas.

Dupla: Nicolas Wolf e Vinicius Antonio Lourençon

## Como rodar

precisa ter python instalado (3.10 pra cima)

clonar o repositorio e entrar na pasta, depois:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
## Rotas

- GET /tarefas - lista as tarefas (da pra filtrar com ?concluida=true)
- POST /tarefas - cria tarefa
- GET /tarefas/{id} - busca por id
- PUT /tarefas/{id} - atualiza
- DELETE /tarefas/{id} - deleta