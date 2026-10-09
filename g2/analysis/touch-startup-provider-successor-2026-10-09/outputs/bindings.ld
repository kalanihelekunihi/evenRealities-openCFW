SECTIONS { .text 0xA9E4 : { *(.text.__libc_init_array) } .init 0xAA44 : { *(.init) } .fini 0xAA50 : { *(.fini) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }
__preinit_array_start = 0x2000087C;
__preinit_array_end = 0x2000087C;
__init_array_start = 0x2000087C;
__init_array_end = 0x20000880;
