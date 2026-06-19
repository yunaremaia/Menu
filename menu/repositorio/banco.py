import sqlite3
from datetime import datetime, timezone

from menu.modelos import Cardapio, Categoria, Item, Mesa


class Banco:
    def __init__(self, caminho: str = "menu.db"):
        self._caminho = caminho
        self._conexao: sqlite3.Connection | None = None

    def iniciar(self):
        self._conexao = sqlite3.connect(self._caminho, check_same_thread=False)
        self._conexao.row_factory = sqlite3.Row
        self._conexao.execute("PRAGMA journal_mode=WAL")
        self._conexao.execute("PRAGMA foreign_keys=ON")
        self._criar_tabelas()

    def fechar(self):
        if self._conexao:
            self._conexao.close()
            self._conexao = None

    def _criar_tabelas(self):
        self._conexao.executescript("""
            CREATE TABLE IF NOT EXISTS cardapios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                idioma_padrao TEXT NOT NULL DEFAULT 'pt-BR',
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cardapio_id INTEGER NOT NULL REFERENCES cardapios(id) ON DELETE CASCADE,
                nome TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                criado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                foto_url TEXT,
                tags TEXT NOT NULL DEFAULT '',
                disponivel INTEGER NOT NULL DEFAULT 1,
                destaque INTEGER NOT NULL DEFAULT 0,
                ordem INTEGER NOT NULL DEFAULT 0,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cardapio_id INTEGER NOT NULL REFERENCES cardapios(id) ON DELETE CASCADE,
                identificacao TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em TEXT NOT NULL
            );
        """)

    def _linha_para_cardapio(self, linha: sqlite3.Row) -> Cardapio:
        return Cardapio(
            id=linha["id"],
            nome=linha["nome"],
            descricao=linha["descricao"],
            ativo=bool(linha["ativo"]),
            idioma_padrao=linha["idioma_padrao"],
            criado_em=linha["criado_em"],
            atualizado_em=linha["atualizado_em"],
        )

    def criar_cardapio(self, cardapio: Cardapio) -> Cardapio:
        cursor = self._conexao.execute(
            """INSERT INTO cardapios (nome, descricao, ativo, idioma_padrao, criado_em, atualizado_em)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                cardapio.nome,
                cardapio.descricao,
                int(cardapio.ativo),
                cardapio.idioma_padrao,
                cardapio.criado_em.isoformat(),
                cardapio.atualizado_em.isoformat(),
            ),
        )
        self._conexao.commit()
        return self._linha_para_cardapio(
            self._conexao.execute(
                "SELECT * FROM cardapios WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        )

    def listar_cardapios(self, apenas_ativos: bool = False) -> list[Cardapio]:
        query = "SELECT * FROM cardapios"
        params: tuple = ()
        if apenas_ativos:
            query += " WHERE ativo = 1"
        query += " ORDER BY id"
        linhas = self._conexao.execute(query, params).fetchall()
        return [self._linha_para_cardapio(l) for l in linhas]

    def obter_cardapio(self, id: int) -> Cardapio | None:
        linha = self._conexao.execute(
            "SELECT * FROM cardapios WHERE id = ?", (id,)
        ).fetchone()
        return self._linha_para_cardapio(linha) if linha else None

    def atualizar_cardapio(self, id: int, dados: dict) -> Cardapio | None:
        existente = self._conexao.execute(
            "SELECT * FROM cardapios WHERE id = ?", (id,)
        ).fetchone()
        if not existente:
            return None
        campos = []
        valores = []
        if "nome" in dados:
            campos.append("nome = ?")
            valores.append(dados["nome"])
        if "descricao" in dados:
            campos.append("descricao = ?")
            valores.append(dados["descricao"])
        if "ativo" in dados:
            campos.append("ativo = ?")
            valores.append(int(dados["ativo"]))
        if "idioma_padrao" in dados:
            campos.append("idioma_padrao = ?")
            valores.append(dados["idioma_padrao"])
        campos.append("atualizado_em = ?")
        valores.append(datetime.now(timezone.utc).isoformat())
        valores.append(id)
        self._conexao.execute(
            f"UPDATE cardapios SET {', '.join(campos)} WHERE id = ?", valores
        )
        self._conexao.commit()
        return self._linha_para_cardapio(
            self._conexao.execute(
                "SELECT * FROM cardapios WHERE id = ?", (id,)
            ).fetchone()
        )

    def deletar_cardapio(self, id: int) -> bool:
        cursor = self._conexao.execute("DELETE FROM cardapios WHERE id = ?", (id,))
        self._conexao.commit()
        return cursor.rowcount > 0

    def _linha_para_categoria(self, linha: sqlite3.Row) -> Categoria:
        return Categoria(
            id=linha["id"],
            nome=linha["nome"],
            cardapio_id=linha["cardapio_id"],
            ordem=linha["ordem"],
            criado_em=linha["criado_em"],
        )

    def criar_categoria(self, categoria: Categoria) -> Categoria:
        cursor = self._conexao.execute(
            """INSERT INTO categorias (nome, cardapio_id, ordem, criado_em)
               VALUES (?, ?, ?, ?)""",
            (
                categoria.nome,
                categoria.cardapio_id,
                categoria.ordem,
                categoria.criado_em.isoformat(),
            ),
        )
        self._conexao.commit()
        return self._linha_para_categoria(
            self._conexao.execute(
                "SELECT * FROM categorias WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        )

    def listar_categorias(self, cardapio_id: int) -> list[Categoria]:
        linhas = self._conexao.execute(
            "SELECT * FROM categorias WHERE cardapio_id = ? ORDER BY ordem, id",
            (cardapio_id,),
        ).fetchall()
        return [self._linha_para_categoria(l) for l in linhas]

    def obter_categoria(self, id: int) -> Categoria | None:
        linha = self._conexao.execute(
            "SELECT * FROM categorias WHERE id = ?", (id,)
        ).fetchone()
        return self._linha_para_categoria(linha) if linha else None

    def atualizar_categoria(self, id: int, dados: dict) -> Categoria | None:
        existente = self._conexao.execute(
            "SELECT * FROM categorias WHERE id = ?", (id,)
        ).fetchone()
        if not existente:
            return None
        campos = []
        valores = []
        if "nome" in dados:
            campos.append("nome = ?")
            valores.append(dados["nome"])
        if "ordem" in dados:
            campos.append("ordem = ?")
            valores.append(dados["ordem"])
        valores.append(id)
        self._conexao.execute(
            f"UPDATE categorias SET {', '.join(campos)} WHERE id = ?", valores
        )
        self._conexao.commit()
        return self._linha_para_categoria(
            self._conexao.execute(
                "SELECT * FROM categorias WHERE id = ?", (id,)
            ).fetchone()
        )

    def deletar_categoria(self, id: int) -> bool:
        cursor = self._conexao.execute("DELETE FROM categorias WHERE id = ?", (id,))
        self._conexao.commit()
        return cursor.rowcount > 0

    def _linha_para_item(self, linha: sqlite3.Row) -> Item:
        return Item(
            id=linha["id"],
            nome=linha["nome"],
            descricao=linha["descricao"],
            preco=linha["preco"],
            foto_url=linha["foto_url"],
            tags=linha["tags"],
            disponivel=bool(linha["disponivel"]),
            destaque=bool(linha["destaque"]),
            ordem=linha["ordem"],
            categoria_id=linha["categoria_id"],
            criado_em=linha["criado_em"],
            atualizado_em=linha["atualizado_em"],
        )

    def criar_item(self, item: Item) -> Item:
        cursor = self._conexao.execute(
            """INSERT INTO itens (nome, descricao, preco, foto_url, tags, disponivel, destaque, ordem, categoria_id, criado_em, atualizado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                item.nome,
                item.descricao,
                item.preco,
                item.foto_url,
                item.tags,
                int(item.disponivel),
                int(item.destaque),
                item.ordem,
                item.categoria_id,
                item.criado_em.isoformat(),
                item.atualizado_em.isoformat(),
            ),
        )
        self._conexao.commit()
        return self._linha_para_item(
            self._conexao.execute(
                "SELECT * FROM itens WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        )

    def listar_itens(
        self, categoria_id: int, apenas_disponiveis: bool = False
    ) -> list[Item]:
        query = "SELECT * FROM itens WHERE categoria_id = ?"
        params: list = [categoria_id]
        if apenas_disponiveis:
            query += " AND disponivel = 1"
        query += " ORDER BY ordem, id"
        linhas = self._conexao.execute(query, params).fetchall()
        return [self._linha_para_item(l) for l in linhas]

    def obter_item(self, id: int) -> Item | None:
        linha = self._conexao.execute(
            "SELECT * FROM itens WHERE id = ?", (id,)
        ).fetchone()
        return self._linha_para_item(linha) if linha else None

    def atualizar_item(self, id: int, dados: dict) -> Item | None:
        existente = self._conexao.execute(
            "SELECT * FROM itens WHERE id = ?", (id,)
        ).fetchone()
        if not existente:
            return None
        campos = []
        valores = []
        for campo_str, intfy in [
            ("nome", False),
            ("descricao", False),
            ("preco", False),
            ("foto_url", False),
            ("tags", False),
            ("disponivel", True),
            ("destaque", True),
            ("ordem", False),
        ]:
            if campo_str in dados:
                campos.append(f"{campo_str} = ?")
                valores.append(int(dados[campo_str]) if intfy else dados[campo_str])
        campos.append("atualizado_em = ?")
        valores.append(datetime.now(timezone.utc).isoformat())
        valores.append(id)
        self._conexao.execute(
            f"UPDATE itens SET {', '.join(campos)} WHERE id = ?", valores
        )
        self._conexao.commit()
        return self._linha_para_item(
            self._conexao.execute(
                "SELECT * FROM itens WHERE id = ?", (id,)
            ).fetchone()
        )

    def deletar_item(self, id: int) -> bool:
        cursor = self._conexao.execute("DELETE FROM itens WHERE id = ?", (id,))
        self._conexao.commit()
        return cursor.rowcount > 0

    def _linha_para_mesa(self, linha: sqlite3.Row) -> Mesa:
        return Mesa(
            id=linha["id"],
            identificacao=linha["identificacao"],
            cardapio_id=linha["cardapio_id"],
            ativo=bool(linha["ativo"]),
            criado_em=linha["criado_em"],
        )

    def criar_mesa(self, mesa: Mesa) -> Mesa:
        cursor = self._conexao.execute(
            """INSERT INTO mesas (identificacao, cardapio_id, ativo, criado_em)
               VALUES (?, ?, ?, ?)""",
            (
                mesa.identificacao,
                mesa.cardapio_id,
                int(mesa.ativo),
                mesa.criado_em.isoformat(),
            ),
        )
        self._conexao.commit()
        return self._linha_para_mesa(
            self._conexao.execute(
                "SELECT * FROM mesas WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        )

    def listar_mesas(
        self, cardapio_id: int, apenas_ativas: bool = False
    ) -> list[Mesa]:
        query = "SELECT * FROM mesas WHERE cardapio_id = ?"
        params: list = [cardapio_id]
        if apenas_ativas:
            query += " AND ativo = 1"
        query += " ORDER BY id"
        linhas = self._conexao.execute(query, params).fetchall()
        return [self._linha_para_mesa(l) for l in linhas]

    def obter_mesa(self, id: int) -> Mesa | None:
        linha = self._conexao.execute(
            "SELECT * FROM mesas WHERE id = ?", (id,)
        ).fetchone()
        return self._linha_para_mesa(linha) if linha else None

    def atualizar_mesa(self, id: int, dados: dict) -> Mesa | None:
        existente = self._conexao.execute(
            "SELECT * FROM mesas WHERE id = ?", (id,)
        ).fetchone()
        if not existente:
            return None
        campos = []
        valores = []
        if "identificacao" in dados:
            campos.append("identificacao = ?")
            valores.append(dados["identificacao"])
        if "ativo" in dados:
            campos.append("ativo = ?")
            valores.append(int(dados["ativo"]))
        valores.append(id)
        self._conexao.execute(
            f"UPDATE mesas SET {', '.join(campos)} WHERE id = ?", valores
        )
        self._conexao.commit()
        return self._linha_para_mesa(
            self._conexao.execute(
                "SELECT * FROM mesas WHERE id = ?", (id,)
            ).fetchone()
        )

    def deletar_mesa(self, id: int) -> bool:
        cursor = self._conexao.execute("DELETE FROM mesas WHERE id = ?", (id,))
        self._conexao.commit()
        return cursor.rowcount > 0
