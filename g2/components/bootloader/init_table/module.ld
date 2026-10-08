ENTRY(opencfw_boot_init_table_run)
PHDRS {
  text PT_LOAD FLAGS(5);
}
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
