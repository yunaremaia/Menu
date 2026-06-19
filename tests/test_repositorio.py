import pytest
from menu.modelos import Cardapio, Categoria, Item, Mesa
from menu.repositorio.banco import Banco


@pytest.fixture
def banco():
    b = Banco(":memory:")
    b.iniciar()
    yield b
    b.fechar()


@pytest.fixture
def cardapio(banco):
    return banco.criar_cardapio(Cardapio(nome="Cardápio Teste"))


@pytest.fixture
def categoria(banco, cardapio):
    return banco.criar_categoria(
        Categoria(nome="Entradas", cardapio_id=cardapio.id, ordem=0)
    )


class TestCardapioRepositorio:
    def test_criar_cardapio(self, banco):
        cardapio = Cardapio(nome="Cardápio do Dia")
        criado = banco.criar_cardapio(cardapio)
        assert criado.id == 1
        assert criado.nome == "Cardápio do Dia"
        assert criado.ativo is True

    def test_criar_cardapio_atribui_id(self, banco):
        c1 = banco.criar_cardapio(Cardapio(nome="Cardápio 1"))
        c2 = banco.criar_cardapio(Cardapio(nome="Cardápio 2"))
        assert c1.id == 1
        assert c2.id == 2

    def test_listar_cardapios_vazio(self, banco):
        cardapios = banco.listar_cardapios()
        assert cardapios == []

    def test_listar_cardapios(self, banco):
        banco.criar_cardapio(Cardapio(nome="Cardápio A"))
        banco.criar_cardapio(Cardapio(nome="Cardápio B"))
        cardapios = banco.listar_cardapios()
        assert len(cardapios) == 2
        assert cardapios[0].nome == "Cardápio A"
        assert cardapios[1].nome == "Cardápio B"

    def test_obter_cardapio_por_id(self, banco):
        criado = banco.criar_cardapio(Cardapio(nome="Jantar Especial"))
        obtido = banco.obter_cardapio(criado.id)
        assert obtido is not None
        assert obtido.nome == "Jantar Especial"
        assert obtido.id == criado.id

    def test_obter_cardapio_inexistente(self, banco):
        obtido = banco.obter_cardapio(999)
        assert obtido is None

    def test_atualizar_cardapio(self, banco):
        criado = banco.criar_cardapio(Cardapio(nome="Original"))
        atualizado = banco.atualizar_cardapio(criado.id, {"nome": "Modificado"})
        assert atualizado is not None
        assert atualizado.nome == "Modificado"

    def test_atualizar_cardapio_inexistente(self, banco):
        atualizado = banco.atualizar_cardapio(999, {"nome": "Nope"})
        assert atualizado is None

    def test_deletar_cardapio(self, banco):
        criado = banco.criar_cardapio(Cardapio(nome="Temporário"))
        deletado = banco.deletar_cardapio(criado.id)
        assert deletado is True
        obtido = banco.obter_cardapio(criado.id)
        assert obtido is None

    def test_deletar_cardapio_inexistente(self, banco):
        deletado = banco.deletar_cardapio(999)
        assert deletado is False

    def test_criar_cardapio_com_campos_completos(self, banco):
        cardapio = Cardapio(
            nome="Brunch", descricao="Café da manhã até tarde", ativo=False
        )
        criado = banco.criar_cardapio(cardapio)
        assert criado.nome == "Brunch"
        assert criado.descricao == "Café da manhã até tarde"
        assert criado.ativo is False
        assert criado.idioma_padrao == "pt-BR"

    def test_listar_apenas_cardapios_ativos(self, banco):
        banco.criar_cardapio(Cardapio(nome="Ativo 1"))
        banco.criar_cardapio(Cardapio(nome="Inativo", ativo=False))
        banco.criar_cardapio(Cardapio(nome="Ativo 2"))
        ativos = banco.listar_cardapios(apenas_ativos=True)
        assert len(ativos) == 2
        assert all(t.nome in ("Ativo 1", "Ativo 2") for t in ativos)

    def test_atualizar_cardapio_retorna_dados_completos(self, banco):
        criado = banco.criar_cardapio(Cardapio(nome="Original"))
        atualizado = banco.atualizar_cardapio(
            criado.id, {"nome": "Novo", "descricao": "Descrição nova"}
        )
        assert atualizado.nome == "Novo"
        assert atualizado.descricao == "Descrição nova"
        assert atualizado.ativo is True


