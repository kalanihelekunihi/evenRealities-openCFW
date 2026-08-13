CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
BUILD_DIR := build
TEST_BINARY := $(BUILD_DIR)/test_model

.PHONY: all test clean

all: $(TEST_BINARY)

$(TEST_BINARY): src/r1_bootloader_model.c tests/test_model.c include/r1_bootloader_model.h
	mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) src/r1_bootloader_model.c tests/test_model.c -o $@

test: $(TEST_BINARY)
	./$(TEST_BINARY)

clean:
	rm -rf -- $(BUILD_DIR)
