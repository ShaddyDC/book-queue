import subprocess
import os
import shutil
from more_itertools import tabulate
import typer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, select, delete
from sqlalchemy.orm import Session, declarative_base
import datetime
from tabulate import tabulate

app = typer.Typer()
Base = declarative_base()
folder = "./"


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    file = Column(String, unique=True)
    modified = Column(DateTime)
    priority = Column(Integer)


def get_session():
    engine = create_engine(f"sqlite:///{folder}/db")
    Base.metadata.create_all(engine)

    return Session(engine)


@app.command()
def add(file: str, priority: int = 10):
    if not os.path.exists(file):
        print(f"File '{file}' does not exist.")
        return

    basename = os.path.basename(file)
    local_file = folder + basename

    if os.path.exists(local_file) and not typer.confirm("File already exests, overwrite?"):
        return

    shutil.copy2(file, local_file)

    session = get_session()
    if session.query(Book.id).filter_by(file=basename).first() is not None:
        # TODO: update priority instead
        print(f"File {basename} already in libary.")
        return

    session.add(
        Book(file=basename, modified=datetime.datetime.now(), priority=priority))
    session.commit()
    print(f"Added file {file} to library.")


@app.command()
def read():
    session = get_session()
    current = datetime.datetime.now()
    books_queried = session.query(Book).all()
    books = [(book.priority * (current - book.modified).total_seconds() / datetime.timedelta(days=1).total_seconds(), book)
             for book in books_queried]
    if not books:
        print("No books in library.")
        return
    books.sort(key=lambda x: x[0], reverse=True)
    table = [[i+1, book.file, priority, book.priority, book.modified]
             for (i, (priority, book)) in enumerate(books)]
    print(tabulate(table, headers=["No", "File",
          "Acc Prio", "Prio", "Modified"], tablefmt="github"))
    choice = typer.prompt("Read Book", default=1, type=int)
    if not 1 <= choice <= len(books):
        print("Invalid choice")
        return
    book = books[choice-1][1]
    subprocess.run(["zathura", folder + book.file])
    book.modified = datetime.datetime.now()
    session.commit()


@app.command()
def clear_db():
    session = get_session()
    session.execute(delete(Book))
    session.commit()


if __name__ == '__main__':
    app()
