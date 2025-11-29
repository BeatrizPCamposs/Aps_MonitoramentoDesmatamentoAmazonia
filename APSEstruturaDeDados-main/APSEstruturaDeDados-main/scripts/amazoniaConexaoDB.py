from sqlalchemy import create_engine, types
import pandas as pd
from pathlib import Path

# ============================================
#   APS - Banco Amazonia (Versão Multi-Tabelas)
#   Cria uma tabela no banco para cada CSV
# ============================================

# Caminho base
BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "resultados"

# Conexão com o banco Neon
DB_URL = "postgresql+psycopg2://neondb_owner:npg_bmfLc7aU3MZW@ep-empty-mouse-ad6tcjm8-pooler.c-2.us-east-1.aws.neon.tech/dbAmazonia?sslmode=require"
engine = create_engine(DB_URL)

# ----------------------------
# 🔹 Função para criar tabela de cada CSV
# ----------------------------
def enviar_csv_para_banco(arquivo_csv: Path):
    nome_tabela = arquivo_csv.stem.lower()  # nome da tabela = nome do arquivo (sem extensão)
    print(f"\n📦 Processando arquivo: {arquivo_csv.name}")

    try:
        # Detecta separador ( ; ou , )
        with open(arquivo_csv, "r", encoding="utf-8") as f:
            primeira_linha = f.readline()
        separador = ";" if ";" in primeira_linha else ","

        # Lê CSV e converte tudo para texto
        df = pd.read_csv(arquivo_csv, sep=separador, dtype=str)

        # Limpa nomes de colunas
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            .str.replace(".", "_")
        )

        # Converte todas as colunas para texto (garante compatibilidade Power BI)
        df = df.astype(str)
        dtype_map = {col: types.TEXT() for col in df.columns}

        # Envia para o banco
        df.to_sql(nome_tabela, engine, if_exists="replace", index=False, dtype=dtype_map)
        print(f"✅ Tabela '{nome_tabela}' criada/atualizada com sucesso! ({len(df):,} linhas, {len(df.columns)} colunas)")

    except Exception as e:
        print(f"❌ Erro ao processar {arquivo_csv.name}: {e}")

# ----------------------------
# 🔹 Execução principal
# ----------------------------
if __name__ == "__main__":
    print("\n🚀 Enviando todos os CSVs da pasta 'resultados' para o banco dbAmazonia...\n")

    arquivos = list(RESULTS_DIR.glob("*.csv"))

    if not arquivos:
        print("⚠️ Nenhum arquivo CSV encontrado na pasta 'resultados'.")
    else:
        for arquivo in arquivos:
            enviar_csv_para_banco(arquivo)

    print("\n🌱 Upload concluído! Todas as tabelas estão disponíveis no banco.\n")
