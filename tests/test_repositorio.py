import pytest
from menu.modelos import Cardapio
from menu.repositorio.banco import Banco


@pytest.fixture
def banco():
    b = Banco(":memory:")
    b.iniciar()
    yield b
    b.fechar()


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
