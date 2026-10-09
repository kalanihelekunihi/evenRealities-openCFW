SECTIONS { .text 0xA9AC : { *(.text.exit) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }
_exit = 0xAA41;
__stdio_exit_handler = 0x20000F54;
