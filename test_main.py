import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

def get_db_teste():
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_db_teste
client = TestClient(app)

@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)

def test_listar_tarefas_retorna_200():
    resposta = client.get("/tarefas")
    assert resposta.status_code == 200
    assert resposta.json() == []

def test_buscar_tarefa_inexistente_retorna_404():
    resposta = client.get("/tarefas/999")
    assert resposta.status_code == 404

def test_criar_tarefa_sem_token_retorna_401():
    resposta = client.post("/tarefas", json={"titulo": "Estudar"})
    assert resposta.status_code == 401
    
def test_login_com_senha_errada_retorna_401():
    client.post("/usuarios", json={"email": "teste@email.com", "senha": "123456"})
    resposta = client.post("/token", data={"username": "teste@email.com", "password": "errada"})
    assert resposta.status_code == 401

def test_login_retorna_token():
    client.post("/usuarios", json={"email": "teste@email.com", "senha": "123456"})
    resposta = client.post("/token", data={"username": "teste@email.com", "password": "123456"})
    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"
    
def pegar_token():
    client.post("/usuarios", json={"email": "teste@email.com", "senha": "123456"})
    resposta = client.post("/token", data={"username": "teste@email.com", "password": "123456"})
    return resposta.json()["access_token"]

def test_criar_tarefa_com_token_retorna_201():
    token = pegar_token()
    resposta = client.post(
        "/tarefas",
        json={"titulo": "Estudar"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 201
    assert resposta.json()["titulo"] == "Estudar"

def test_deletar_tarefa_com_token():
    token = pegar_token()
    cabecalho = {"Authorization": f"Bearer {token}"}
    criada = client.post("/tarefas", json={"titulo": "Apagar"}, headers=cabecalho).json()

    resposta = client.delete(f"/tarefas/{criada['id']}", headers=cabecalho)
    assert resposta.status_code == 200
    assert client.get(f"/tarefas/{criada['id']}").status_code == 404