MEMORY
{
  FLASH (rx)  : ORIGIN = 0x00027000, LENGTH = 0x000C9000
  RAM   (rwx) : ORIGIN = 0x200064A8, LENGTH = 0x00039B58
}

SECTIONS
{
  .text : { KEEP(*(.isr_vector)) *(.text*) *(.rodata*) } > FLASH
  .data : { *(.data*) } > RAM AT > FLASH
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } > RAM
}

