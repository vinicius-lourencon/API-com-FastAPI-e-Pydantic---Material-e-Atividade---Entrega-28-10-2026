from pydantic import BaseModel, ConfigDict, Field


class TarefaEntrada(BaseModel):
    titulo: str = Field(min_length=1)
    descricao: str | None = None
    concluida: bool = False


class Tarefa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descricao: str | None = None
    concluida: bool = False