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
def listar_tarefas(concluida: bool | None = None):
    if concluida is None:
        return tarefas

    resultado = []
    for tarefa in tarefas:
        if tarefa.concluida == concluida:
            resultado.append(tarefa)
    return resultado


@app.post("/tarefas")
def criar_tarefa(tarefa: Tarefa):
    tarefas.append(tarefa)
    return tarefa

@app.get("/tarefas/{tarefa_id}")
def buscar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            return tarefa
        
@app.put("/tarefas/{tarefa_id}")
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: Tarefa):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            tarefa = tarefa_atualizada
            return tarefa
        
@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            tarefas.remove(tarefa)
            return {"mensagem": "Tarefa deletada"}