from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TarefaModel(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String, nullable=True)
    concluida: Mapped[bool] = mapped_column(default=False)