class TestCategoriaRepositorio:
    def test_criar_categoria(self, banco, cardapio):
        categoria = Categoria(nome="Bebidas", cardapio_id=cardapio.id)
        criada = banco.criar_categoria(categoria)
        assert criada.id == 1
        assert criada.nome == "Bebidas"
        assert criada.cardapio_id == cardapio.id

    def test_listar_categorias_por_cardapio(self, banco, cardapio):
        banco.criar_categoria(Categoria(nome="Entradas", cardapio_id=cardapio.id))
        banco.criar_categoria(Categoria(nome="Principais", cardapio_id=cardapio.id))
        categorias = banco.listar_categorias(cardapio.id)
        assert len(categorias) == 2
        assert categorias[0].nome == "Entradas"

    def test_listar_categorias_ordem_padrao(self, banco, cardapio):
        banco.criar_categoria(Categoria(nome="Z", cardapio_id=cardapio.id, ordem=5))
        banco.criar_categoria(Categoria(nome="A", cardapio_id=cardapio.id, ordem=1))
        categorias = banco.listar_categorias(cardapio.id)
        assert categorias[0].nome == "A"
        assert categorias[1].nome == "Z"

    def test_listar_categorias_outro_cardapio_vazio(self, banco, cardapio):
        outro_cardapio = banco.criar_cardapio(Cardapio(nome="Outro"))
        categorias = banco.listar_categorias(outro_cardapio.id)
        assert categorias == []

    def test_obter_categoria(self, banco, cardapio, categoria):
        obtida = banco.obter_categoria(categoria.id)
        assert obtida is not None
        assert obtida.nome == "Entradas"

    def test_obter_categoria_inexistente(self, banco):
        assert banco.obter_categoria(999) is None

    def test_atualizar_categoria(self, banco, categoria):
        atualizada = banco.atualizar_categoria(categoria.id, {"nome": "Sobremesas"})
        assert atualizada is not None
        assert atualizada.nome == "Sobremesas"

    def test_atualizar_categoria_inexistente(self, banco):
        assert banco.atualizar_categoria(999, {"nome": "X"}) is None

    def test_deletar_categoria(self, banco, categoria):
        assert banco.deletar_categoria(categoria.id) is True
        assert banco.obter_categoria(categoria.id) is None

    def test_deletar_categoria_inexistente(self, banco):
        assert banco.deletar_categoria(999) is False


class TestItemRepositorio:
    def test_criar_item(self, banco, categoria):
        item = Item(nome="Hambúrguer", preco=29.90, categoria_id=categoria.id)
        criado = banco.criar_item(item)
        assert criado.id == 1
        assert criado.nome == "Hambúrguer"
        assert criado.preco == 29.90

    def test_listar_itens_por_categoria(self, banco, categoria):
        banco.criar_item(Item(nome="Item A", preco=10, categoria_id=categoria.id))
        banco.criar_item(Item(nome="Item B", preco=20, categoria_id=categoria.id))
        itens = banco.listar_itens(categoria.id)
        assert len(itens) == 2

    def test_listar_itens_ordenados_por_ordem(self, banco, categoria):
        banco.criar_item(
            Item(nome="Segundo", preco=10, categoria_id=categoria.id, ordem=2)
        )
        banco.criar_item(
            Item(nome="Primeiro", preco=10, categoria_id=categoria.id, ordem=1)
        )
        itens = banco.listar_itens(categoria.id)
        assert itens[0].nome == "Primeiro"
        assert itens[1].nome == "Segundo"

    def test_obter_item(self, banco, categoria):
        criado = banco.criar_item(
            Item(nome="Pizza", preco=49.90, categoria_id=categoria.id)
        )
        obtido = banco.obter_item(criado.id)
        assert obtido is not None
        assert obtido.nome == "Pizza"

    def test_obter_item_inexistente(self, banco):
        assert banco.obter_item(999) is None

    def test_atualizar_item(self, banco, categoria):
        criado = banco.criar_item(
            Item(nome="Original", preco=10, categoria_id=categoria.id)
        )
        atualizado = banco.atualizar_item(criado.id, {"preco": 15.50})
        assert atualizado is not None
        assert atualizado.preco == 15.50

    def test_atualizar_item_inexistente(self, banco):
        assert banco.atualizar_item(999, {"nome": "X"}) is None

    def test_deletar_item(self, banco, categoria):
        criado = banco.criar_item(
            Item(nome="Temp", preco=5, categoria_id=categoria.id)
        )
        assert banco.deletar_item(criado.id) is True
        assert banco.obter_item(criado.id) is None

    def test_deletar_item_inexistente(self, banco):
        assert banco.deletar_item(999) is False

    def test_listar_apenas_itens_disponiveis(self, banco, categoria):
        banco.criar_item(
            Item(nome="Disponível", preco=10, categoria_id=categoria.id)
        )
        banco.criar_item(
            Item(
                nome="Indisponível",
                preco=10,
                categoria_id=categoria.id,
                disponivel=False,
            )
        )
        disponiveis = banco.listar_itens(categoria.id, apenas_disponiveis=True)
        assert len(disponiveis) == 1
        assert disponiveis[0].nome == "Disponível"


