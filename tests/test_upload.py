import io
import struct
import zlib

import pytest
from fastapi.testclient import TestClient

from menu.api.app import criar_app


def _png_1x1() -> bytes:
    """Gera um PNG válido de 1x1 pixel."""
    def chunk(tipo: bytes, dados: bytes) -> bytes:
        comprimento = struct.pack(">I", len(dados))
        crc = struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
        return comprimento + tipo + dados + crc

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"x\x01\x01\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\xff\xff"
    idat = zlib.compress(raw)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


@pytest.fixture
def cliente():
    app = criar_app(caminho_banco=":memory:")
    with TestClient(app) as c:
        yield c


@pytest.fixture
def item_id(cliente):
    resp = cliente.post("/api/cardapios", json={"nome": "Cardápio Teste"})
    cardapio_id = resp.json()["id"]
    resp = cliente.post(
        "/api/categorias",
        json={"nome": "Entradas", "cardapio_id": cardapio_id},
    )
    cat_id = resp.json()["id"]
    resp = cliente.post(
        "/api/itens",
        json={"nome": "Bruschetta", "preco": 19.90, "categoria_id": cat_id},
    )
    return resp.json()["id"]


class TestUploadFoto:
    def test_upload_foto_retorna_200(self, cliente, item_id):
        img = _png_1x1()
        resposta = cliente.post(
            f"/api/itens/{item_id}/foto",
            files={"arquivo": ("foto.png", img, "image/png")},
        )
        assert resposta.status_code == 200

    def test_upload_foto_atualiza_foto_url(self, cliente, item_id):
        img = _png_1x1()
        cliente.post(
            f"/api/itens/{item_id}/foto",
            files={"arquivo": ("foto.png", img, "image/png")},
        )
        item = cliente.get(f"/api/itens/{item_id}").json()
        assert item["foto_url"] is not None
        assert item["foto_url"].endswith(".png")

    def test_upload_foto_arquivo_servido(self, cliente, item_id):
        img = _png_1x1()
        cliente.post(
            f"/api/itens/{item_id}/foto",
            files={"arquivo": ("foto.png", img, "image/png")},
        )
        item = cliente.get(f"/api/itens/{item_id}").json()
        url = item["foto_url"]
        resposta = cliente.get(url)
        assert resposta.status_code == 200
        assert resposta.headers["content-type"] in ("image/png", "image/png; charset=utf-8")

    def test_upload_foto_item_inexistente(self, cliente):
        img = _png_1x1()
        resposta = cliente.post(
            "/api/itens/999/foto",
            files={"arquivo": ("foto.png", img, "image/png")},
        )
        assert resposta.status_code == 404

    def test_upload_arquivo_nao_imagem_rejeitado(self, cliente, item_id):
        resposta = cliente.post(
            f"/api/itens/{item_id}/foto",
            files={"arquivo": ("texto.txt", b"nao sou imagem", "text/plain")},
        )
        assert resposta.status_code == 400

    def test_upload_substitui_foto_anterior(self, cliente, item_id):
        img1 = _png_1x1()
        img2 = _png_1x1()
        cliente.post(
            f"/api/itens/{item_id}/foto",
            files={"arquivo": ("foto1.png", img1, "image/png")},
        )
        resp1 = cliente.get(f"/api/itens/{item_id}").json()
        cliente.post(
            f"/api/itens/{item_id}/foto",
            files={"arquivo": ("foto2.png", img2, "image/png")},
        )
        resp2 = cliente.get(f"/api/itens/{item_id}").json()
        assert resp1["foto_url"] != resp2["foto_url"]

    def test_upload_sem_arquivo_retorna_422(self, cliente, item_id):
        resposta = cliente.post(f"/api/itens/{item_id}/foto")
        assert resposta.status_code == 422
