from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Tarefa(BaseModel):
    id: int
    titulo: str
    descricao: str | None = None
    concluida: bool = False


tarefas = []


@app.get("/")
def raiz():
    return {"mensagem": "API de tarefas funcionando"}

@app.get("/tarefas")
def listar_tarefas():
    return tarefas


@app.post("/tarefas")
def criar_tarefa(tarefa: Tarefa):
    tarefas.append(tarefa)
    return tarefa

@app.get("/tarefas/{tarefa_id}")
def buscar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            return tarefa