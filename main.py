from fastapi import FastAPI

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