class TestMesaRepositorio:
    def test_criar_mesa(self, banco, cardapio):
        mesa = Mesa(identificacao="Mesa 1", cardapio_id=cardapio.id)
        criada = banco.criar_mesa(mesa)
        assert criada.id == 1
        assert criada.identificacao == "Mesa 1"

    def test_listar_mesas_por_cardapio(self, banco, cardapio):
        banco.criar_mesa(Mesa(identificacao="Mesa 1", cardapio_id=cardapio.id))
        banco.criar_mesa(Mesa(identificacao="Mesa 2", cardapio_id=cardapio.id))
        mesas = banco.listar_mesas(cardapio.id)
        assert len(mesas) == 2

    def test_obter_mesa(self, banco, cardapio):
        criada = banco.criar_mesa(
            Mesa(identificacao="Balcão", cardapio_id=cardapio.id)
        )
        obtida = banco.obter_mesa(criada.id)
        assert obtida is not None
        assert obtida.identificacao == "Balcão"

    def test_obter_mesa_inexistente(self, banco):
        assert banco.obter_mesa(999) is None

    def test_atualizar_mesa(self, banco, cardapio):
        criada = banco.criar_mesa(
            Mesa(identificacao="Mesa 1", cardapio_id=cardapio.id)
        )
        atualizada = banco.atualizar_mesa(criada.id, {"identificacao": "Mesa 1A"})
        assert atualizada is not None
        assert atualizada.identificacao == "Mesa 1A"

    def test_atualizar_mesa_inexistente(self, banco):
        assert banco.atualizar_mesa(999, {"identificacao": "X"}) is None

    def test_deletar_mesa(self, banco, cardapio):
        criada = banco.criar_mesa(
            Mesa(identificacao="Temp", cardapio_id=cardapio.id)
        )
        assert banco.deletar_mesa(criada.id) is True
        assert banco.obter_mesa(criada.id) is None

    def test_deletar_mesa_inexistente(self, banco):
        assert banco.deletar_mesa(999) is False

    def test_listar_apenas_mesas_ativas(self, banco, cardapio):
        banco.criar_mesa(Mesa(identificacao="Mesa Ativa", cardapio_id=cardapio.id))
        banco.criar_mesa(
            Mesa(identificacao="Mesa Inativa", cardapio_id=cardapio.id, ativo=False)
        )
        ativas = banco.listar_mesas(cardapio.id, apenas_ativas=True)
        assert len(ativas) == 1


class TestBuscaRepositorio:
    def test_buscar_itens_por_nome(self, banco, cardapio, categoria):
        cat = banco.criar_categoria(
            Categoria(nome="Bebidas", cardapio_id=cardapio.id, ordem=1)
        )
        banco.criar_item(
            Item(nome="Suco de Laranja", preco=8.0, categoria_id=categoria.id)
        )
        banco.criar_item(
            Item(nome="Café Expresso", preco=5.0, categoria_id=cat.id)
        )
        resultados = banco.buscar_itens(cardapio.id, "laranja")
        assert len(resultados) == 1
        assert resultados[0]["item"].nome == "Suco de Laranja"

    def test_buscar_itens_por_descricao(self, banco, cardapio, categoria):
        banco.criar_item(
            Item(
                nome="Bruschetta",
                descricao="Pão italiano com tomate e manjericão",
                preco=19.90,
                categoria_id=categoria.id,
            )
        )
        resultados = banco.buscar_itens(cardapio.id, "manjericão")
        assert len(resultados) == 1

    def test_buscar_itens_por_tag(self, banco, cardapio, categoria):
        banco.criar_item(
            Item(
                nome="Hambúrguer",
                preco=29.90,
                tags="vegano, sem gluten",
                categoria_id=categoria.id,
            )
        )
        resultados = banco.buscar_itens(cardapio.id, "vegano")
        assert len(resultados) == 1

    def test_buscar_itens_sem_resultado(self, banco, cardapio, categoria):
        banco.criar_item(
            Item(nome="Pizza", preco=35.0, categoria_id=categoria.id)
        )
        resultados = banco.buscar_itens(cardapio.id, "sushi")
        assert resultados == []

    def test_buscar_itens_case_insensitive(self, banco, cardapio, categoria):
        banco.criar_item(
            Item(nome="Suco de Laranja", preco=8.0, categoria_id=categoria.id)
        )
        resultados = banco.buscar_itens(cardapio.id, "LARANJA")
        assert len(resultados) == 1

    def test_buscar_itens_inclui_categoria(self, banco, cardapio, categoria):
        banco.criar_item(
            Item(nome="Bruschetta", preco=19.90, categoria_id=categoria.id)
        )
        resultados = banco.buscar_itens(cardapio.id, "bruschetta")
        assert resultados[0]["categoria"] == "Entradas"

    def test_buscar_itens_apenas_disponiveis(self, banco, cardapio, categoria):
        banco.criar_item(
            Item(nome="Item OK", preco=10.0, categoria_id=categoria.id)
        )
        banco.criar_item(
            Item(
                nome="Item Esgotado",
                preco=10.0,
                categoria_id=categoria.id,
                disponivel=False,
            )
        )
        resultados = banco.buscar_itens(cardapio.id, "Item")
        assert len(resultados) == 1
        assert resultados[0]["item"].nome == "Item OK"
