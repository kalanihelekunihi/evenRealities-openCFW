ENTRY(opencfw_boot_spotmgr_power_state_update_a)
MEMORY { FLASH (rx) : ORIGIN = 0x10000, LENGTH = 0x10000 }
SECTIONS {
  . = ORIGIN(FLASH);
  .text : { KEEP(*(.text.opencfw_boot_spotmgr_power_state_update_a)) *(.text*) *(.rodata*) } > FLASH
  .data : { *(.data*) } > FLASH
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } > FLASH
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
