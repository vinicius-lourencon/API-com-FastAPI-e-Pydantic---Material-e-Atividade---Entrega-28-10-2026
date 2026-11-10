# API de tarefas

Atividade de API com FastAPI e Pydantic. CRUD de tarefas salvando num banco SQLite com SQLAlchemy, tabelas criadas pelo Alembic e, agora, **autenticação com usuário, senha e token JWT**.

Dupla: Nicolas Wolf e Vinicius Antonio Lourençon

## O que tem de novo

- tabela `usuarios` no banco (model `UsuarioModel` + migração do Alembic)
- cadastro de usuário em `POST /usuarios`, com a senha salva como hash (argon2, pelo `pwdlib`)
- login em `POST /token`, que devolve um token JWT (algoritmo HS256, vale 30 minutos)
- as rotas de **criar, atualizar e deletar** tarefas agora só funcionam com token
- as rotas de listar e buscar tarefa continuam abertas, sem login

## Tecnologias

- FastAPI + Uvicorn
- Pydantic (schemas de entrada e saída)
- SQLAlchemy 2 + SQLite
- Alembic (migrações)
- PyJWT (gera e valida o token)
- pwdlib[argon2] (hash da senha)
- python-multipart (necessário pro formulário de login do `/token`)

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

o `alembic upgrade head` cria o arquivo `tarefas.db` com as tabelas `tarefas` e `usuarios`. Tem que rodar antes de subir a api senão dá erro.

> Se você já tinha o projeto rodando antes da parte de login, rode `pip install -r requirements.txt` e `alembic upgrade head` de novo pra instalar as libs novas e criar a tabela de usuários.

depois abrir http://127.0.0.1:8000/docs que tá tudo no swagger

## Rotas

| Método | Rota | Precisa de token? | O que faz |
|---|---|---|---|
| GET | `/` | não | mensagem de que a API está funcionando |
| POST | `/usuarios` | não | cadastra usuário (email + senha) |
| POST | `/token` | não | faz login e devolve o token JWT |
| GET | `/tarefas` | não | lista as tarefas (dá pra filtrar com `?concluida=true`) |
| GET | `/tarefas/{id}` | não | busca tarefa por id |
| POST | `/tarefas` | **sim** | cria tarefa |
| PUT | `/tarefas/{id}` | **sim** | atualiza tarefa |
| DELETE | `/tarefas/{id}` | **sim** | deleta tarefa |

### Cadastro de usuário (`POST /usuarios`)

Corpo em JSON. O email precisa ter pelo menos 3 caracteres e a senha pelo menos 6.

```json
{
  "email": "aluno@email.com",
  "senha": "123456"
}
```

Resposta `201` (a senha nunca volta na resposta):

```json
{
  "id": 1,
  "email": "aluno@email.com"
}
```

Se o email já existir volta `400` com `"Email ja cadastrado"`.

### Login (`POST /token`)

Diferente das outras rotas, o login **não é JSON**, é formulário (`application/x-www-form-urlencoded`), que é o padrão OAuth2 que o FastAPI usa. O campo `username` é o **email** do usuário.

```
username=aluno@email.com
password=123456
```

Resposta `200`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Se o email ou a senha estiverem errados volta `401` com `"Email ou senha incorretos"`.

### Usando o token

Nas rotas protegidas o token vai no cabeçalho `Authorization`:

```
Authorization: Bearer <access_token>
```

Respostas de erro:

- sem token → `401` `"Not authenticated"`
- token inválido, alterado ou expirado → `401` `"Token invalido ou expirado"`

## Exemplo de token JWT gerado pelo sistema

Token gerado pela rota `POST /token` depois de cadastrar o usuário `aluno@email.com` com a senha `123456`:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbHVub0BlbWFpbC5jb20iLCJleHAiOjE3OTQzNTA2NTZ9.bhVmP7cTQkCIsfnO-Qq55nv61AwNQEA-lNVMHQJk-Z4
```

O token tem 3 partes separadas por ponto (`header.payload.assinatura`). Decodificando as duas primeiras (são só base64, dá pra ver em https://jwt.io):

**Header**

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**

```json
{
  "sub": "aluno@email.com",
  "exp": 1794350656
}
```

- `sub` é o email do usuário logado; é por ele que a API descobre quem está fazendo a requisição
- `exp` é quando o token expira (timestamp Unix). Esse aí vence em 10/11/2026 às 18:44 (horário de Brasília), 30 minutos depois do login

A terceira parte é a assinatura, feita com a `SECRET_KEY` que está no `auth.py`. Se alguém mudar qualquer coisa no payload a assinatura não bate e a API recusa o token. Esse token de exemplo **já está expirado**, então pra testar tem que gerar um novo fazendo login.

## Como testar o login pelo Swagger

1. Suba a API (`uvicorn main:app --reload`) e abra http://127.0.0.1:8000/docs
2. **Cadastre um usuário**: abra `POST /usuarios`, clique em **Try it out**, coloque no corpo:
   ```json
   {
     "email": "aluno@email.com",
     "senha": "123456"
   }
   ```
   e clique em **Execute**. Tem que voltar `201` com o id e o email.
3. **Veja que a rota está protegida**: abra `POST /tarefas`, clique em **Try it out** e **Execute** com uma tarefa qualquer. Vai voltar `401 Not authenticated`, porque ainda não tem login. O cadeado aberto ao lado da rota mostra que ela precisa de autenticação.
4. **Faça o login**: clique no botão verde **Authorize** (com um cadeado, no canto superior direito da página). Na janela que abrir preencha:
   - **username**: `aluno@email.com` (é o email)
   - **password**: `123456`
   - deixe `client_id` e `client_secret` em branco

   Clique em **Authorize** e depois em **Close**. O Swagger chama o `POST /token` por trás, guarda o token e os cadeados das rotas ficam fechados.
5. **Teste as rotas protegidas**: agora `POST /tarefas`, `PUT /tarefas/{id}` e `DELETE /tarefas/{id}` funcionam, porque o Swagger manda o `Authorization: Bearer ...` sozinho. Por exemplo, crie:
   ```json
   {
     "titulo": "Estudar JWT",
     "descricao": "ler a doc do FastAPI",
     "concluida": false
   }
   ```
   deve voltar `201` com a tarefa criada.
6. **Ver o token na mão (opcional)**: dá pra testar a rota `POST /token` direto, em **Try it out**, preenchendo `username` e `password`. A resposta mostra o `access_token`, que pode ser colado no https://jwt.io pra ver o conteúdo.
7. **Sair**: clique em **Authorize** de novo e depois em **Logout**. As rotas protegidas voltam a dar `401`.

Lembrando que o token dura 30 minutos. Se as rotas começarem a dar `401 Token invalido ou expirado`, é só fazer Logout e Authorize de novo.

## Arquivos

- `main.py` - rotas (usuários, login e tarefas)
- `auth.py` - hash de senha, criação e validação do token JWT, e a dependência `get_usuario_atual` que protege as rotas
- `database.py` - conexão com o banco
- `models.py` - tabelas do banco (`tarefas` e `usuarios`)
- `schemas.py` - modelos do pydantic (tarefa, usuário e token)
- `alembic/` - migrações do banco (tabela de tarefas e tabela de usuários)

## Observação

A `SECRET_KEY` está escrita direto no `auth.py` porque é um projeto de estudo. Num projeto de verdade ela ficaria numa variável de ambiente e não iria pro GitHub.
