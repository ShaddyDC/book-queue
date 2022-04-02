# Book-Queue

Simple tool to manage a collection of in-progress books to get a varied reading intake, written in Python with [Poetry](https://python-poetry.org/), [Typer](https://typer.tiangolo.com/), and [SQLAlchemy](https://www.sqlalchemy.org/).

## Features

- Manage books in collection
- Prioritise queue based on importance and time since last access
- Read books (by default in [Zathura](https://pwmt.org/projects/zathura/))

```bash
foo@bar:~$ book-queue read
| No  | File                                                                                             | Acc Prio    | Prio | Modified                   |
| --- | ------------------------------------------------------------------------------------------------ | ----------- | ---- | -------------------------- |
| 1   | Introduction_to_algorithms-3rd Edition.pdf                                                       | 0.0107284   | 50   | 2022-04-01 15:00:57.944001 |
| 2   | Adrian Ostrowski_ Piotr Gaczkowski - Software Architecture with C++-Packt Publishing (2021).epub | 0.000870491 | 10   | 2022-04-01 15:01:08.961704 |
Pick book [1]:
# Opening PDF in Zathura...
(d)one, (q)uit, (r)emove [d]:
# Resetting accumulated priotity of book...
```

## Getting started

You should be able to install book-queue with pip.

```
pip install book-queue
```

You will find instructions for use with `book-queue --help`.


### How do I handle many varying media types?

By default, book-queue uses zathura, which can for example support EPUB besides PDF with the [mupdf library](https://pwmt.org/projects/zathura-pdf-mupdf/).

To handle different files more flexibly, you may use a little helper. While this example is linux-specific, a similar approach is possible on Windows.

```bash
foo@bar:~$ echo '#!/bin/sh

file="$1"
extension="${file##*.}"

if [ "$extension" = "md" ]; then
    base=$(basename -- "$file")
    out="/tmp/${base%.*}.pdf"
    pandoc "$file" -o "$out"
    zathura "$out"
elif [ "$extension" = "link" ]; then
    firefox $(cat "$file")
elif [ "$extension" = "youtube" ]; then
    mpv $(cat "$file")
elif [ "$extension" = "pdf" ]; then
    zathura "$file"
else
    echo "File type not supported."
fi' > runner.sh && chmod +x runner.sh
foo@bar:~$ book-queue add README.md
foo@bar:~$ echo "https://github.com/ShaddyDC/book-queue" > important.link && book-queue add important.link
foo@bar:~$ echo "https://www.youtube.com/watch?v=dQw4w9WgXcQ" > good_video.youtube && book-queue add good_video.youtube
foo@bar:~$ book-queue add some.pdf
foo@bar:~$ touch broken_file && book-queue add broken_file
foo@bar:~$ book-queue read --reader "$PWD/runner.sh"
```

This will open
- the Markdown in Zathura after conversion to PDF (requires [Pandoc](https://pandoc.org/))
- the link in Firefox (naturally, requires [Firefox](https://www.mozilla.org/en-US/firefox/new/))
- the YouTube video in mpv (you guessed it, requires [mpv](https://mpv.io/))
- the PDF in Zathura
- the broken file will just print "File type not supported"
