CC=cc

OBJS1=MyVariables.o

TARGETS=MyVariables.so

CFLAGS=`net-snmp-config --cflags`
BUILDLIBS=`net-snmp-config --libs`
BUILDAGENTLIBS=`net-snmp-config --agent-libs`

# shared library flags
DLFLAGS=-fPIC -shared -g -O0 -O

all: $(TARGETS)

clean:
	rm $(TARGETS)

MyVariables.so: MyVariables.c Makefile
	$(CC) $(CFLAGS) $(DLFLAGS) -o MyVariables.so MyVariables.c $(BUILDAGENTLIBS)

