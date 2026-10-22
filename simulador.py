"""Simulador de Máquina de Turing determinística com uma fita."""

import argparse
from pathlib import Path


def carregar_maquina(caminho):
    linhas = []
    for numero, linha in enumerate(Path(caminho).read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.split(";", 1)[0].strip()
        if linha:
            linhas.append((numero, linha))
    if len(linhas) < 6:
        raise ValueError("O arquivo precisa das seis linhas de definição.")

    def lista(indice):
        itens = [item.strip() for item in linhas[indice][1].split(",")]
        if any(not item for item in itens) or len(itens) != len(set(itens)):
            raise ValueError(f"Lista inválida na linha {linhas[indice][0]}.")
        return set(itens)

    estados, entrada, alfabeto = lista(0), lista(1), lista(2)
    branco, inicial = linhas[3][1], linhas[4][1]
    finais = lista(5)
    if any(len(s) != 1 for s in entrada | alfabeto):
        raise ValueError("Cada símbolo deve ter um caractere.")
    if not entrada <= alfabeto or branco not in alfabeto or branco in entrada:
        raise ValueError("Alfabetos ou símbolo de branco inválidos.")
    if inicial not in estados or not finais <= estados:
        raise ValueError("Estado inicial ou final não declarado.")
    transicoes = {}
    for numero, linha in linhas[6:]:
        partes = [parte.strip() for parte in linha.split(",")]
        if len(partes) != 5:
            raise ValueError(f"Transição inválida na linha {numero}.")
        origem, le, escreve, direcao, destino = partes
        if origem not in estados or destino not in estados:
            raise ValueError(f"Estado não declarado na linha {numero}.")
        if le not in alfabeto or escreve not in alfabeto or direcao not in {"R", "L", "S"}:
            raise ValueError(f"Símbolo ou direção inválida na linha {numero}.")
        if (origem, le) in transicoes:
            raise ValueError(f"Transição duplicada na linha {numero}: a MT deve ser determinística.")
        transicoes[origem, le] = escreve, direcao, destino
    return entrada, branco, inicial, finais, transicoes


def mostrar_fita(fita, cabeca, estado, passo, branco):
    esquerda = min(min(fita, default=cabeca), cabeca) - 1
    direita = max(max(fita, default=cabeca), cabeca) + 1
    simbolos = " ".join(fita.get(i, branco) for i in range(esquerda, direita + 1))
    print(f"Passo {passo} | estado: {estado} | cabeçote: {cabeca}")
    print(simbolos)
    print(" " * (2 * (cabeca - esquerda)) + "^")


def simular(maquina, palavra, limite=100000, trace=True):
    entrada, branco, estado, finais, transicoes = maquina
    if limite <= 0:
        raise ValueError("O limite de passos deve ser positivo.")
    if any(simbolo not in entrada for simbolo in palavra):
        raise ValueError("A entrada contém símbolos fora do alfabeto de entrada.")
    fita = dict(enumerate(palavra))
    cabeca = passo = 0
    while True:
        if trace:
            mostrar_fita(fita, cabeca, estado, passo, branco)
        if estado in finais:
            status = "ACEITA/PARADA"
            break
        regra = transicoes.get((estado, fita.get(cabeca, branco)))
        if regra is None:
            status = "REJEITA"
            break
        if passo >= limite:
            status = "LIMITE DE PASSOS"
            break
        escreve, direcao, estado = regra
        if escreve == branco:
            fita.pop(cabeca, None)
        else:
            fita[cabeca] = escreve
        cabeca += {"R": 1, "L": -1, "S": 0}[direcao]
        passo += 1
    resultado = ""
    if fita:
        resultado = "".join(fita.get(i, branco) for i in range(min(fita), max(fita) + 1))
    return status, resultado, passo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help='Exemplo: "111*11". Zero é uma sequência vazia.')
    parser.add_argument("--arquivo", type=Path, default=Path(__file__).with_name("multiplicacao.txt"))
    parser.add_argument("--limite", type=int, default=100000)
    args = parser.parse_args()
    try:
        status, resultado, passos = simular(carregar_maquina(args.arquivo), args.entrada, args.limite)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(f"\nSituação: {status}\nFita final: {resultado or '(vazia)'}\nPassos: {passos}")
    if status == "LIMITE DE PASSOS":
        print("Execução abortada: o limite foi atingido; isso não prova que exista um loop infinito.")
    return 0 if status == "ACEITA/PARADA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
