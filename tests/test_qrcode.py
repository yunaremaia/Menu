import struct

import pytest

from menu.qrcode.gerador import gerar_qrcode


class TestGerarQRCode:
    def test_gerar_qrcode_retorna_bytes(self):
        resultado = gerar_qrcode("https://exemplo.com")
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_gerar_qrcode_e_png_valido(self):
        resultado = gerar_qrcode("https://exemplo.com")
        assert resultado[:8] == b"\x89PNG\r\n\x1a\n"

    def test_gerar_qrcode_com_url_longa(self):
        url = "https://menu.exemplo.com/cardapio/42?mesa=7&lang=pt-BR"
        resultado = gerar_qrcode(url)
        assert resultado[:8] == b"\x89PNG\r\n\x1a\n"

    def test_gerar_qrcode_com_string_vazia(self):
        with pytest.raises(ValueError):
            gerar_qrcode("")

    def test_gerar_qrcode_com_dados_diferentes_produz_imagens_diferentes(self):
        qr1 = gerar_qrcode("https://exemplo.com/mesa/1")
        qr2 = gerar_qrcode("https://exemplo.com/mesa/2")
        assert qr1 != qr2

    def test_gerar_qrcode_com_unicode(self):
        resultado = gerar_qrcode("https://menu.exemplo.com/mesa/1/cardápio")
        assert resultado[:8] == b"\x89PNG\r\n\x1a\n"

    def test_gerar_qrcode_tamanho_razoavel(self):
        resultado = gerar_qrcode("https://exemplo.com")
        assert len(resultado) < 50_000
