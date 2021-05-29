CC=g++
CFLAGS=-Wall -g -lm
HFILES = projekt.h
CFILES = projekt.cpp

proj: $(CFILES) $(HFILES)
	$(CC) -o $@ $(CFILES) $(CFLAGS)

run:
	./proj -v

clean:
	rm -f *.o *~ proj
