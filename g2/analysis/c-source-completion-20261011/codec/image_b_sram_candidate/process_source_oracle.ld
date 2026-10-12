ENTRY(_start)
SECTIONS {
  . = 0x10000000;
  .text : { *(.text.start) *(.text*) }
  .rodata : { *(.rodata*) }
  . = 0x21000000;
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
