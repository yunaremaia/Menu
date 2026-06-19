from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from menu.modelos import Cardapio, Categoria, Item, Mesa


class TestCardapio:
    def test_criar_cardapio_minimo(self):
        cardapio = Cardapio(nome="Cardápio do Dia")
        assert cardapio.nome == "Cardápio do Dia"
        assert cardapio.descricao is None
        assert cardapio.ativo is True
        assert cardapio.idioma_padrao == "pt-BR"
        assert isinstance(cardapio.criado_em, datetime)

    def test_criar_cardapio_completo(self):
        cardapio = Cardapio(
            nome="Happy Hour",
            descricao="Promoções especiais após as 18h",
            ativo=True,
            idioma_padrao="en",
        )
        assert cardapio.nome == "Happy Hour"
        assert cardapio.descricao == "Promoções especiais após as 18h"
        assert cardapio.ativo is True
        assert cardapio.idioma_padrao == "en"

    def test_cardapio_inativo(self):
        cardapio = Cardapio(nome="Brunch", ativo=False)
        assert cardapio.ativo is False

    def test_cardapio_nome_vazio_rejeitado(self):
        with pytest.raises(ValidationError):
            Cardapio(nome="")

    def test_cardapio_nome_so_espacos_rejeitado(self):
        with pytest.raises(ValidationError):
            Cardapio(nome="   ")

    def test_cardapio_criado_em_e_timezone_aware(self):
        cardapio = Cardapio(nome="Teste")
        assert cardapio.criado_em.tzinfo is not None

    def test_cardapio_atualizado_em_e_timezone_aware(self):
        cardapio = Cardapio(nome="Teste")
        assert cardapio.atualizado_em.tzinfo is not None

    def test_cardapio_representacao_string(self):
        cardapio = Cardapio(nome="Jantar")
        assert repr(cardapio) == "<Cardapio Jantar>"


class TestCategoria:
    def test_criar_categoria_minimo(self):
        categoria = Categoria(nome="Entradas", cardapio_id=1)
        assert categoria.nome == "Entradas"
        assert categoria.cardapio_id == 1
        assert categoria.ordem == 0
        assert isinstance(categoria.criado_em, datetime)

    def test_criar_categoria_com_ordem(self):
        categoria = Categoria(nome="Bebidas", cardapio_id=1, ordem=2)
        assert categoria.ordem == 2

    def test_categoria_nome_vazio_rejeitado(self):
        with pytest.raises(ValidationError):
            Categoria(nome="", cardapio_id=1)

    def test_categoria_cardapio_id_invalido(self):
        with pytest.raises(ValidationError):
            Categoria(nome="Sobremesas", cardapio_id=-1)

    def test_categoria_ordem_negativa_rejeitada(self):
        with pytest.raises(ValidationError):
            Categoria(nome="Teste", cardapio_id=1, ordem=-1)


class TestItem:
    def test_criar_item_minimo(self):
        item = Item(nome="Hambúrguer Artesanal", preco=29.90, categoria_id=1)
        assert item.nome == "Hambúrguer Artesanal"
        assert item.preco == 29.90
        assert item.categoria_id == 1
        assert item.descricao is None
        assert item.disponivel is True
        assert item.destaque is False
        assert item.ordem == 0
        assert isinstance(item.criado_em, datetime)

    def test_criar_item_completo(self):
        item = Item(
            nome="Pizza Margherita",
            descricao="Molho de tomate, mussarela e manjericão",
            preco=49.90,
            foto_url="https://exemplo.com/pizza.jpg",
            tags="vegano,lactose",
            disponivel=True,
            destaque=True,
            ordem=1,
            categoria_id=2,
        )
        assert item.descricao == "Molho de tomate, mussarela e manjericão"
        assert item.foto_url == "https://exemplo.com/pizza.jpg"
        assert item.tags == "vegano,lactose"
        assert item.destaque is True
        assert item.ordem == 1

    def test_item_nome_vazio_rejeitado(self):
        with pytest.raises(ValidationError):
            Item(nome="", preco=10.0, categoria_id=1)

    def test_item_preco_negativo_rejeitado(self):
        with pytest.raises(ValidationError):
            Item(nome="Teste", preco=-5.0, categoria_id=1)

    def test_item_preco_zero(self):
        item = Item(nome="Brinde", preco=0.0, categoria_id=1)
        assert item.preco == 0.0

    def test_item_disponivel_false(self):
        item = Item(nome="Esgotado", preco=10.0, categoria_id=1, disponivel=False)
        assert item.disponivel is False

    def test_item_categoria_id_invalido(self):
        with pytest.raises(ValidationError):
            Item(nome="Teste", preco=10.0, categoria_id=-1)

    def test_item_com_tags_vazias(self):
        item = Item(nome="Teste", preco=10.0, categoria_id=1, tags="")
        assert item.tags == ""

    def test_item_atualizado_em_e_timezone_aware(self):
        item = Item(nome="Teste", preco=10.0, categoria_id=1)
        assert item.atualizado_em.tzinfo is not None


class TestMesa:
    def test_criar_mesa_minimo(self):
        mesa = Mesa(identificacao="Mesa 1", cardapio_id=1)
        assert mesa.identificacao == "Mesa 1"
        assert mesa.cardapio_id == 1
        assert mesa.ativo is True
        assert isinstance(mesa.criado_em, datetime)

    def test_criar_mesa_inativa(self):
        mesa = Mesa(identificacao="Balcão 3", cardapio_id=1, ativo=False)
        assert mesa.ativo is False

    def test_mesa_identificacao_vazia_rejeitado(self):
        with pytest.raises(ValidationError):
            Mesa(identificacao="", cardapio_id=1)

    def test_mesa_cardapio_id_invalido(self):
        with pytest.raises(ValidationError):
            Mesa(identificacao="Mesa 5", cardapio_id=-1)
