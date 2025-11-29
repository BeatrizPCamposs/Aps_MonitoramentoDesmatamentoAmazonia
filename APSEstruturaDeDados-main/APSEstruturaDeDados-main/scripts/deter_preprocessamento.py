import os
import time
from collections import deque
import pandas as pd

# -----------------------------------------------------------------------------------------------
# Processamento dos dados do DETER
# -----------------------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dados_path = os.path.join(BASE_DIR, "..", "dados")
resultados_dir = os.path.join(BASE_DIR, "..", "resultados")
os.makedirs(resultados_dir, exist_ok=True)

deter_file = os.path.join(dados_path, "DETER_BASE_DE_ALARMES.csv")

if not os.path.exists(deter_file):
    raise FileNotFoundError(f"Arquivo não encontrado: {deter_file}")

# -----------------------------------------------------------------------------------------------
# Leitura e tratamento dos dados
# -----------------------------------------------------------------------------------------------
deter = pd.read_csv(deter_file, sep=";", encoding="utf-8-sig", header=0)
deter.columns = deter.columns.str.strip().str.lower()

# Remove linhas com valores ausentes importantes
deter = deter.dropna(subset=["year", "uf", "area"])

# Converte tipos e arredonda
deter["area"] = pd.to_numeric(deter["area"], errors="coerce").round(2)
deter["month"] = pd.to_numeric(deter["month"], errors="coerce")
deter["numpol"] = pd.to_numeric(deter["numpol"], errors="coerce")
deter = deter.dropna(subset=["area", "month", "numpol"])

# -----------------------------------------------------------------------------------------------
# Conversão para texto (Power BI) e salvamento
# -----------------------------------------------------------------------------------------------
deter = deter.astype(str)

# Salva o arquivo completo tratado
saida_tratado = os.path.join(resultados_dir, "deter_tratado_completo.csv")
deter.to_csv(saida_tratado, sep=";", index=False, encoding="utf-8-sig")
print(f"✅ Arquivo tratado gerado: {saida_tratado} ({len(deter)} linhas)")

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
# Carrega os dados na Pilha e Fila
# -----------------------------------------------------------------------------------------------
pilha = Pilha()
fila = Fila()

# Vamos utilizar todos os dados (não apenas UF e ano)
for _, row in deter.iterrows():
    registro = {
        "year": row["year"],
        "month": row["month"],
        "area": row["area"],
        "uf": row["uf"],
        "classname": row["classname"] if "classname" in row else "",
        "numpol": row["numpol"]
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
            # Comparar por área convertida pra número
            try:
                if float(lista[j]["area"]) > float(lista[j + 1]["area"]):
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
            pivo = float(items[len(items)//2]["area"])
        except ValueError:
            return items
        menores = [x for x in items if float(x["area"]) < pivo]
        iguais = [x for x in items if float(x["area"]) == pivo]
        maiores = [x for x in items if float(x["area"]) > pivo]
        comparacoes[0] += len(items) - 1
        return _quick_sort(menores) + iguais + _quick_sort(maiores)
    inicio = time.time()
    ordenado = _quick_sort(lista.copy())
    return ordenado, comparacoes[0], round(time.time() - inicio, 4)

# -----------------------------------------------------------------------------------------------
# Execução dos algoritmos e geração de resultados
# -----------------------------------------------------------------------------------------------
dados_para_ordenar = pilha.listar()

bubble_dados, bubble_comp, bubble_tempo = bubble_sort(dados_para_ordenar)
quick_dados, quick_comp, quick_tempo = quick_sort(dados_para_ordenar)

resultados = pd.DataFrame([
    {"Algoritmo": "Bubble Sort", "Comparações": bubble_comp, "Tempo (s)": bubble_tempo},
    {"Algoritmo": "Quick Sort", "Comparações": quick_comp, "Tempo (s)": quick_tempo}
])

# -----------------------------------------------------------------------------------------------
# Exporta apenas o arquivo de desempenho
# -----------------------------------------------------------------------------------------------
saida_performance = os.path.join(resultados_dir, "desempenho_algoritmos_deter.csv")
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
