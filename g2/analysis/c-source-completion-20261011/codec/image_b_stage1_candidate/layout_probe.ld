/* Experimental BINH-B stage1 layout; stock stage2 reset is authenticated. */
ENTRY(gx8002_image_b_stage1_reset_10000100)
PROVIDE(gx8002_image_b_stage2_reset_10003100 = 0x10003100);
SECTIONS {
  .spl.vectors 0x10000000 : { KEEP(*(.spl.vectors)) }
  .spl.reset 0x10000100 : { KEEP(*(.spl.reset)) }
  .spl.default : { KEEP(*(.spl.default)) }
  .stage1_text : { *(.text .text.*) }
  .stage1_rodata : { *(.rodata .rodata.*) }
  ASSERT(SIZEOF(.spl.vectors) == 0x100, "stage1 vector span")
  ASSERT(ADDR(.stage1_rodata) + SIZEOF(.stage1_rodata) <= 0x100014c8, "stage1 text and rodata overlap initialized data")
  .clock_param 0x200014c8 : AT(0x100014c8) { KEEP(*(.data.gx_clock_param_table)) }
  .clock_sources 0x20001688 : AT(0x10001688) { KEEP(*(.data.gx_stage1_sources)) }
  .clock_dto 0x200016d8 : AT(0x100016d8) { KEEP(*(.data.gx_clock_dto_table)) }
  .clock_div 0x200016dc : AT(0x100016dc) { KEEP(*(.data.gx_clock_div_table)) }
  .boot_info 0x20001720 : AT(0x10001720) { KEEP(*(.stage1.boot_info)) }
  .transfer_modes 0x20001728 : AT(0x10001728) { KEEP(*(.stage1.transfer_modes)) }
  .uart_baud 0x2000172c : AT(0x1000172c) { KEEP(*(.stage1.uart_baud)) }
  .flash_jedec 0x20001730 : AT(0x10001730) { KEEP(*(.stage1.flash_jedec)) }
  .extra_data 0x20001734 : { *(.data .data.*) }
  .bss 0x20001738 (NOLOAD) : { *(.bss .bss.* COMMON) }
  ASSERT(SIZEOF(.extra_data) == 0, "unplaced initialized stage1 data")
  ASSERT(SIZEOF(.bss) == 0, "unplaced stage1 BSS")
  ASSERT(LOADADDR(.flash_jedec) + SIZEOF(.flash_jedec) <= 0x10003000, "stage1 load exceeds 12KiB")
  /DISCARD/ : { *(.comment) *(.note*) *(.csky_stack_size) }
}
