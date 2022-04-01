import pathlib
import subprocess
import os
import shutil
from typing import Any, Callable
from more_itertools import tabulate
import typer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, delete
from sqlalchemy.orm import Session, declarative_base
import datetime
from tabulate import tabulate
from pathlib import Path

APP_NAME = "Book Queue"
APP_VERSION = "0.1.0"

app = typer.Typer(name=APP_NAME, help=APP_NAME)

Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    file = Column(String, unique=True)
    modified = Column(DateTime)
    priority = Column(Integer)


def get_folder():
    folder = Path(typer.get_app_dir(APP_NAME))
    if not folder.exists():
        typer.echo(f"Creating folder {folder}")
        os.mkdir(folder)
    return folder


def get_session():
    folder = get_folder()
    engine = create_engine(f"sqlite:///{folder / 'books.db'}")
    Base.metadata.create_all(engine)

    return Session(engine)


def prompt(message: str, validator: Callable[[Any], bool] = None, default=None, **kwargs):
    while True:
        value = typer.prompt(message, default=default, **kwargs)
        if validator is None or validator(value):
            return value
        else:
            typer.echo(f"Invalid input: {value}")


def book_acc_priority(book: Book, current: datetime.datetime):
    return book.priority * (current - book.modified).total_seconds() / datetime.timedelta(days=1).total_seconds()


def select_book(session: Session):
    current = datetime.datetime.now()
    books_queried = session.query(Book).all()
    books = [(book_acc_priority(book, current), book)
             for book in books_queried]

    if len(books) == 0:
        typer.echo("No books found")
        return None

    books.sort(key=lambda x: x[0], reverse=True)
    table = [[i+1, book.file, priority, book.priority, book.modified]
             for (i, (priority, book)) in enumerate(books)]
    typer.echo(tabulate(table, headers=["No", "File",
                                        "Acc Prio", "Prio", "Modified"], tablefmt="github"))
    choice = prompt("Pick book", default=1, type=int,
                    validator=lambda x: 1 <= x <= len(books))
    return books[choice-1][1]


def remove_book(session: Session, book: Book):
    session.delete(book)
    os.remove(get_folder() / book.file)
    session.commit()


@app.command()
def add(file: str, priority: int = 10):
    if not os.path.exists(file):
        typer.echo(f"File '{file}' does not exist.")
        return

    basename = os.path.basename(file)
    local_file = get_folder() / basename

    if not os.path.exists(local_file) or typer.confirm("File {basename} already exists, overwrite?"):
        shutil.copy2(file, local_file)

    session = get_session()
    if book := session.query(Book).filter_by(file=basename).first():
        book.priority = priority
        book.modified = datetime.datetime.now()
        session.commit()
        typer.echo(f"Updated priority of existing {basename} to {priority}.")
        return

    session.add(
        Book(file=basename, modified=datetime.datetime.now(), priority=priority))
    session.commit()
    typer.echo(f"Added file {file} to library.")


@app.command()
def remove(file: str):
    file = os.path.basename(file)
    session = get_session()
    book = session.query(Book).filter_by(file=file).first()
    if book is None:
        typer.echo(f"File {file} not found in library.")
        return

    remove_book(session, book)
    typer.echo(f"Removed file {file} from library.")


@app.command()
def read(reader: str = "zathura"):
    session = get_session()
    book = select_book(session)

    if book is None:
        return

    subprocess.run([reader, get_folder() / book.file])

    choice = prompt("(d)one, (q)uit, (r)emove", default="d",
                    type=str, validator=lambda x: x in ["d", "q", "r"])
    if choice == "d":
        book.modified = datetime.datetime.now()
        session.commit()
        typer.echo(f"Rescheduled {book.file} for reading.")
    elif choice == "q":
        return
    elif choice == "r":
        remove_book(session, book)
        typer.echo(f"Removed book {book.file} from library.")


@app.command()
def clear_db():
    session = get_session()
    session.execute(delete(Book))
    session.commit()


if __name__ == '__main__':
    app()
