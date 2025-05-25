
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URI = "postgresql+psycopg2://postgres:password#@localhost:5432/postgres?options=-csearch_path%3DprodjectX"

engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

try:
    with engine.connect() as connection:
        print("Успех подключения к БД!")
except Exception as e:
    print(f"Ошибка подключения: {e}")