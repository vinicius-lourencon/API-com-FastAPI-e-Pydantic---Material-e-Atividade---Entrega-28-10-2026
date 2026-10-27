from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class TarefaEntrada(BaseModel):
    titulo: str
    descricao: str | None = None
    concluida: bool = False


class Tarefa(BaseModel):
    id: int
    titulo: str
    descricao: str | None = None
    concluida: bool = False


tarefas = []
proximo_id = 1


@app.get("/")
def raiz():
    return {"mensagem": "API de tarefas funcionando"}


@app.get("/tarefas", response_model=list[Tarefa])
def listar_tarefas(concluida: bool | None = None):
    if concluida is None:
        return tarefas

    resultado = []
    for tarefa in tarefas:
        if tarefa.concluida == concluida:
            resultado.append(tarefa)
    return resultado


@app.post("/tarefas", response_model=Tarefa)
def criar_tarefa(tarefa: TarefaEntrada):
    global proximo_id
    nova_tarefa = Tarefa(
        id=proximo_id,
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida,
    )
    tarefas.append(nova_tarefa)
    proximo_id += 1
    return nova_tarefa


@app.get("/tarefas/{tarefa_id}", response_model=Tarefa)
def buscar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            return tarefa
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@app.put("/tarefas/{tarefa_id}", response_model=Tarefa)
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: TarefaEntrada):
    for i, tarefa in enumerate(tarefas):
        if tarefa.id == tarefa_id:
            tarefas[i] = Tarefa(
                id=tarefa_id,
                titulo=tarefa_atualizada.titulo,
                descricao=tarefa_atualizada.descricao,
                concluida=tarefa_atualizada.concluida,
            )
            return tarefas[i]
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            tarefas.remove(tarefa)
            return {"mensagem": "Tarefa deletada"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")