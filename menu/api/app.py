from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from menu.modelos import Cardapio
from menu.repositorio.banco import Banco


class CardapioRequest(BaseModel):
    nome: str = Field(min_length=1)
    descricao: str | None = None
    ativo: bool = True
    idioma_padrao: str = "pt-BR"


class CardapioResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    ativo: bool
    idioma_padrao: str
    criado_em: datetime
    atualizado_em: datetime


def criar_app(caminho_banco: str = "menu.db") -> FastAPI:
    banco = Banco(caminho_banco)
    banco.iniciar()

    app = FastAPI(title="Menu", version="0.1.0")

    @app.post("/api/cardapios", response_model=CardapioResponse, status_code=201)
    def criar_cardapio(dados: CardapioRequest):
        cardapio = Cardapio(
            nome=dados.nome,
            descricao=dados.descricao,
            ativo=dados.ativo,
            idioma_padrao=dados.idioma_padrao,
            criado_em=datetime.now(timezone.utc),
            atualizado_em=datetime.now(timezone.utc),
        )
        return banco.criar_cardapio(cardapio)

    @app.get("/api/cardapios", response_model=list[CardapioResponse])
    def listar_cardapios(apenas_ativos: bool = False):
        return banco.listar_cardapios(apenas_ativos=apenas_ativos)

    @app.get("/api/cardapios/{cardapio_id}", response_model=CardapioResponse)
    def obter_cardapio(cardapio_id: int):
        cardapio = banco.obter_cardapio(cardapio_id)
        if not cardapio:
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")
        return cardapio

    @app.put("/api/cardapios/{cardapio_id}", response_model=CardapioResponse)
    def atualizar_cardapio(cardapio_id: int, dados: CardapioRequest):
        atualizado = banco.atualizar_cardapio(
            cardapio_id, dados.model_dump(exclude_unset=True)
        )
        if not atualizado:
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")
        return atualizado

    @app.delete("/api/cardapios/{cardapio_id}", status_code=204)
    def deletar_cardapio(cardapio_id: int):
        if not banco.deletar_cardapio(cardapio_id):
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")

    return app
