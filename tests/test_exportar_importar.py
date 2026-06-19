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
        "/api/cardapios", json={"nome": "Cardápio Export", "descricao": "Teste"}
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
    cliente.post(
        "/api/mesas",
        json={"identificacao": "Mesa 2", "cardapio_id": cid},
    )

    return cid


class TestExportarCardapio:
    def test_exportar_retorna_200(self, cliente, cardapio_completo):
        resp = cliente.get(f"/api/cardapios/{cardapio_completo}/exportar")
        assert resp.status_code == 200

    def test_exportar_contem_cardapio(self, cliente, cardapio_completo):
        dados = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        assert dados["cardapio"]["nome"] == "Cardápio Export"
        assert dados["cardapio"]["descricao"] == "Teste"

    def test_exportar_contem_categorias(self, cliente, cardapio_completo):
        dados = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        nomes = [c["nome"] for c in dados["categorias"]]
        assert "Entradas" in nomes
        assert "Bebidas" in nomes

    def test_exportar_categorias_ordenadas(self, cliente, cardapio_completo):
        dados = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        ordens = [c["ordem"] for c in dados["categorias"]]
        assert ordens == sorted(ordens)

    def test_exportar_contem_itens_nas_categorias(self, cliente, cardapio_completo):
        dados = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        itens_entradas = [
            i
            for c in dados["categorias"]
            if c["nome"] == "Entradas"
            for i in c["itens"]
        ]
        assert any(i["nome"] == "Bruschetta" for i in itens_entradas)
        assert any(i["preco"] == 19.90 for i in itens_entradas)

    def test_exportar_contem_mesas(self, cliente, cardapio_completo):
        dados = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        identificacoes = [m["identificacao"] for m in dados["mesas"]]
        assert "Mesa 1" in identificacoes
        assert "Mesa 2" in identificacoes

    def test_exportar_cardapio_inexistente(self, cliente):
        resp = cliente.get("/api/cardapios/999/exportar")
        assert resp.status_code == 404

    def test_exportar_sem_categorias(self, cliente):
        resp = cliente.post("/api/cardapios", json={"nome": "Vazio"})
        cid = resp.json()["id"]
        dados = cliente.get(f"/api/cardapios/{cid}/exportar").json()
        assert dados["categorias"] == []
        assert dados["mesas"] == []


class TestImportarCardapio:
    def test_importar_retorna_201(self, cliente, cardapio_completo):
        exportado = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        resp = cliente.post("/api/cardapios/importar", json=exportado)
        assert resp.status_code == 201

    def test_importar_cria_cardapio(self, cliente, cardapio_completo):
        exportado = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        resp = cliente.post("/api/cardapios/importar", json=exportado)
        cid = resp.json()["id"]
        cardapio = cliente.get(f"/api/cardapios/{cid}").json()
        assert cardapio["nome"] == "Cardápio Export"

    def test_importar_cria_categorias(self, cliente, cardapio_completo):
        exportado = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        resp = cliente.post("/api/cardapios/importar", json=exportado)
        cid = resp.json()["id"]
        cats = cliente.get(f"/api/cardapios/{cid}/categorias").json()
        assert len(cats) == 2

    def test_importar_cria_itens(self, cliente, cardapio_completo):
        exportado = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        resp = cliente.post("/api/cardapios/importar", json=exportado)
        cid = resp.json()["id"]
        cats = cliente.get(f"/api/cardapios/{cid}/categorias").json()
        total_itens = sum(
            len(
                cliente.get(
                    f"/api/categorias/{cat['id']}/itens"
                ).json()
            )
            for cat in cats
        )
        assert total_itens == 2

    def test_importar_cria_mesas(self, cliente, cardapio_completo):
        exportado = cliente.get(
            f"/api/cardapios/{cardapio_completo}/exportar"
        ).json()
        resp = cliente.post("/api/cardapios/importar", json=exportado)
        cid = resp.json()["id"]
        mesas = cliente.get(f"/api/cardapios/{cid}/mesas").json()
        assert len(mesas) == 2

    def test_importar_dados_invalidos(self, cliente):
        resp = cliente.post(
            "/api/cardapios/importar", json={"invalido": True}
        )
        assert resp.status_code == 422

    def test_importar_sem_categorias(self, cliente):
        dados = {
            "cardapio": {"nome": "Simples"},
            "categorias": [],
            "mesas": [],
        }
        resp = cliente.post("/api/cardapios/importar", json=dados)
        assert resp.status_code == 201
        cid = resp.json()["id"]
        cats = cliente.get(f"/api/cardapios/{cid}/categorias").json()
        assert cats == []
