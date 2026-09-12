# Compile against the C binding (requires mystilink-horoscope on PATH).
CC ?= cc
ROOT := ../..
CFLAGS ?= -Wall -Wextra -O2
TARGET := example_natal

.PHONY: all clean run

all: $(TARGET)

$(TARGET): main.c $(ROOT)/bindings/c/mystilink_horoscope.c
	$(CC) $(CFLAGS) -I$(ROOT)/bindings/c -o $@ main.c $(ROOT)/bindings/c/mystilink_horoscope.c

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)
