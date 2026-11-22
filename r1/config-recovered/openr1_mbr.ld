/* Standalone source MBR page. It does not link code from S140 or the
 * bootloader, because either image may be absent during a DFU update. */
ENTRY(Reset_Handler)
MEMORY {
  FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 0x00001000
  RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 0x00001000
}
SECTIONS {
  .isr_vector 0x00000000 : { KEEP(*(.isr_vector)) } > FLASH
  .text : { *(.text*) *(.rodata*) __mbr_text_end = .; } > FLASH
  .mbr_stage_tag 0x000007fc : { KEEP(*(.mbr_stage_tag)) } > FLASH
  .mbr_stage_entry 0x00000800 : { KEEP(*(.mbr_stage_entry)) __mbr_stage_end = .; } > FLASH
  .mbr_cordio_init_tag 0x000008fc : { KEEP(*(.mbr_cordio_init_tag)) } > FLASH
  .mbr_cordio_init 0x00000900 : { KEEP(*(.mbr_cordio_init)) __mbr_cordio_init_end = .; } > FLASH
  .mbr_command_tag 0x00000afc : { KEEP(*(.mbr_command_tag)) } > FLASH
  .mbr_command 0x00000b00 : { KEEP(*(.mbr_command)) __mbr_command_end = .; } > FLASH
  .mbr_config 0x00000ff8 : { KEEP(*(.mbr_config)) } > FLASH
  .data : { *(.data*) } > RAM AT > FLASH
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } > RAM
  /DISCARD/ : { *(.comment*) *(.note*) *(.ARM.attributes*) *(.ARM.exidx*) *(.ARM.extab*) }
}
ASSERT(SIZEOF(.isr_vector) == 512, "MBR vector size changed")
ASSERT(__mbr_text_end <= 0x000007fc, "MBR text overlaps stage tag")
ASSERT(SIZEOF(.mbr_stage_tag) == 4, "MBR stage tag missing")
ASSERT(__mbr_stage_end <= 0x000008fc, "MBR stage entry overlaps Cordio init tag")
ASSERT(SIZEOF(.mbr_cordio_init_tag) == 4, "MBR Cordio init tag missing")
ASSERT(__mbr_cordio_init_end <= 0x00000afc, "MBR Cordio init overlaps command tag")
ASSERT(SIZEOF(.mbr_command_tag) == 4, "MBR command tag missing")
ASSERT(__mbr_command_end <= 0x00000ff8, "MBR command entry overlaps config")
ASSERT(SIZEOF(.mbr_config) == 8, "MBR config words missing")
ASSERT(SIZEOF(.data) == 0, "MBR reset has no data initializer")
ASSERT(SIZEOF(.bss) == 0, "MBR reset has no BSS initializer")
