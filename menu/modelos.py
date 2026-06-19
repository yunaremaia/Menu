from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


NomeNaoVazio = Annotated[
    str,
    StringConstraints(min_length=1, strip_whitespace=True),
]


class Cardapio(BaseModel):
    id: int | None = None
    nome: NomeNaoVazio
    descricao: str | None = None
    ativo: bool = True
    idioma_padrao: str = "pt-BR"
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Cardapio {self.nome}>"


class Categoria(BaseModel):
    id: int | None = None
    nome: NomeNaoVazio
    cardapio_id: int = Field(gt=0)
    ordem: int = Field(default=0, ge=0)
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Item(BaseModel):
    id: int | None = None
    nome: NomeNaoVazio
    descricao: str | None = None
    preco: float = Field(ge=0)
    foto_url: str | None = None
    tags: str = ""
    disponivel: bool = True
    destaque: bool = False
    ordem: int = Field(default=0, ge=0)
    categoria_id: int = Field(gt=0)
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Mesa(BaseModel):
    id: int | None = None
    identificacao: NomeNaoVazio
    cardapio_id: int = Field(gt=0)
    ativo: bool = True
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
