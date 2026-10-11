case_increment_tick = 0x0800ca79;
SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
