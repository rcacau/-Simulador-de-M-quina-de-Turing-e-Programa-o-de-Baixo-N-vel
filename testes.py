"""Verificações do simulador e da máquina de multiplicação: python testes.py."""

from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from simulador import carregar_maquina, simular


class Testes(unittest.TestCase):
    def test_multiplicacoes(self):
        maquina = carregar_maquina(Path(__file__).with_name("multiplicacao.txt"))
        for a in range(9):
            for b in range(9):
                with self.subTest(a=a, b=b):
                    status, fita, _ = simular(maquina, "1" * a + "*" + "1" * b, trace=False)
                    self.assertEqual(status, "ACEITA/PARADA")
                    self.assertEqual(fita, "1" * (a * b))

    def test_formato_invalido(self):
        maquina = carregar_maquina(Path(__file__).with_name("multiplicacao.txt"))
        for tamanho in range(8):
            for simbolos in product("1*", repeat=tamanho):
                palavra = "".join(simbolos)
                if palavra.count("*") != 1:
                    with self.subTest(palavra=palavra):
                        self.assertEqual(simular(maquina, palavra, trace=False)[0], "REJEITA")
        with self.assertRaises(ValueError):
            simular(maquina, "11*2", trace=False)

    def test_limite(self):
        maquina = carregar_maquina(Path(__file__).with_name("multiplicacao.txt"))
        self.assertEqual(simular(maquina, "111*11", limite=1, trace=False)[0], "LIMITE DE PASSOS")

    def test_fita_nos_dois_sentidos_e_movimento_s(self):
        # Uma segunda MT testa o motor independentemente da multiplicação.
        texto = "q0,q1,q2,q3,qf\na\na,X,B\nB\nq0\nqf\n" + "\n".join([
            "q0,B,B,L,q1", "q1,B,X,R,q2", "q2,B,B,R,q3", "q3,B,X,S,qf"])
        with TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "maquina.txt"
            arquivo.write_text(texto, encoding="utf-8")
            maquina = carregar_maquina(arquivo)
            self.assertEqual(simular(maquina, "", limite=4, trace=False), ("ACEITA/PARADA", "XBX", 4))
            arquivo.write_text(texto + "\nq0,B,B,R,qf", encoding="utf-8")
            with self.assertRaises(ValueError):
                carregar_maquina(arquivo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
