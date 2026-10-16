SECTIONS {
 . = 0x000286f0;
 .r1.scanf.width_limit : { *(.r1.scanf.width_limit) }
 . = 0x000bda90;
 .r1.ctype.window : { *(.r1.ctype.window) }
 . = 0x01000000;
 .text : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
