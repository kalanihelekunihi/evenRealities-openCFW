ENTRY(__aeabi_idiv)
SECTIONS { .signed 0xA7D4 : { *signed.o(.text) } .zero 0xA9A8 : { *zero.o(.text) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
