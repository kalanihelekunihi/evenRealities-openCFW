/* Exploratory Boot co-placement: source callbacks resolve to linked symbols.
 * The bound ends before the main OTA preamble at 0x437fe0. The package
 * validator allows Boot bytes up to main execution base 0x438000, while the
 * 32-byte preamble occupies 0x437fe0..0x437fff in the OTA address coordinate.
 * This does not establish image completeness or physical flashing behavior.
 */
ENTRY(opencfw_boot_reset_entry)
MEMORY {
  FLASH (rx) : ORIGIN = 0x00410000, LENGTH = 0x00027fe0
  SRAM (rwx) : ORIGIN = 0x20000000, LENGTH = 0x00080000
}
opencfw_boot_rom48 = 0x00000049;
opencfw_boot_rom_delay_cycles = 0x00000041;
opencfw_boot_rom_mram_program = 0x0200ff21;
SECTIONS {
  .boot_vectors : { KEEP(*(.boot_vectors)) } > FLASH
  .text : { *(.text*) *(.rodata*) *(.ARM.extab*) *(.ARM.exidx*) } > FLASH
  .data : { *(.data*) } > SRAM AT> FLASH
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } > SRAM
  /DISCARD/ : { *(.comment*) *(.note.GNU-stack*) }
}
ASSERT(ADDR(.boot_vectors) == 0x00410000, "Boot vector base moved")
ASSERT(SIZEOF(.boot_vectors) == 1024, "Boot 256-word vector table changed size")
