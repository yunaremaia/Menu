from fastapi.testclient import TestClient

from menu.api.app import criar_app


class TestCardapioWeb:
    def _cliente_com_dados(self):
        app = criar_app(caminho_banco=":memory:")
        with TestClient(app) as c:
            resp = c.post("/api/cardapios", json={"nome": "Cardápio Teste"})
            cardapio_id = resp.json()["id"]

            resp = c.post(
                "/api/categorias",
                json={"nome": "Entradas", "cardapio_id": cardapio_id, "ordem": 1},
            )
            cat_id = resp.json()["id"]

            c.post(
                "/api/categorias",
                json={"nome": "Bebidas", "cardapio_id": cardapio_id, "ordem": 2},
            )

            c.post(
                "/api/itens",
                json={
                    "nome": "Bruschetta",
                    "descricao": "Pão com tomate",
                    "preco": 19.90,
                    "categoria_id": cat_id,
                    "tags": "vegano",
                },
            )
            c.post(
                "/api/itens",
                json={
                    "nome": "Item Indisponível",
                    "descricao": "Esgotado",
                    "preco": 10.0,
                    "categoria_id": cat_id,
                    "disponivel": False,
                },
            )

            c.post(
                "/api/mesas",
                json={"identificacao": "Mesa 5", "cardapio_id": cardapio_id},
            )

            yield c, cardapio_id

    def test_pagina_retorna_200_e_html(self):
        for c, cardapio_id in self._cliente_com_dados():
            resposta = c.get(f"/cardapio/{cardapio_id}")
            assert resposta.status_code == 200
            assert resposta.headers["content-type"] == "text/html; charset=utf-8"

    def test_pagina_contem_nome_do_cardapio(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}").text
            assert "Cardápio Teste" in html

    def test_pagina_contem_categorias(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}").text
            assert "Entradas" in html
            assert "Bebidas" in html

    def test_pagina_contem_itens_disponiveis(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}").text
            assert "Bruschetta" in html
            assert "19,90" in html or "19.90" in html
            assert "Pão com tomate" in html

    def test_pagina_nao_mostra_itens_indisponiveis(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}").text
            assert "Item Indisponível" not in html
            assert "Esgotado" not in html

    def test_pagina_com_mesa_na_query(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}?mesa=1").text
            assert "Mesa" in html

    def test_pagina_404_para_cardapio_inexistente(self):
        app = criar_app(caminho_banco=":memory:")
        with TestClient(app) as c:
            resposta = c.get("/cardapio/999")
            assert resposta.status_code == 404

    def test_pagina_contem_tags_nos_itens(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}").text
            assert "vegano" in html

    def test_pagina_categorias_ordenadas_por_ordem(self):
        for c, cardapio_id in self._cliente_com_dados():
            html = c.get(f"/cardapio/{cardapio_id}").text
            pos_entradas = html.index("Entradas")
            pos_bebidas = html.index("Bebidas")
            assert pos_entradas < pos_bebidas
