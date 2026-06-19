import io

import qrcode


def gerar_qrcode(dados: str) -> bytes:
    if not dados:
        raise ValueError("dados não pode estar vazio")
    img = qrcode.make(dados)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
