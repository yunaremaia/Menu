import uuid
from pathlib import Path

EXTENSOES_PERMITIDAS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


class ArmazenamentoLocal:
    def __init__(self, diretorio: str, url_base: str = "/arquivos"):
        self._diretorio = Path(diretorio)
        self._diretorio.mkdir(parents=True, exist_ok=True)
        self._url_base = url_base.rstrip("/")

    def salvar(self, dados: bytes, extensao: str) -> str:
        extensao = extensao.lower()
        if extensao not in EXTENSOES_PERMITIDAS:
            raise ValueError(f"Extensão não permitida: {extensao}")
        nome = f"{uuid.uuid4().hex}{extensao}"
        caminho = self._diretorio / nome
        caminho.write_bytes(dados)
        return f"{self._url_base}/{nome}"

    def obter_caminho(self, url: str) -> Path | None:
        nome = url.split("/")[-1]
        caminho = self._diretorio / nome
        return caminho if caminho.exists() else None

    def remover(self, url: str) -> None:
        nome = url.split("/")[-1]
        caminho = self._diretorio / nome
        if caminho.exists():
            caminho.unlink()
