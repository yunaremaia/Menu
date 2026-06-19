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
    return cliente.post(
        "/api/cardapios", json={"nome": "Cardápio Teste"}
    ).json()["id"]


@pytest.fixture
def mesa_id(cliente, cardapio_id):
    return cliente.post(
        "/api/mesas",
        json={"identificacao": "Mesa 1", "cardapio_id": cardapio_id},
    ).json()["id"]


class TestQRCodeAPI:
    def test_gerar_qrcode_retorna_png(self, cliente, mesa_id):
        resposta = cliente.get(f"/api/mesas/{mesa_id}/qrcode")
        assert resposta.status_code == 200
        assert resposta.headers["content-type"] == "image/png"
        assert len(resposta.content) > 0

    def test_gerar_qrcode_e_png_valido(self, cliente, mesa_id):
        resposta = cliente.get(f"/api/mesas/{mesa_id}/qrcode")
        assert resposta.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_gerar_qrcode_mesa_inexistente(self, cliente):
        resposta = cliente.get("/api/mesas/999/qrcode")
        assert resposta.status_code == 404

    def test_gerar_qrcode_mesa_inativa(self, cliente, cardapio_id):
        criada = cliente.post(
            "/api/mesas",
            json={"identificacao": "Inativa", "cardapio_id": cardapio_id, "ativo": False},
        ).json()
        resposta = cliente.get(f"/api/mesas/{criada['id']}/qrcode")
        assert resposta.status_code == 200

    def test_gerar_qrcode_mesas_diferentes_produzem_qr_diferentes(
        self, cliente, cardapio_id
    ):
        m1 = cliente.post(
            "/api/mesas", json={"identificacao": "M1", "cardapio_id": cardapio_id}
        ).json()
        m2 = cliente.post(
            "/api/mesas", json={"identificacao": "M2", "cardapio_id": cardapio_id}
        ).json()
        qr1 = cliente.get(f"/api/mesas/{m1['id']}/qrcode").content
        qr2 = cliente.get(f"/api/mesas/{m2['id']}/qrcode").content
        assert qr1 != qr2
