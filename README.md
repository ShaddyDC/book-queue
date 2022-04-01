# Book-Queue

Simple tool to manage a collection of in-progress books to get a varied reading intake, written in Python with [Poetry](https://python-poetry.org/), [Typer](https://typer.tiangolo.com/), and [SQLAlchemy](https://www.sqlalchemy.org/).

## Features

- Manage books in collection
- Prioritise queue based on importance and time since last access
- Read books (by default in [Zathura](https://pwmt.org/projects/zathura/))

```
> book-queue read
| No  | File                                                                                             | Acc Prio    | Prio | Modified                   |
| --- | ------------------------------------------------------------------------------------------------ | ----------- | ---- | -------------------------- |
| 1   | Introduction_to_algorithms-3rd Edition.pdf                                                       | 0.0107284   | 50   | 2022-04-01 15:00:57.944001 |
| 2   | Adrian Ostrowski_ Piotr Gaczkowski - Software Architecture with C++-Packt Publishing (2021).epub | 0.000870491 | 10   | 2022-04-01 15:01:08.961704 |

```

## Getting started

You should be able to install book-queue with pip.

```
pip install book-queue
```

You will find instructions for use with `book-queue --help`.
