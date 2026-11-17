from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import criar_token, gerar_hash_senha, get_usuario_atual, verificar_senha
from database import get_db
from models import TarefaModel, UsuarioModel
from schemas import Tarefa, TarefaEntrada, Token, Usuario, UsuarioCriar

tags_metadata = [
    {
        "name": "Usuarios",
        "description": "Cadastro de usuarios e login. O login devolve o token JWT usado nas rotas protegidas.",
    },
    {
        "name": "Tarefas",
        "description": "CRUD das tarefas. As rotas de leitura sao publicas, as de criar, atualizar e deletar precisam de token.",
    },
]

app = FastAPI(
    title="API de Tarefas",
    description="Gerenciador de tarefas simples feito pra atividade de FastAPI",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

@app.get("/", tags=["Status"], summary="Verifica se a API esta no ar")
def raiz():
    """Rota simples so pra conferir se o servidor esta rodando."""
    return {"mensagem": "API de tarefas funcionando"}

@app.post(
    "/usuarios",
    response_model=Usuario,
    status_code=201,
    tags=["Usuarios"],
    summary="Cadastra um usuario",
    responses={400: {"description": "Email ja cadastrado"}},
)
def criar_usuario(usuario: UsuarioCriar, db: Session = Depends(get_db)):
    """
    Cria um usuario novo com email e senha.

    A senha é salva com hash no banco e nunca é devolvida na resposta.
    """
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


@app.post(
    "/token",
    response_model=Token,
    tags=["Usuarios"],
    summary="Faz login e devolve o token",
    responses={401: {"description": "Email ou senha incorretos"}},
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Recebe o email no campo **username** e a senha no campo **password**.

    Se estiver certo, devolve um token JWT que vale por 30 minutos.
    """
    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == form_data.username).first()
    if usuario is None or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token(usuario.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get(
    "/tarefas",
    response_model=list[Tarefa],
    tags=["Tarefas"],
    summary="Lista as tarefas",
)
def listar_tarefas(concluida: bool | None = None, db: Session = Depends(get_db)):
    """
    Lista todas as tarefas cadastradas.

    Da pra filtrar pelo parametro **concluida** (true ou false). Sem ele, volta tudo.
    """
    consulta = db.query(TarefaModel)
    if concluida is not None:
        consulta = consulta.filter(TarefaModel.concluida == concluida)
    return consulta.all()

@app.post(
    "/tarefas",
    response_model=Tarefa,
    status_code=201,
    tags=["Tarefas"],
    summary="Cria uma tarefa",
    responses={401: {"description": "Token ausente, invalido ou expirado"}},
)
def criar_tarefa(
    tarefa: TarefaEntrada,
    db: Session = Depends(get_db),
    usuario: UsuarioModel = Depends(get_usuario_atual),
):
    """
    Cria uma tarefa nova. **Precisa estar logado.**

    O id é gerado pelo banco, nao precisa mandar.
    """
    nova_tarefa = TarefaModel(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida,
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return nova_tarefa

@app.get(
    "/tarefas/{tarefa_id}",
    response_model=Tarefa,
    tags=["Tarefas"],
    summary="Busca uma tarefa pelo id",
    responses={404: {"description": "Tarefa não encontrada"}},
)
def buscar_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    """Busca uma tarefa pelo id. Se nao existir, devolve 404."""
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa


@app.put(
    "/tarefas/{tarefa_id}",
    response_model=Tarefa,
    tags=["Tarefas"],
    summary="Atualiza uma tarefa",
    responses={
        401: {"description": "Token ausente, invalido ou expirado"},
        404: {"description": "Tarefa não encontrada"},
    },
)
def atualizar_tarefa(
    tarefa_id: int,
    tarefa_atualizada: TarefaEntrada,
    db: Session = Depends(get_db),
    usuario: UsuarioModel = Depends(get_usuario_atual),
):
    """
    Substitui os dados de uma tarefa pelos dados enviados. **Precisa estar logado.**

    O id vem pela URL e nao muda.
    """
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    tarefa.titulo = tarefa_atualizada.titulo
    tarefa.descricao = tarefa_atualizada.descricao
    tarefa.concluida = tarefa_atualizada.concluida
    db.commit()
    db.refresh(tarefa)
    return tarefa


@app.delete(
    "/tarefas/{tarefa_id}",
    tags=["Tarefas"],
    summary="Deleta uma tarefa",
    responses={
        401: {"description": "Token ausente, invalido ou expirado"},
        404: {"description": "Tarefa não encontrada"},
    },
)
def deletar_tarefa(
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: UsuarioModel = Depends(get_usuario_atual),
):
    """Apaga uma tarefa do banco. **Precisa estar logado.**"""
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(tarefa)
    db.commit()
    return {"mensagem": "Tarefa deletada"}