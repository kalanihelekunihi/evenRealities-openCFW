ENTRY(spotmgr_init_42abbc_native)
SECTIONS
{
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  . = ALIGN(4);
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
