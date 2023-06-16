CC = clang
CFLAGS = -Wall -std=c99 -pedantic

PYTHON_VERSION = 3.7m
PYTHON_INCLUDE_PATH = /usr/include/python$(PYTHON_VERSION)

MOL_LIBRARY_PATH = .

all: molecule.py _molecule.so

clean:
	rm -f *.o *.so molecule.py molecule_wrap.c a4

mol.o: mol.c
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

molecule_wrap.c: molecule.i
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I$(PYTHON_INCLUDE_PATH) -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) molecule_wrap.o -shared -dynamiclib -o _molecule.so -L$(MOL_LIBRARY_PATH) -lmol -L/usr/lib/python$(PYTHON_VERSION)/config-$(PYTHON_VERSION)-x86_64-linux-gnu -lpython$(PYTHON_VERSION)

molecule.py: molecule_wrap.c

.PHONY: all clean
