ENTRY(__libc_init_array)
_init = 0xAA45;
__preinit_array_start = 0x2000087C;
__preinit_array_end = 0x2000087C;
__init_array_start = 0x2000087C;
__init_array_end = 0x20000880;
SECTIONS { .text 0xA9E4 : { *(.text.__libc_init_array) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) } }
