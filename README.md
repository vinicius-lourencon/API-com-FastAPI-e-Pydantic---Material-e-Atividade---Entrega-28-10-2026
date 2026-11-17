# API de tarefas

API de gerenciador de tarefas feita com FastAPI para as atividades da materia.

Dupla: Nicolas Wolf e Vinicius Antonio Lourençon

## Atividades entregues neste repositorio

o mesmo repositorio foi usado nas 3 atividades, cada uma foi feita em cima da anterior:

- **Atividade 1** - API com FastAPI e Pydantic - entrega 28/10/2026 
- **Atividade 2** - Persistencia de dados e migracoes - entrega 04/11/2026 
- **Atividade 3** - Autenticacao e autorizacao (tokens) - entrega 11/11/2026 
- **Atividade 4** - Testes e documentacao - entrega 18/11/2026 

as datas de cada parte tambem aparecem no historico de commits

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

o `alembic upgrade head` cria o arquivo tarefas.db com as tabelas, tem que rodar antes de subir a api senao da erro

depois abrir http://127.0.0.1:8000/docs que ta tudo no swagger

- test_main.py - testes automaticos com pytest

## Como rodar os testes

com o venv ativado:

```
pytest
```

os testes usam um banco na memoria, entao nao mexem no tarefas.db. tem 7 testes: listar tarefas (200), buscar tarefa que nao existe (404), criar tarefa sem token (401), login com senha errada (401), login certo devolvendo token, criar tarefa com token (201) e deletar tarefa com token

## Rotas

- POST /usuarios - cadastra usuario (email e senha)
- POST /token - login, devolve o token JWT
- GET /tarefas - lista as tarefas (da pra filtrar com ?concluida=true)
- GET /tarefas/{id} - busca por id
- POST /tarefas - cria tarefa (precisa de token)
- PUT /tarefas/{id} - atualiza (precisa de token)
- DELETE /tarefas/{id} - deleta (precisa de token)

as rotas GET sao publicas, so as que alteram alguma coisa pedem login

## Como testar o login pelo swagger

1. no /docs, cadastrar um usuario no POST /usuarios
2. clicar no botao Authorize (cadeado la em cima) e colocar o email no campo username e a senha no password
3. depois disso o swagger manda o token sozinho e da pra usar o POST, PUT e DELETE de tarefas

sem fazer login essas rotas retornam 401

## Exemplo de token

token gerado pela rota /token (ele vence em 30 minutos):

```
exemplo de token:"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZUBlbWFpbC5jb20iLCJleHAiOjE3OTUwMDAwMDB9.HFzHCQccuWT0cCS36N4UNSkHdzs4GfAaoA5PT4HqYMA"
```

pra usar fora do swagger tem que mandar no header assim:

```
Authorization: Bearer <token>
```

## Arquivos

- main.py - rotas
- database.py - conexao com o banco
- models.py - tabelas do banco (tarefas e usuarios)
- schemas.py - modelos do pydantic
- auth.py - hash da senha e geracao/validacao do token
- alembic/ - migracoes do banco

- test_main.py - testes automaticos com pytest

## O que foi feito em cada atividade

**Atividade 1:** CRUD de tarefas com os dados numa lista em memoria, modelos do pydantic pra entrada e saida e documentacao pelo swagger.

**Atividade 2:** troca da lista em memoria por banco SQLite com SQLAlchemy, rotas usando sessao com Depends e tabela criada pelo Alembic. O arquivo .db fica no .gitignore.

**Atividade 3:** tabela de usuarios com senha em hash, rota /token que devolve um JWT e as rotas POST, PUT e DELETE de tarefas protegidas pelo token.

**Atividade 4:** documentacao das rotas no swagger com tags, resumos, descricoes (docstrings), respostas de erro e exemplos nos schemas. Testes automaticos com pytest e TestClient.
