from typing import Annotated

from fastapi import Depends

from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "db.sqlite3"
engine = create_engine(f"sqlite:///{sqlite_file_name}")


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]