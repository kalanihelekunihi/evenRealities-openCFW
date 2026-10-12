/* Test placement only: retained stock callback table, relocatable selected C. */
ENTRY(opencfw_boot_init_table_default)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  . = 0x433440;
  .boot_initializer_callbacks : { KEEP(*(.boot_initializer_callbacks)) }
  .boot_context_config : { *(.boot_context_config) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note.GNU-stack*) }
}
