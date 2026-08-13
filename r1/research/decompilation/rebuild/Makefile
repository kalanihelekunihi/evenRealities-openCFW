CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all verify clean

all: emit_image

emit_image: emit_image.c application.bytes.inc bootloader.bytes.inc uicr.bytes.inc approtect-runtime.bytes.inc
	$(CC) $(CFLAGS) emit_image.c -o $@

verify: emit_image
	./verify.py

clean:
	rm -f emit_image rebuilt-*.bin
