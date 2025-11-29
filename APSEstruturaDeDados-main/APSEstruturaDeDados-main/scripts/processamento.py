import os
import pandas as pd

# -----------------------------------------------------------------------------------------------
# Processamento dos Dados - PRODES e DETER
# -----------------------------------------------------------------------------------------------

# Define caminhos base e arquivos ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dados_path = os.path.join(BASE_DIR, "..", "dados")
deter_file = os.path.join(dados_path, "DETER_BASE_DE_ALARMES.csv")
prodes_file = os.path.join(dados_path, "PRODES_BASE_DE_DESMATAMENTO_POR_ANOS.csv")

# Verifica existência dos arquivos --------------------------------------------------------------
for arquivo in [deter_file, prodes_file]:
    if not os.path.exists(arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

# Lê os arquivos CSV com tratamento de encoding -------------------------------------------------

# DETER - Tratamento da base de dados
deter = pd.read_csv(deter_file, sep=";", encoding="utf-8-sig")

# PRODES - Tratamento da base de dados
try:
    prodes = pd.read_csv(prodes_file, sep=";", encoding="utf-8-sig")
except UnicodeDecodeError:
    prodes = pd.read_csv(prodes_file, sep=";", encoding="latin1")

# Converte e arredonda os valores numéricos -----------------------------------------------------
if "area" in deter.columns:
    deter["area"] = (
        deter["area"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
        .round(2)
    )

if "areakm" in prodes.columns:
    prodes["areakm"] = (
        prodes["areakm"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
        .round(2)
)

# Retorna prévia do resultado -------------------------------------------------------------------
print("DETER:\n", deter.head(), "\n")
print("PRODES:\n", prodes.head())
