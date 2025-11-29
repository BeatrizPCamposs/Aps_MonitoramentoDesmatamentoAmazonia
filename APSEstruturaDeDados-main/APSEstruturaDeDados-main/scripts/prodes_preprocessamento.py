import os
import time
from collections import deque
import pandas as pd

# -----------------------------------------------------------------------------------------------
# Processamento dos dados do PRODES
# -----------------------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dados_path = os.path.join(BASE_DIR, "..", "dados")
resultados_dir = os.path.join(BASE_DIR, "..", "resultados")
os.makedirs(resultados_dir, exist_ok=True)

prodes_file = os.path.join(dados_path, "PRODES_BASE_DE_DESMATAMENTO_POR_ANOS.csv")

if not os.path.exists(prodes_file):
    raise FileNotFoundError(f"Arquivo não encontrado: {prodes_file}")

# -----------------------------------------------------------------------------------------------
# Leitura e tratamento dos dados
# -----------------------------------------------------------------------------------------------
prodes = pd.read_csv(prodes_file, sep=";", encoding="latin1")

# Remove linhas com valores ausentes importantes
prodes = prodes.dropna(subset=["year", "state", "areakm"])

# Corrige codificação de texto para UTF-8
for coluna in ["municipality", "state"]:
    if coluna in prodes.columns:
        prodes[coluna] = prodes[coluna].apply(
            lambda x: x.encode("latin1").decode("utf-8") if isinstance(x, str) else x
        )

# Converte e arredonda valores numéricos
prodes["areakm"] = (
    prodes["areakm"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
    .round(2)
)

# -----------------------------------------------------------------------------------------------
# Conversão final para texto (para Power BI)
# -----------------------------------------------------------------------------------------------
prodes = prodes.astype(str)

# -----------------------------------------------------------------------------------------------
# Gera arquivo completo tratado (único arquivo de dados)
# -----------------------------------------------------------------------------------------------
prodes_tratado = os.path.join(resultados_dir, "prodes_tratado_completo.csv")
prodes.to_csv(prodes_tratado, sep=";", index=False, encoding="utf-8-sig")
print(f"✅ Arquivo tratado gerado: {prodes_tratado} ({len(prodes)} linhas)")

# -----------------------------------------------------------------------------------------------
# Estruturas de Dados - Pilha e Fila
# -----------------------------------------------------------------------------------------------
class Pilha:
    def __init__(self): self.itens = []
    def push(self, item): self.itens.append(item)
    def pop(self): return self.itens.pop() if self.itens else None
    def tamanho(self): return len(self.itens)
    def listar(self): return list(self.itens)

class Fila:
    def __init__(self): self.itens = deque()
    def enqueue(self, item): self.itens.append(item)
    def dequeue(self): return self.itens.popleft() if self.itens else None
    def tamanho(self): return len(self.itens)
    def listar(self): return list(self.itens)

# -----------------------------------------------------------------------------------------------
# Carrega os dados completos nas estruturas
# -----------------------------------------------------------------------------------------------
pilha = Pilha()
fila = Fila()

for _, row in prodes.iterrows():
    registro = {
        "year": row["year"],
        "state": row["state"],
        "municipality": row["municipality"] if "municipality" in row else "",
        "areakm": row["areakm"]
    }
    pilha.push(registro)
    fila.enqueue(registro)

# -----------------------------------------------------------------------------------------------
# Algoritmos de Ordenação
# -----------------------------------------------------------------------------------------------
def bubble_sort(lista):
    lista = lista.copy()
    n = len(lista)
    comparacoes = 0
    inicio = time.time()
    for i in range(n):
        for j in range(0, n - i - 1):
            comparacoes += 1
            try:
                if float(lista[j]["areakm"]) > float(lista[j + 1]["areakm"]):
                    lista[j], lista[j + 1] = lista[j + 1], lista[j]
            except ValueError:
                continue
    return lista, comparacoes, round(time.time() - inicio, 4)

def quick_sort(lista):
    comparacoes = [0]
    def _quick_sort(items):
        if len(items) <= 1:
            return items
        try:
            pivo = float(items[len(items)//2]["areakm"])
        except ValueError:
            return items
        menores = [x for x in items if float(x["areakm"]) < pivo]
        iguais = [x for x in items if float(x["areakm"]) == pivo]
        maiores = [x for x in items if float(x["areakm"]) > pivo]
        comparacoes[0] += len(items) - 1
        return _quick_sort(menores) + iguais + _quick_sort(maiores)
    inicio = time.time()
    ordenado = _quick_sort(lista.copy())
    return ordenado, comparacoes[0], round(time.time() - inicio, 4)

# -----------------------------------------------------------------------------------------------
# Execução dos algoritmos e geração do CSV de desempenho
# -----------------------------------------------------------------------------------------------
dados_para_ordenar = pilha.listar()
bubble_dados, bubble_comp, bubble_tempo = bubble_sort(dados_para_ordenar)
quick_dados, quick_comp, quick_tempo = quick_sort(dados_para_ordenar)

resultados = pd.DataFrame([
    {"Algoritmo": "Bubble Sort", "Comparações": bubble_comp, "Tempo (s)": bubble_tempo},
    {"Algoritmo": "Quick Sort", "Comparações": quick_comp, "Tempo (s)": quick_tempo}
])

saida_performance = os.path.join(resultados_dir, "desempenho_algoritmos_prodes.csv")
resultados.to_csv(saida_performance, sep=";", index=False, encoding="utf-8-sig")

# -----------------------------------------------------------------------------------------------
# Exibição no console
# -----------------------------------------------------------------------------------------------
print("\nEstruturas de Dados:")
print(f"Pilha: {pilha.tamanho()} registros")
print(f"Fila:  {fila.tamanho()} registros")

if pilha.tamanho() > 0:
    print("\nExemplo do topo da Pilha (último inserido):")
    print(pilha.listar()[-1])

if fila.tamanho() > 0:
    print("\nExemplo da frente da Fila (primeiro inserido):")
    print(fila.listar()[0])

print("--------------------------------------------------------")
print("Comparativo de desempenho dos algoritmos:\n")
print(resultados.to_string(index=False))
