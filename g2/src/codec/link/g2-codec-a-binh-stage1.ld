/* BINH A stage-1 source candidate. Its boot block is separate from codec A's
 * UART stage-1 image, which also executes at 0x10000000. The stock BINH A
 * initialized-data D-bus view starts at 0x20001028. The module descriptors,
 * source tables, clock dividers, boot state, and JEDEC sentinel occupy the
 * same 0x26c-byte window in the locked load. Code layout and byte identity
 * remain independent qualification gates.
 */
ENTRY(gx8002_image_a_stage1_reset_10000100)

MEMORY {
  CODE (rwx) : ORIGIN = 0x10000000, LENGTH = 0x00001028
  DATA (rw)  : ORIGIN = 0x20001028, LENGTH = 0x00001fd8
}

SECTIONS {
  .vectors 0x10000000 : { KEEP(*(.spl_a.vectors)) } > CODE
  .reset 0x10000100 : { KEEP(*(.spl_a.reset)) } > CODE
  .default 0x10000130 : { KEEP(*(.spl_a.default)) } > CODE
  .return_leaf 0x10000134 : { KEEP(*(.spl_a.return_leaf)) } > CODE
  /* The SDK helpers, module lookup, and clock-source leaf match their locked
     function bytes at these addresses. */
  .reg_set_val 0x10000138 : { KEEP(*(.text.__reg_set_val)) } > CODE
  .clock_source 0x1000014c : { KEEP(*(.spl_a.clock_source)) } > CODE
  .module_get_info 0x10000160 : { KEEP(*(.text.__module_get_info)) } > CODE
  .module_get_div 0x10000204 : { KEEP(*(.text.__module_get_div.isra.1)) } > CODE
  .text_before_bus 0x10000220 : {
    *(.spl_a.text)
    *(.spl_a.boot_setup .spl_a.audio_gate .spl_a.boot_mode .spl_a.clock_setup)
    *(.spl_a.osc_all_state .spl_a.osc_32k_state .spl_a.timer_start)
    *(.spl_a.clock_gate .spl_a.clock_frequency .spl_a.clock_div .spl_a.clock_dto)
    *(.spl_a.clock_init .spl_a.divmod)
  } > CODE
  /* These five adjacent C functions match the locked 0xb40..0xc3e bytes. */
  .clock_status 0x10000b40 : { KEEP(*(.spl_a.clock_status)) } > CODE
  .wait_bus 0x10000b4c : { KEEP(*(.spl_a.wait_bus)) } > CODE
  .flash_write 0x10000b5c : { KEEP(*(.spl_a.flash_write)) } > CODE
  .flash_transaction 0x10000bbc : { KEEP(*(.spl_a.flash_transaction)) } > CODE
  .wait_ready 0x10000c1c : { KEEP(*(.spl_a.wait_ready)) } > CODE
  .text 0x10000c40 : {
    *(.spl_a.clock_module .spl_a.clock_trim)
    *(.spl_a.udiv .spl_a.umod .spl_a.timer_config)
    *(.text .text.*)
    . = ALIGN(4);
  } > CODE
  .clock_trim_enable 0x10000f34 : {
    KEEP(*(.spl_a.clock_trim_enable))
  } > CODE
  .rodata 0x10000f48 : {
    *(.rodata .rodata.*)
    . = ALIGN(4);
  } > CODE
  ASSERT(SIZEOF(.vectors) == 0x100 &&
         gx8002_image_a_stage1_reset_10000100 == 0x10000100 &&
         gx8002_image_a_stage1_default_10000130 == 0x10000130,
         "BINH A stage-1 vectors and entries changed")
  ASSERT(SIZEOF(.return_leaf) == 2 && SIZEOF(.reg_set_val) == 18 &&
         SIZEOF(.clock_source) == 20 && SIZEOF(.module_get_info) == 164 &&
         SIZEOF(.module_get_div) == 28,
         "BINH A stage-1 source helper sections changed")
  ASSERT(gx8002_image_a_stage1_clock_gate_100005a4 == 0x100005a4 &&
         gx8002_image_a_stage1_clock_frequency_100006a4 == 0x100006a4,
         "BINH A stage-1 clock functions left their locked addresses")
  ASSERT(ADDR(.text_before_bus) + SIZEOF(.text_before_bus) <= 0x10000b40 &&
         SIZEOF(.clock_status) == 12 && SIZEOF(.wait_bus) == 16 &&
         SIZEOF(.flash_write) == 96 && SIZEOF(.flash_transaction) == 96 &&
         SIZEOF(.wait_ready) == 34,
         "BINH A stage-1 bus helper layout changed")
  ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x10000f34 &&
         SIZEOF(.clock_trim_enable) == 18 &&
         ADDR(.clock_trim_enable) + SIZEOF(.clock_trim_enable) <= 0x10000f48 &&
         SIZEOF(.rodata) == 0xe0 &&
         ADDR(.rodata) + SIZEOF(.rodata) <= 0x10001028,
         "BINH A stage-1 code overlaps initialized data")

  .data 0x20001028 : AT(0x10001028) {
    KEEP(*(.data.gx_clock_param_table))
    KEEP(*(.spl_a.trim_low_sources))
    KEEP(*(.spl_a.trim_high_sources))
    KEEP(*(.spl_a.clock_sources))
    KEEP(*(.data.gx_clock_dto_table))
    KEEP(*(.data.gx_clock_div_table))
    KEEP(*(.spl_a.boot_info))
    KEEP(*(.spl_a.transfer_modes))
    KEEP(*(.spl_a.uart_baud))
    KEEP(*(.spl_a.flash_jedec))
    *(.data .data.*)
    . = ALIGN(4);
  } > DATA
  .bss (NOLOAD) : { *(.bss .bss.* COMMON) } > DATA
  ASSERT(SIZEOF(.data) == 0x26c,
         "BINH A stage-1 initialized data differs in size")
  ASSERT(LOADADDR(.data) + SIZEOF(.data) <= 0x10003000,
         "BINH A stage-1 data exceeds the boot block")
}
