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


class TestCategoriaAPI:
    @pytest.fixture
    def cardapio_id(self, cliente):
        return cliente.post(
            "/api/cardapios", json={"nome": "Cardápio Teste"}
        ).json()["id"]

    def test_criar_categoria(self, cliente, cardapio_id):
        resposta = cliente.post(
            "/api/categorias", json={"nome": "Entradas", "cardapio_id": cardapio_id}
        )
        assert resposta.status_code == 201
        dados = resposta.json()
        assert dados["nome"] == "Entradas"
        assert "id" in dados

    def test_criar_categoria_sem_cardapio(self, cliente):
        resposta = cliente.post(
            "/api/categorias", json={"nome": "Entradas", "cardapio_id": 999}
        )
        assert resposta.status_code == 404

    def test_criar_categoria_nome_vazio(self, cliente, cardapio_id):
        resposta = cliente.post(
            "/api/categorias", json={"nome": "", "cardapio_id": cardapio_id}
        )
        assert resposta.status_code == 422

    def test_listar_categorias(self, cliente, cardapio_id):
        cliente.post(
            "/api/categorias", json={"nome": "Entradas", "cardapio_id": cardapio_id}
        )
        cliente.post(
            "/api/categorias", json={"nome": "Bebidas", "cardapio_id": cardapio_id}
        )
        resposta = cliente.get(f"/api/cardapios/{cardapio_id}/categorias")
        assert resposta.status_code == 200
        dados = resposta.json()
        assert len(dados) == 2

    def test_obter_categoria(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/categorias", json={"nome": "Sobremesas", "cardapio_id": cardapio_id}
        ).json()
        resposta = cliente.get(f"/api/categorias/{criada['id']}")
        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Sobremesas"

    def test_obter_categoria_inexistente(self, cliente):
        resposta = cliente.get("/api/categorias/999")
        assert resposta.status_code == 404

    def test_atualizar_categoria(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/categorias", json={"nome": "Original", "cardapio_id": cardapio_id}
        ).json()
        resposta = cliente.put(
            f"/api/categorias/{criada['id']}", json={"nome": "Modificada"}
        )
        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Modificada"

    def test_atualizar_categoria_inexistente(self, cliente):
        resposta = cliente.put("/api/categorias/999", json={"nome": "X"})
        assert resposta.status_code == 404

    def test_deletar_categoria(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/categorias", json={"nome": "Temp", "cardapio_id": cardapio_id}
        ).json()
        resposta = cliente.delete(f"/api/categorias/{criada['id']}")
        assert resposta.status_code == 204
        obtida = cliente.get(f"/api/categorias/{criada['id']}")
        assert obtida.status_code == 404

    def test_deletar_categoria_inexistente(self, cliente):
        resposta = cliente.delete("/api/categorias/999")
        assert resposta.status_code == 404


