from pydantic import BaseModel, ConfigDict, Field


class TarefaEntrada(BaseModel):
    titulo: str = Field(min_length=1, description="Titulo da tarefa", examples=["Estudar FastAPI"])
    descricao: str | None = Field(default=None, description="Detalhes da tarefa", examples=["Fazer a atividade de testes"])
    concluida: bool = Field(default=False, description="Se a tarefa ja foi feita")


class Tarefa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descricao: str | None = None
    concluida: bool = False
    

class UsuarioCriar(BaseModel):
    email: str = Field(min_length=3, description="Email usado no login", examples=["aluno@email.com"])
    senha: str = Field(min_length=6, description="Senha com no minimo 6 caracteres", examples=["123456"])


class Usuario(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str