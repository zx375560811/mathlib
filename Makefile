all: mathlib

mathlib: main.c db.c viewer.c
	gcc -o mathlib main.c db.c viewer.c -lsqlite3

clean:
	rm -f mathlib books.db