class TestItemAPI:
    @pytest.fixture
    def categoria_id(self, cliente):
        cardapio = cliente.post(
            "/api/cardapios", json={"nome": "Cardápio"}
        ).json()
        return cliente.post(
            "/api/categorias",
            json={"nome": "Entradas", "cardapio_id": cardapio["id"]},
        ).json()["id"]

    def test_criar_item(self, cliente, categoria_id):
        resposta = cliente.post(
            "/api/itens",
            json={"nome": "Hambúrguer", "preco": 29.90, "categoria_id": categoria_id},
        )
        assert resposta.status_code == 201
        dados = resposta.json()
        assert dados["nome"] == "Hambúrguer"
        assert dados["preco"] == 29.90
        assert "id" in dados

    def test_criar_item_sem_categoria(self, cliente):
        resposta = cliente.post(
            "/api/itens", json={"nome": "Teste", "preco": 10, "categoria_id": 999}
        )
        assert resposta.status_code == 404

    def test_criar_item_nome_vazio(self, cliente, categoria_id):
        resposta = cliente.post(
            "/api/itens",
            json={"nome": "", "preco": 10, "categoria_id": categoria_id},
        )
        assert resposta.status_code == 422

    def test_listar_itens_por_categoria(self, cliente, categoria_id):
        cliente.post(
            "/api/itens",
            json={"nome": "Item A", "preco": 10, "categoria_id": categoria_id},
        )
        cliente.post(
            "/api/itens",
            json={"nome": "Item B", "preco": 20, "categoria_id": categoria_id},
        )
        resposta = cliente.get(f"/api/categorias/{categoria_id}/itens")
        assert resposta.status_code == 200
        assert len(resposta.json()) == 2

    def test_obter_item(self, cliente, categoria_id):
        criado = cliente.post(
            "/api/itens",
            json={"nome": "Pizza", "preco": 49.90, "categoria_id": categoria_id},
        ).json()
        resposta = cliente.get(f"/api/itens/{criado['id']}")
        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Pizza"

    def test_obter_item_inexistente(self, cliente):
        resposta = cliente.get("/api/itens/999")
        assert resposta.status_code == 404

    def test_atualizar_item(self, cliente, categoria_id):
        criado = cliente.post(
            "/api/itens",
            json={"nome": "Original", "preco": 10, "categoria_id": categoria_id},
        ).json()
        resposta = cliente.put(
            f"/api/itens/{criado['id']}", json={"preco": 15.50}
        )
        assert resposta.status_code == 200
        assert resposta.json()["preco"] == 15.50

    def test_atualizar_item_inexistente(self, cliente):
        resposta = cliente.put("/api/itens/999", json={"nome": "X"})
        assert resposta.status_code == 404

    def test_deletar_item(self, cliente, categoria_id):
        criado = cliente.post(
            "/api/itens",
            json={"nome": "Temp", "preco": 5, "categoria_id": categoria_id},
        ).json()
        resposta = cliente.delete(f"/api/itens/{criado['id']}")
        assert resposta.status_code == 204
        obtido = cliente.get(f"/api/itens/{criado['id']}")
        assert obtido.status_code == 404

    def test_deletar_item_inexistente(self, cliente):
        resposta = cliente.delete("/api/itens/999")
        assert resposta.status_code == 404


class TestMesaAPI:
    @pytest.fixture
    def cardapio_id(self, cliente):
        return cliente.post(
            "/api/cardapios", json={"nome": "Cardápio Teste"}
        ).json()["id"]

    def test_criar_mesa(self, cliente, cardapio_id):
        resposta = cliente.post(
            "/api/mesas", json={"identificacao": "Mesa 1", "cardapio_id": cardapio_id}
        )
        assert resposta.status_code == 201
        dados = resposta.json()
        assert dados["identificacao"] == "Mesa 1"
        assert "id" in dados

    def test_criar_mesa_identificacao_vazia(self, cliente, cardapio_id):
        resposta = cliente.post(
            "/api/mesas", json={"identificacao": "", "cardapio_id": cardapio_id}
        )
        assert resposta.status_code == 422

    def test_listar_mesas(self, cliente, cardapio_id):
        cliente.post(
            "/api/mesas", json={"identificacao": "Mesa 1", "cardapio_id": cardapio_id}
        )
        cliente.post(
            "/api/mesas", json={"identificacao": "Mesa 2", "cardapio_id": cardapio_id}
        )
        resposta = cliente.get(f"/api/cardapios/{cardapio_id}/mesas")
        assert resposta.status_code == 200
        assert len(resposta.json()) == 2

    def test_obter_mesa(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/mesas", json={"identificacao": "Balcão", "cardapio_id": cardapio_id}
        ).json()
        resposta = cliente.get(f"/api/mesas/{criada['id']}")
        assert resposta.status_code == 200
        assert resposta.json()["identificacao"] == "Balcão"

    def test_obter_mesa_inexistente(self, cliente):
        resposta = cliente.get("/api/mesas/999")
        assert resposta.status_code == 404

    def test_atualizar_mesa(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/mesas", json={"identificacao": "Mesa 1", "cardapio_id": cardapio_id}
        ).json()
        resposta = cliente.put(
            f"/api/mesas/{criada['id']}", json={"identificacao": "Mesa 1A"}
        )
        assert resposta.status_code == 200
        assert resposta.json()["identificacao"] == "Mesa 1A"

    def test_atualizar_mesa_inexistente(self, cliente):
        resposta = cliente.put("/api/mesas/999", json={"identificacao": "X"})
        assert resposta.status_code == 404

    def test_deletar_mesa(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/mesas", json={"identificacao": "Temp", "cardapio_id": cardapio_id}
        ).json()
        resposta = cliente.delete(f"/api/mesas/{criada['id']}")
        assert resposta.status_code == 204
        obtida = cliente.get(f"/api/mesas/{criada['id']}")
        assert obtida.status_code == 404

    def test_deletar_mesa_inexistente(self, cliente):
        resposta = cliente.delete("/api/mesas/999")
        assert resposta.status_code == 404
