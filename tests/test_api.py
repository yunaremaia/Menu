import pytest
from fastapi.testclient import TestClient

from menu.api.app import criar_app


@pytest.fixture
def cliente():
    app = criar_app(caminho_banco=":memory:")
    with TestClient(app) as c:
        yield c


class TestCardapioAPI:
    def test_criar_cardapio(self, cliente):
        resposta = cliente.post("/api/cardapios", json={"nome": "Cardápio do Dia"})
        assert resposta.status_code == 201
        dados = resposta.json()
        assert dados["nome"] == "Cardápio do Dia"
        assert dados["ativo"] is True
        assert "id" in dados

    def test_criar_cardapio_nome_vazio(self, cliente):
        resposta = cliente.post("/api/cardapios", json={"nome": ""})
        assert resposta.status_code == 422

    def test_listar_cardapios_vazio(self, cliente):
        resposta = cliente.get("/api/cardapios")
        assert resposta.status_code == 200
        assert resposta.json() == []

    def test_listar_cardapios(self, cliente):
        cliente.post("/api/cardapios", json={"nome": "Cardápio A"})
        cliente.post("/api/cardapios", json={"nome": "Cardápio B"})
        resposta = cliente.get("/api/cardapios")
        assert resposta.status_code == 200
        dados = resposta.json()
        assert len(dados) == 2

    def test_obter_cardapio(self, cliente):
        criado = cliente.post("/api/cardapios", json={"nome": "Meu Cardápio"}).json()
        resposta = cliente.get(f"/api/cardapios/{criado['id']}")
        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Meu Cardápio"

    def test_obter_cardapio_inexistente(self, cliente):
        resposta = cliente.get("/api/cardapios/999")
        assert resposta.status_code == 404

    def test_atualizar_cardapio(self, cliente):
        criado = cliente.post("/api/cardapios", json={"nome": "Original"}).json()
        resposta = cliente.put(
            f"/api/cardapios/{criado['id']}", json={"nome": "Atualizado"}
        )
        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Atualizado"

    def test_atualizar_cardapio_inexistente(self, cliente):
        resposta = cliente.put("/api/cardapios/999", json={"nome": "Nope"})
        assert resposta.status_code == 404

    def test_deletar_cardapio(self, cliente):
        criado = cliente.post("/api/cardapios", json={"nome": "Temporário"}).json()
        resposta = cliente.delete(f"/api/cardapios/{criado['id']}")
        assert resposta.status_code == 204
        obtido = cliente.get(f"/api/cardapios/{criado['id']}")
        assert obtido.status_code == 404

    def test_deletar_cardapio_inexistente(self, cliente):
        resposta = cliente.delete("/api/cardapios/999")
        assert resposta.status_code == 404

    def test_criar_cardapio_completo(self, cliente):
        resposta = cliente.post(
            "/api/cardapios",
            json={
                "nome": "Happy Hour",
                "descricao": "Promoções após 18h",
                "ativo": False,
                "idioma_padrao": "en",
            },
        )
        assert resposta.status_code == 201
        dados = resposta.json()
        assert dados["nome"] == "Happy Hour"
        assert dados["descricao"] == "Promoções após 18h"
        assert dados["ativo"] is False
        assert dados["idioma_padrao"] == "en"

    def test_listar_apenas_ativos(self, cliente):
        cliente.post("/api/cardapios", json={"nome": "Ativo"})
        cliente.post("/api/cardapios", json={"nome": "Inativo", "ativo": False})
        resposta = cliente.get("/api/cardapios?apenas_ativos=true")
        assert resposta.status_code == 200
        dados = resposta.json()
        assert len(dados) == 1
        assert dados[0]["nome"] == "Ativo"
