from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import TarefaModel
from schemas import Tarefa, TarefaEntrada

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Tarefas",
    description="Gerenciador de tarefas simples feito pra atividade de FastAPI",
)

tarefas = []

@app.get("/")
def raiz():
    return {"mensagem": "API de tarefas funcionando"}

@app.get("/tarefas", response_model=list[Tarefa])
def listar_tarefas(concluida: bool | None = None, db: Session = Depends(get_db)):
    consulta = db.query(TarefaModel)
    if concluida is not None:
        consulta = consulta.filter(TarefaModel.concluida == concluida)
    return consulta.all()

@app.post("/tarefas", response_model=Tarefa, status_code=201)
def criar_tarefa(tarefa: TarefaEntrada, db: Session = Depends(get_db)):
    nova_tarefa = TarefaModel(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida,
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
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