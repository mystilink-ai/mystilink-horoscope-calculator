CXX ?= c++
ROOT := ../..
CXXFLAGS ?= -Wall -Wextra -O2 -std=c++17
TARGET := example_natal

.PHONY: all clean run

all: $(TARGET)

$(TARGET): main.cpp $(ROOT)/bindings/c/mystilink_horoscope.c
	$(CXX) $(CXXFLAGS) -I$(ROOT)/bindings/cpp -I$(ROOT)/bindings/c \
	  -o $@ main.cpp $(ROOT)/bindings/c/mystilink_horoscope.c

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)
