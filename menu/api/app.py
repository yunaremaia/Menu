from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fastapi.responses import Response

from menu.modelos import Cardapio, Categoria, Item, Mesa
from menu.qrcode.gerador import gerar_qrcode
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


class CategoriaCriar(BaseModel):
    nome: str = Field(min_length=1)
    cardapio_id: int = Field(gt=0)
    ordem: int = Field(default=0, ge=0)


class CategoriaAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    ordem: int | None = Field(default=None, ge=0)


class CategoriaResponse(BaseModel):
    id: int
    nome: str
    cardapio_id: int
    ordem: int
    criado_em: datetime


class ItemCriar(BaseModel):
    nome: str = Field(min_length=1)
    descricao: str | None = None
    preco: float = Field(ge=0)
    foto_url: str | None = None
    tags: str = ""
    disponivel: bool = True
    destaque: bool = False
    ordem: int = Field(default=0, ge=0)
    categoria_id: int = Field(gt=0)


class ItemAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    descricao: str | None = None
    preco: float | None = Field(default=None, ge=0)
    foto_url: str | None = None
    tags: str | None = None
    disponivel: bool | None = None
    destaque: bool | None = None
    ordem: int | None = Field(default=None, ge=0)
    categoria_id: int | None = Field(default=None, gt=0)


class ItemResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    preco: float
    foto_url: str | None
    tags: str
    disponivel: bool
    destaque: bool
    ordem: int
    categoria_id: int
    criado_em: datetime
    atualizado_em: datetime


class MesaCriar(BaseModel):
    identificacao: str = Field(min_length=1)
    cardapio_id: int = Field(gt=0)
    ativo: bool = True


class MesaAtualizar(BaseModel):
    identificacao: str | None = Field(default=None, min_length=1)
    ativo: bool | None = None


class MesaResponse(BaseModel):
    id: int
    identificacao: str
    cardapio_id: int
    ativo: bool
    criado_em: datetime


def criar_app(caminho_banco: str = "menu.db", base_url: str = "") -> FastAPI:
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

    @app.post("/api/categorias", response_model=CategoriaResponse, status_code=201)
    def criar_categoria(dados: CategoriaCriar):
        if not banco.obter_cardapio(dados.cardapio_id):
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")
        categoria = Categoria(
            nome=dados.nome,
            cardapio_id=dados.cardapio_id,
            ordem=dados.ordem,
            criado_em=datetime.now(timezone.utc),
        )
        return banco.criar_categoria(categoria)

    @app.get(
        "/api/cardapios/{cardapio_id}/categorias",
        response_model=list[CategoriaResponse],
    )
    def listar_categorias(cardapio_id: int):
        return banco.listar_categorias(cardapio_id)

    @app.get("/api/categorias/{categoria_id}", response_model=CategoriaResponse)
    def obter_categoria(categoria_id: int):
        categoria = banco.obter_categoria(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        return categoria

    @app.put("/api/categorias/{categoria_id}", response_model=CategoriaResponse)
    def atualizar_categoria(categoria_id: int, dados: CategoriaAtualizar):
        atualizada = banco.atualizar_categoria(
            categoria_id, dados.model_dump(exclude_unset=True)
        )
        if not atualizada:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        return atualizada

    @app.delete("/api/categorias/{categoria_id}", status_code=204)
    def deletar_categoria(categoria_id: int):
        if not banco.deletar_categoria(categoria_id):
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

    @app.post("/api/itens", response_model=ItemResponse, status_code=201)
    def criar_item(dados: ItemCriar):
        if not banco.obter_categoria(dados.categoria_id):
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        item = Item(
            nome=dados.nome,
            descricao=dados.descricao,
            preco=dados.preco,
            foto_url=dados.foto_url,
            tags=dados.tags,
            disponivel=dados.disponivel,
            destaque=dados.destaque,
            ordem=dados.ordem,
            categoria_id=dados.categoria_id,
            criado_em=datetime.now(timezone.utc),
            atualizado_em=datetime.now(timezone.utc),
        )
        return banco.criar_item(item)

    @app.get(
        "/api/categorias/{categoria_id}/itens",
        response_model=list[ItemResponse],
    )
    def listar_itens(categoria_id: int, apenas_disponiveis: bool = False):
        return banco.listar_itens(categoria_id, apenas_disponiveis=apenas_disponiveis)

    @app.get("/api/itens/{item_id}", response_model=ItemResponse)
    def obter_item(item_id: int):
        item = banco.obter_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return item

    @app.put("/api/itens/{item_id}", response_model=ItemResponse)
    def atualizar_item(item_id: int, dados: ItemAtualizar):
        atualizado = banco.atualizar_item(
            item_id, dados.model_dump(exclude_unset=True)
        )
        if not atualizado:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return atualizado

    @app.delete("/api/itens/{item_id}", status_code=204)
    def deletar_item(item_id: int):
        if not banco.deletar_item(item_id):
            raise HTTPException(status_code=404, detail="Item não encontrado")

    @app.post("/api/mesas", response_model=MesaResponse, status_code=201)
    def criar_mesa(dados: MesaCriar):
        if not banco.obter_cardapio(dados.cardapio_id):
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")
        mesa = Mesa(
            identificacao=dados.identificacao,
            cardapio_id=dados.cardapio_id,
            ativo=dados.ativo,
            criado_em=datetime.now(timezone.utc),
        )
        return banco.criar_mesa(mesa)

    @app.get(
        "/api/cardapios/{cardapio_id}/mesas",
        response_model=list[MesaResponse],
    )
    def listar_mesas(cardapio_id: int, apenas_ativas: bool = False):
        return banco.listar_mesas(cardapio_id, apenas_ativas=apenas_ativas)

    @app.get("/api/mesas/{mesa_id}", response_model=MesaResponse)
    def obter_mesa(mesa_id: int):
        mesa = banco.obter_mesa(mesa_id)
        if not mesa:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
        return mesa

    @app.put("/api/mesas/{mesa_id}", response_model=MesaResponse)
    def atualizar_mesa(mesa_id: int, dados: MesaAtualizar):
        atualizada = banco.atualizar_mesa(
            mesa_id, dados.model_dump(exclude_unset=True)
        )
        if not atualizada:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
        return atualizada

    @app.delete("/api/mesas/{mesa_id}", status_code=204)
    def deletar_mesa(mesa_id: int):
        if not banco.deletar_mesa(mesa_id):
            raise HTTPException(status_code=404, detail="Mesa não encontrada")

    @app.get("/api/mesas/{mesa_id}/qrcode")
    def obter_qrcode_mesa(mesa_id: int):
        mesa = banco.obter_mesa(mesa_id)
        if not mesa:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
        url_destino = f"{base_url}/cardapio/{mesa.cardapio_id}?mesa={mesa_id}"
        imagem = gerar_qrcode(url_destino)
        return Response(content=imagem, media_type="image/png")

    return app
