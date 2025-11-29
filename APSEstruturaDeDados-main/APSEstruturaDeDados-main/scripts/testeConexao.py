from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://neondb_owner:npg_bmfLc7aU3MZW@ep-empty-mouse-ad6tcjm8-pooler.c-2.us-east-1.aws.neon.tech/dbAmazonia?sslmode=require"

try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        print("✅ Conexão com o PostgreSQL (Neon) bem-sucedida!")
except Exception as e:
    print("❌ Erro na conexão:", e)
