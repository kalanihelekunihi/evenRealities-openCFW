/* Experimental source-owned CASE placement, not stock-byte layout. */
ENTRY(case_reset_entry_0144)
SECTIONS {
  . = 0x08000000;
  .isr_vector : { KEEP(*(.isr_vector)) }
  . = ALIGN(4);
  .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
