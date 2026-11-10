from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import criar_token, gerar_hash_senha, get_usuario_atual, verificar_senha
from database import get_db
from models import TarefaModel, UsuarioModel
from schemas import Tarefa, TarefaEntrada, Token, Usuario, UsuarioCriar

app = FastAPI(
    title="API de Tarefas",
    description="Gerenciador de tarefas simples feito pra atividade de FastAPI",
)

@app.get("/")
def raiz():
    return {"mensagem": "API de tarefas funcionando"}

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(usuario: UsuarioCriar, db: Session = Depends(get_db)):
    existe = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")

    novo_usuario = UsuarioModel(
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == form_data.username).first()
    if usuario is None or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token(usuario.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/tarefas", response_model=list[Tarefa])
def listar_tarefas(concluida: bool | None = None, db: Session = Depends(get_db)):
    consulta = db.query(TarefaModel)
    if concluida is not None:
        consulta = consulta.filter(TarefaModel.concluida == concluida)
    return consulta.all()

@app.post("/tarefas", response_model=Tarefa, status_code=201)
def criar_tarefa(
    tarefa: TarefaEntrada,
    db: Session = Depends(get_db),
    usuario: UsuarioModel = Depends(get_usuario_atual),
):
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
def buscar_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa


@app.put("/tarefas/{tarefa_id}", response_model=Tarefa)
def atualizar_tarefa(
    tarefa_id: int,
    tarefa_atualizada: TarefaEntrada,
    db: Session = Depends(get_db),
    usuario: UsuarioModel = Depends(get_usuario_atual),
):
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    tarefa.titulo = tarefa_atualizada.titulo
    tarefa.descricao = tarefa_atualizada.descricao
    tarefa.concluida = tarefa_atualizada.concluida
    db.commit()
    db.refresh(tarefa)
    return tarefa


@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: UsuarioModel = Depends(get_usuario_atual),
):
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(tarefa)
    db.commit()
    return {"mensagem": "Tarefa deletada"}