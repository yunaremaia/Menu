from datetime import datetime, timezone
from pathlib import Path

import csv
import io

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response, PlainTextResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

from menu.armazenamento.local import ArmazenamentoLocal
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


class ItemExportar(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float
    foto_url: str | None = None
    tags: str = ""
    disponivel: bool = True
    destaque: bool = False
    ordem: int = 0


class CategoriaExportar(BaseModel):
    nome: str
    ordem: int = 0
    itens: list[ItemExportar] = []


class CardapioExportar(BaseModel):
    nome: str
    descricao: str | None = None
    ativo: bool = True
    idioma_padrao: str = "pt-BR"


class MesaExportar(BaseModel):
    identificacao: str
    ativo: bool = True


class CardapioImportar(BaseModel):
    cardapio: CardapioExportar
    categorias: list[CategoriaExportar] = []
    mesas: list[MesaExportar] = []


def criar_app(
    caminho_banco: str = "menu.db",
    base_url: str = "",
    armazenamento_dir: str = "",
) -> FastAPI:
    banco = Banco(caminho_banco)
    banco.iniciar()

    if not armazenamento_dir:
        armazenamento_dir = str(Path.cwd() / "uploads")
    storage = ArmazenamentoLocal(armazenamento_dir)

    templates_dir = Path(__file__).parent / "templates"
    templates = Environment(loader=FileSystemLoader(str(templates_dir)))

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

    @app.get("/api/cardapios/{cardapio_id}/buscar")
    def buscar_itens(cardapio_id: int, q: str = Query(min_length=1)):
        if not banco.obter_cardapio(cardapio_id):
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")
        return banco.buscar_itens(cardapio_id, q)

    @app.get("/api/cardapios/{cardapio_id}/exportar")
    def exportar_cardapio(cardapio_id: int, formato: str | None = None):
        cardapio = banco.obter_cardapio(cardapio_id)
        if not cardapio:
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")

        categorias = banco.listar_categorias(cardapio_id)
        dados_categorias = []
        for cat in categorias:
            itens = banco.listar_itens(cat.id)
            dados_categorias.append({
                "nome": cat.nome,
                "ordem": cat.ordem,
                "itens": [
                    {
                        "nome": i.nome,
                        "descricao": i.descricao,
                        "preco": i.preco,
                        "foto_url": i.foto_url,
                        "tags": i.tags,
                        "disponivel": i.disponivel,
                        "destaque": i.destaque,
                        "ordem": i.ordem,
                    }
                    for i in itens
                ],
            })

        mesas = banco.listar_mesas(cardapio_id)
        dados_mesas = [
            {"identificacao": m.identificacao, "ativo": m.ativo}
            for m in mesas
        ]

        if formato == "csv":
            saida = io.StringIO()
            escritor = csv.writer(saida)
            escritor.writerow(["categoria", "item", "descricao", "preco", "tags", "disponivel"])
            for cat in dados_categorias:
                if not cat["itens"]:
                    escritor.writerow([cat["nome"], "", "", "", "", ""])
                for item in cat["itens"]:
                    escritor.writerow([
                        cat["nome"],
                        item["nome"],
                        item["descricao"] or "",
                        f"{item['preco']:.2f}",
                        item["tags"],
                        "sim" if item["disponivel"] else "nao",
                    ])
            return PlainTextResponse(
                content=saida.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f'attachment; filename="cardapio_{cardapio_id}.csv"'},
            )
        elif formato is not None and formato != "json":
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {formato}. Use 'json' ou 'csv'.",
            )

        return {
            "cardapio": {
                "nome": cardapio.nome,
                "descricao": cardapio.descricao,
                "ativo": cardapio.ativo,
                "idioma_padrao": cardapio.idioma_padrao,
            },
            "categorias": dados_categorias,
            "mesas": dados_mesas,
        }

    @app.post("/api/cardapios/importar", status_code=201)
    def importar_cardapio(dados: CardapioImportar):
        cardapio_dados = dados.cardapio
        cardapio = Cardapio(
            nome=cardapio_dados.nome,
            descricao=cardapio_dados.descricao,
            ativo=cardapio_dados.ativo,
            idioma_padrao=cardapio_dados.idioma_padrao,
            criado_em=datetime.now(timezone.utc),
            atualizado_em=datetime.now(timezone.utc),
        )
        cardapio_criado = banco.criar_cardapio(cardapio)

        mapa_categorias = {}
        for cat_dados in dados.categorias:
            categoria = Categoria(
                nome=cat_dados.nome,
                cardapio_id=cardapio_criado.id,
                ordem=cat_dados.ordem,
                criado_em=datetime.now(timezone.utc),
            )
            cat_criada = banco.criar_categoria(categoria)
            mapa_categorias[cat_dados.nome] = cat_criada.id

            for item_dados in cat_dados.itens:
                item = Item(
                    nome=item_dados.nome,
                    descricao=item_dados.descricao,
                    preco=item_dados.preco,
                    foto_url=item_dados.foto_url,
                    tags=item_dados.tags,
                    disponivel=item_dados.disponivel,
                    destaque=item_dados.destaque,
                    ordem=item_dados.ordem,
                    categoria_id=cat_criada.id,
                    criado_em=datetime.now(timezone.utc),
                    atualizado_em=datetime.now(timezone.utc),
                )
                banco.criar_item(item)

        for mesa_dados in dados.mesas:
            mesa = Mesa(
                identificacao=mesa_dados.identificacao,
                cardapio_id=cardapio_criado.id,
                ativo=mesa_dados.ativo,
                criado_em=datetime.now(timezone.utc),
            )
            banco.criar_mesa(mesa)

        return {"id": cardapio_criado.id}

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

    @app.post("/api/itens/{item_id}/foto")
    def upload_foto(item_id: int, arquivo: UploadFile):
        item = banco.obter_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado")

        extensao = Path(arquivo.filename or "").suffix.lower()
        if extensao not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            raise HTTPException(
                status_code=400,
                detail="Formato não permitido. Use PNG, JPG, GIF ou WebP.",
            )

        if item.foto_url:
            try:
                storage.remover(item.foto_url)
            except Exception:
                pass

        dados = arquivo.file.read()
        url = storage.salvar(dados, extensao)
        banco.atualizar_item(item_id, {"foto_url": url})
        return {"foto_url": url}

    @app.get("/arquivos/{nome_arquivo}")
    def servir_arquivo(nome_arquivo: str):
        caminho = storage.obter_caminho(nome_arquivo)
        if not caminho:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        return FileResponse(str(caminho))

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

    @app.get("/cardapio/{cardapio_id}", response_class=HTMLResponse)
    def exibir_cardapio(cardapio_id: int, mesa: int | None = None):
        cardapio = banco.obter_cardapio(cardapio_id)
        if not cardapio:
            raise HTTPException(status_code=404, detail="Cardápio não encontrado")

        categorias = banco.listar_categorias(cardapio_id)
        dados_categorias = []
        for cat in categorias:
            itens = banco.listar_itens(cat.id, apenas_disponiveis=True)
            dados_categorias.append({
                "nome": cat.nome,
                "ordem": cat.ordem,
                "itens": itens,
            })

        dados_mesa = None
        if mesa:
            m = banco.obter_mesa(mesa)
            if m and m.cardapio_id == cardapio_id:
                dados_mesa = m

        html = templates.get_template("cardapio.html").render(
            cardapio=cardapio,
            categorias=dados_categorias,
            mesa=dados_mesa,
        )
        return HTMLResponse(content=html)

    @app.get("/api/mesas/{mesa_id}/qrcode")
    def obter_qrcode_mesa(mesa_id: int):
        mesa = banco.obter_mesa(mesa_id)
        if not mesa:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
        url_destino = f"{base_url}/cardapio/{mesa.cardapio_id}?mesa={mesa_id}"
        imagem = gerar_qrcode(url_destino)
        return Response(content=imagem, media_type="image/png")

    return app
