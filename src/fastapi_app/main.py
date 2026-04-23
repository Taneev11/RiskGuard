from typing import List
from fastapi import FastAPI
from sqlmodel import SQLModel, Session, create_engine, select, Field

#table model
class Table1(SQLModel, table=True):
    no: int | None = Field(default = None, primary_key=True)
    name: str

DATABASE_URL = "postgresql+psycopg://user1:password@localhost:5432/db1"
engine = create_engine(DATABASE_URL)

app = FastAPI()

@app.get("/table1", response_model=List[Table1])
def get_items():
    with Session(engine) as session:
        statement = select(Table1)
        results = session.exec(statement).all()
        return results

