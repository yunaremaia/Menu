import pytest
from fastapi.testclient import TestClient

from menu.api.app import criar_app


@pytest.fixture
def cliente():
    app = criar_app(caminho_banco=":memory:")
    with TestClient(app) as c:
        yield c


@pytest.fixture
def cardapio_id(cliente):
    resp = cliente.post("/api/cardapios", json={"nome": "Cardápio Teste"})
    return resp.json()["id"]


@pytest.fixture
def dados_completos(cliente, cardapio_id):
    resp = cliente.post(
        "/api/categorias",
        json={"nome": "Entradas", "cardapio_id": cardapio_id, "ordem": 1},
    )
    cat1 = resp.json()["id"]
    resp = cliente.post(
        "/api/categorias",
        json={"nome": "Bebidas", "cardapio_id": cardapio_id, "ordem": 2},
    )
    cat2 = resp.json()["id"]

    cliente.post(
        "/api/itens",
        json={
            "nome": "Bruschetta",
            "descricao": "Pão com tomate e manjericão",
            "preco": 19.90,
            "categoria_id": cat1,
            "tags": "vegano",
        },
    )
    cliente.post(
        "/api/itens",
        json={
            "nome": "Suco de Laranja",
            "descricao": "Suco natural",
            "preco": 8.50,
            "categoria_id": cat2,
        },
    )
    return cardapio_id


class TestBuscarItensAPI:
    def test_buscar_retorna_200(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=bruschetta")
        assert resp.status_code == 200

    def test_buscar_retorna_lista(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=bruschetta")
        dados = resp.json()
        assert isinstance(dados, list)
        assert len(dados) == 1

    def test_buscar_contem_item_e_categoria(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=bruschetta")
        item = resp.json()[0]
        assert item["item"]["nome"] == "Bruschetta"
        assert item["categoria"] == "Entradas"

    def test_buscar_sem_resultado(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=sushi")
        assert resp.json() == []

    def test_buscar_ignora_maiusculas(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=BRUSCHETTA")
        assert len(resp.json()) == 1

    def test_buscar_por_tag(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=vegano")
        assert len(resp.json()) == 1

    def test_buscar_sem_query_retorna_422(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar")
        assert resp.status_code == 422

    def test_buscar_query_vazia_retorna_422(self, cliente, dados_completos):
        resp = cliente.get(f"/api/cardapios/{dados_completos}/buscar?q=")
        assert resp.status_code == 422

    def test_buscar_cardapio_inexistente(self, cliente):
        resp = cliente.get("/api/cardapios/999/buscar?q=teste")
        assert resp.status_code == 404
