import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# -----------------------------------------------------------------------------------------------
# Previsão de desmatamento - PRODES
# -----------------------------------------------------------------------------------------------

# Define caminhos base e arquivos ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
resultados_dir = os.path.join(BASE_DIR, "..", "resultados")

arquivo_estado = os.path.join(resultados_dir, "prodes_agregado_estado_ano.csv")
arquivo_municipio = os.path.join(resultados_dir, "prodes_agregado_municipio_ano.csv")
saida_geral = os.path.join(resultados_dir, "previsoes_prodes_geral.csv")
saida_estado = os.path.join(resultados_dir, "previsoes_prodes_estados.csv")
saida_municipio = os.path.join(resultados_dir, "previsoes_prodes_cidades.csv")

# -----------------------------------------------------------------------------------------------
# Funções auxiliares
# -----------------------------------------------------------------------------------------------

# Normaliza ano
def normaliza_ano(coluna):
    c = coluna.astype(str).str.split("/").str[-1]
    return pd.to_numeric(c, errors="coerce")

# Ajusta colunas e converte tipos numéricos
def prepara_dados(df, coluna_grupo=None):
    df = df.copy()
    df.columns = df.columns.str.strip()
    df["year"] = normaliza_ano(df["year"])
    df["areakm"] = df["areakm"].astype(str).str.replace(",", ".", regex=False).astype(float)
    if coluna_grupo:
        df = df.dropna(subset=["year", "areakm", coluna_grupo])
    else:
        df = df.dropna(subset=["year", "areakm"])
    return df.sort_values(["year"])

# -----------------------------------------------------------------------------------------------
# Função de previsão com regressão linear
# -----------------------------------------------------------------------------------------------

def gerar_previsoes(df, coluna_grupo=None, nome_grupo=None):
    resultados = []
    modelo = LinearRegression()
    anos_futuros = pd.DataFrame({"year": [2025, 2026, 2027, 2028, 2029, 2030]})

    # Previsão geral (sem agrupamento)
    if not coluna_grupo:
        if len(df) < 2:
            return pd.DataFrame()
        X, y = df[["year"]], df["areakm"]
        if len(df) >= 5:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)
            mse = round(mean_squared_error(y_test, y_pred), 4)
            r2 = round(r2_score(y_test, y_pred), 4)
        else:
            modelo.fit(X, y)
            mse, r2 = "", ""
        previsoes = modelo.predict(anos_futuros)
        for ano, valor in zip(anos_futuros["year"], previsoes):
            resultados.append({
                "Ano": int(ano),
                "Área Prevista (km²)": round(float(valor), 2),
                "MSE": mse,
                "R²": r2
            })
        return pd.DataFrame(resultados)

    # Previsões por agrupamento (estado ou município)
    for grupo, dados in df.groupby(coluna_grupo):
        if len(dados) < 2:
            continue
        X, y = dados[["year"]], dados["areakm"]
        if len(dados) >= 5:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)
            mse = round(mean_squared_error(y_test, y_pred), 4)
            r2 = round(r2_score(y_test, y_pred), 4)
        else:
            modelo.fit(X, y)
            mse, r2 = "", ""
        previsoes = modelo.predict(anos_futuros)
        for ano, valor in zip(anos_futuros["year"], previsoes):
            resultados.append({
                nome_grupo: grupo,
                "Ano": int(ano),
                "Área Prevista (km²)": round(float(valor), 2),
                "MSE": mse,
                "R²": r2
            })
    return pd.DataFrame(resultados)

# -----------------------------------------------------------------------------------------------
# Execução principal
# -----------------------------------------------------------------------------------------------

print("----------------------------------------------")
print("Verificando base de dados:")
print("----------------------------------------------")

# Verifica base principal
if os.path.exists(arquivo_estado):
    print(f"Base de estados encontrada: {os.path.basename(arquivo_estado)}")
else:
    raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_estado}")

# Base de municípios
if os.path.exists(arquivo_municipio):
    print(f"Base de municípios encontrada: {os.path.basename(arquivo_municipio)}")
else:
    print("Base de municípios não encontrada.")

# -----------------------------------------------------------------------------------------------
# Previsão geral (Amazônia como um todo)
# -----------------------------------------------------------------------------------------------

df_geral = pd.read_csv(arquivo_estado, sep=";", encoding="utf-8-sig")
df_geral = prepara_dados(df_geral)
df_geral = df_geral.groupby("year", as_index=False)["areakm"].sum()
previsoes_gerais = gerar_previsoes(df_geral)

# -----------------------------------------------------------------------------------------------
# Previsões por Estado
# -----------------------------------------------------------------------------------------------

df_estados = prepara_dados(pd.read_csv(arquivo_estado, sep=";", encoding="utf-8-sig"), "state")
previsoes_estados = gerar_previsoes(df_estados, "state", "UF")

# -----------------------------------------------------------------------------------------------
# Previsões por Município
# -----------------------------------------------------------------------------------------------

if os.path.exists(arquivo_municipio):
    df_municipios = prepara_dados(pd.read_csv(arquivo_municipio, sep=";", encoding="utf-8-sig"), "municipality")
    previsoes_municipios = gerar_previsoes(df_municipios, "municipality", "Município")
else:
    previsoes_municipios = pd.DataFrame()

# -----------------------------------------------------------------------------------------------
# Exibição final
# -----------------------------------------------------------------------------------------------

print("\n-----------------------------------------------")
print("Prévia dos resultados:")
print("-----------------------------------------------")

# Geral
print("\nPrévia das previsões gerais (Amazônia):")
if not previsoes_gerais.empty:
    print(previsoes_gerais.head(10).to_string(index=False))
else:
    print("Nenhuma previsão disponível.")

# Estados
print("\nPrévia das previsões por Estado:")
if not previsoes_estados.empty:
    print(previsoes_estados.head(10).to_string(index=False))
else:
    print("Nenhuma previsão disponível.")

# Municípios
print("\nPrévia das previsões por Município:")
if not previsoes_municipios.empty:
    print(previsoes_municipios.head(10).to_string(index=False))
else:
    print("Nenhuma previsão disponível.")

