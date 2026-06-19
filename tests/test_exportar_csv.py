import csv
import io

import pytest
from fastapi.testclient import TestClient

from menu.api.app import criar_app


@pytest.fixture
def cliente():
    app = criar_app(caminho_banco=":memory:")
    with TestClient(app) as c:
        yield c


@pytest.fixture
def cardapio_completo(cliente):
    resp = cliente.post(
        "/api/cardapios", json={"nome": "Cardápio Teste"}
    )
    cid = resp.json()["id"]

    resp = cliente.post(
        "/api/categorias",
        json={"nome": "Entradas", "cardapio_id": cid, "ordem": 1},
    )
    cat1 = resp.json()["id"]

    resp = cliente.post(
        "/api/categorias",
        json={"nome": "Bebidas", "cardapio_id": cid, "ordem": 2},
    )
    cat2 = resp.json()["id"]

    cliente.post(
        "/api/itens",
        json={
            "nome": "Bruschetta",
            "descricao": "Pão com tomate",
            "preco": 19.90,
            "categoria_id": cat1,
            "tags": "vegano",
        },
    )
    cliente.post(
        "/api/itens",
        json={
            "nome": "Suco de Laranja",
            "preco": 8.50,
            "categoria_id": cat2,
        },
    )

    cliente.post(
        "/api/mesas",
        json={"identificacao": "Mesa 1", "cardapio_id": cid},
    )

    return cid


class TestExportarCSV:
    def test_exportar_csv_retorna_200(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        assert resp.status_code == 200

    def test_exportar_csv_content_type(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        assert "text/csv" in resp.headers["content-type"]

    def test_exportar_csv_tem_cabecalho(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        linhas = resp.text.strip().split("\n")
        cabecalho = linhas[0]
        assert "categoria" in cabecalho.lower()
        assert "item" in cabecalho.lower()
        assert "preco" in cabecalho.lower()

    def test_exportar_csv_contem_itens(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        leitor = csv.DictReader(io.StringIO(resp.text))
        linhas = list(leitor)
        nomes = [l["item"] for l in linhas]
        assert "Bruschetta" in nomes
        assert "Suco de Laranja" in nomes

    def test_exportar_csv_contem_categoria(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        leitor = csv.DictReader(io.StringIO(resp.text))
        categorias = {l["categoria"] for l in leitor}
        assert "Entradas" in categorias
        assert "Bebidas" in categorias

    def test_exportar_csv_preco_formatado(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        leitor = csv.DictReader(io.StringIO(resp.text))
        precos = {l["item"]: l["preco"] for l in leitor}
        assert precos["Bruschetta"] == "19.90"
        assert precos["Suco de Laranja"] == "8.50"

    def test_exportar_csv_contem_tags(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=csv"
        )
        leitor = csv.DictReader(io.StringIO(resp.text))
        for l in leitor:
            if l["item"] == "Bruschetta":
                assert "vegano" in l.get("tags", "")

    def test_exportar_csv_cardapio_vazio(self, cliente):
        resp = cliente.post("/api/cardapios", json={"nome": "Vazio"})
        cid = resp.json()["id"]
        resp = cliente.get(
            f"/api/cardapios/{cid}/exportar?formato=csv"
        )
        assert resp.status_code == 200
        linhas = resp.text.strip().split("\n")
        assert len(linhas) == 1

    def test_exportar_csv_cardapio_inexistente(self, cliente):
        resp = cliente.get("/api/cardapios/999/exportar?formato=csv")
        assert resp.status_code == 404

    def test_exportar_formato_invalido(self, cliente, cardapio_completo):
        resp = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar?formato=xml"
        )
        assert resp.status_code == 400
