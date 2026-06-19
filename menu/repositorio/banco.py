import sqlite3
from datetime import datetime, timezone

from menu.modelos import Cardapio


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
