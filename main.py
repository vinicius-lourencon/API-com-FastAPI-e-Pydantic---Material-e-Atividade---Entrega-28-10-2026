from fastapi import FastAPI, HTTPException
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
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
@app.put("/tarefas/{tarefa_id}")
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: Tarefa):
    for i, tarefa in enumerate(tarefas):
        if tarefa.id == tarefa_id:
            tarefas[i] = tarefa_atualizada
            return tarefa_atualizada
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            tarefas.remove(tarefa)
            return {"mensagem": "Tarefa deletada"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")