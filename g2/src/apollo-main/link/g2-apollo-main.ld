/*
 * openCFW G2 apollo-main GNU linker script (g2c wave 2, first full link).
 *
 * Memory map from the stock image (main-analysis-only.elf, Ghidra 12.1.4):
 *   image header 0x437FE0, vector table 0x438000 (VTOR set by
 *   low_level_init_5e4228), MRAM image to 0x794324;
 *   DTCM 0x20000000 (CSTACK 0x2007D000..0x2007FB00, initial MSP 0x2007FB00);
 *   SSRAM 0x20080000..0x2037FFFF (stock zero-init reaches 0x2037CE44).
 * MRAM end 0x800000 and SSRAM 0x300000: upstream match (wave20) with
 * third-party/upstream/ambiqhal-apollo510/mcu/apollo510/regs/am_reg_base_addresses.h:74-81
 * (SSRAM_BASEADDR 0x20080000, SSRAM_MAX_SIZE 3072 KB, MRAM_BASEADDR 0x400000, MRAM_MAX_SIZE 4096 KB).
 * Stock zero-init reaches 0x2037CE44 (< 0x20380000), consistent with that size.
 * The fixed-address placement fragments under g2/src (*.ld, byte-identity
 * campaign) are NOT included here; this script links by section class only, so
 * raw-address RAM accesses in hand copies are not yet reconciled with where
 * GNU ld puts the named objects (see C-RECONSTRUCTION-PROGRESS.md).
 */
ENTRY(reset_handler_5e4232)


MEMORY
{
  /* Apollo510 ITCM: 256 KB at 0x00000000 (am_reg_base_addresses.h).
   * Stock keeps 0x40..0x58 for the IAR LZ77 delay/memcpy overlay
   * (region table 0x75D3E0). Ambiq .itcm_text / .ramfunc start after
   * that window so the overlay and HAL ramfuncs do not collide. */
  ITCM  (rx)  : ORIGIN = 0x00000058, LENGTH = 0x0003FFA8
  MRAM  (rx)  : ORIGIN = 0x00438000, LENGTH = 0x003C8000
  DTCM  (rwx) : ORIGIN = 0x20000000, LENGTH = 0x0007D000
  STACK (rw)  : ORIGIN = 0x2007D000, LENGTH = 0x00002B00
  SSRAM (rwx) : ORIGIN = 0x20080000, LENGTH = 0x00300000
}

SECTIONS
{
  .text :
  {
    _stext = .;
    KEEP(*(.isr_vector))
    /* .itcm_text / .ramfunc are NOT here: they need an ITCM VMA and an
     * MRAM LMA, copied by the region table (see .itcm_text below). Putting
     * them in MRAM .text broke Ambiq's 3-cycle delay loop and any code that
     * must run while MRAM is busy or powered down. */
    *(.text .text.* .opencfw.* .g2_rom_* .g2.rom.*)
    *(.rodata .rodata.* .g2_rom* )
    . = ALIGN(4);
    __start_kvdb_migration = .;
    KEEP(*(kvdb_migration))
    __stop_kvdb_migration = .;
    . = ALIGN(4);
    _etext = .;
  } > MRAM
  ASSERT(g2c_itcm_overlay_end - g2c_itcm_overlay_start == 24,
         "Apollo ITCM overlay must contain exactly 24 bytes")

  /* Ambiq HAL ramfuncs (.itcm_text) and any .ramfunc: execute from ITCM,
   * load from MRAM. Stock IAR used .textrw the same way (VMA ITCM, LMA
   * MRAM). ORIGIN 0x58 leaves 0x40..0x58 for the stock overlay.
   * KEEP these under --gc-sections: they are often reached only via the
   * region-table copy (LOADADDR / VMA symbols), not a live direct call
   * at link time. Vectors and kvdb_migration already use KEEP above. */
  .itcm_text : ALIGN(4)
  {
    __itcm_text_start = .;
    KEEP(*(.itcm_text .itcm_text.*))
    KEEP(*(.ramfunc .ramfunc.*))
    . = ALIGN(4);
    __itcm_text_end = .;
  } > ITCM AT > MRAM
  __itcm_text_load_start = LOADADDR(.itcm_text);
  ASSERT(__itcm_text_start >= 0x58,
         "ITCM ramfuncs must not overlap the stock 0x40 overlay")
  ASSERT(__itcm_text_end <= 0x00040000,
         "ITCM ramfuncs exceed the 256 KB ITCM")

  .ARM.exidx : { *(.ARM.exidx .ARM.exidx.*) } > MRAM

  .data : ALIGN(4)
  {
    __data_start = .;
    *(.data .data.* .g2_ram_* .g2.ram.* .g2_sync_* .g2_tx_* .g2_transaction_*)
    /* Writable named sections (.g2_locale_data_*, .g2_conversate_*_2xxxxxxx,
     * .g2_bss_*, ...) carry initial values. As orphans they were placed after
     * __data_end, so the region-table copy row never loaded them and the
     * locale tables read as zero at runtime (2026-10-31 sim check). */
    INPUT_SECTION_FLAGS (SHF_WRITE) *(.g2_*)
    . = ALIGN(4);
    __data_end = .;
  } > DTCM AT > MRAM
  __data_load_start = LOADADDR(.data);

  /* Fix 41: FreeRTOS heap_4 ucHeap (0x2f000) in DTCM, as stock: stock DTCM has an
   * otherwise-unowned 0x2f001-byte span at 0x20004557 (reloc map; next object
   * g2_production_sync_recv_data). GUESS on exact base; size match is the evidence.
   * NOLOAD: heap_4 prvHeapInit builds its free list, no zeroing needed. */
  .dtcm_heap (NOLOAD) : ALIGN(8) { *(.bss.ucHeap) } > DTCM
  /* Fix 42: zero-init objects whose stock address is DTCM (name suffix _2000xxxx.._2007xxxx)
   * live in DTCM as in stock, freeing SSRAM. Zeroed by the g2c_gnu_init.c region-table row. */
  .dtcm_bss (NOLOAD) : ALIGN(8)
  {
    __dtcm_bss_start = .;
    *(.bss.*_2000???? .bss.*_2001???? .bss.*_2002???? .bss.*_2003???? .bss.*_2004???? .bss.*_2005???? .bss.*_2006???? .bss.*_2007????)
    INCLUDE g2/src/apollo-main/link/g2-dtcm-bss.ld
    . = ALIGN(4);
    __dtcm_bss_end = .;
  } > DTCM

  /* Stock-pinned (layout genuinely required): OTA bootloader flag page shared
   * with the secure bootloader at mapped MRAM 0x007fe000. Evidence: stock
   * OTA_FileSystemSetBootloaderFlag 0x478860 programs it via nv_program, and
   * the Renode stock 2.2.6.10 run logs "ROM nv_program_main2: operation=1,
   * destination=0x007FE000, words=4, status=0" (sim-test 2026-10-26). Without
   * this the flag landed in SSRAM .bss and nv_program returned status=2. */
  .opencfw_ota_flag 0x007FE000 (NOLOAD) : { KEEP(*(.bss.opencfw.ota.bootloader_flag)) }
  ASSERT(__data_load_start + SIZEOF(.data) <= 0x007FE000, "MRAM image overlaps the OTA flag page")
  /* Stock-pinned (layout genuinely required): Cordio app_db bond records, ten
   * 256-byte rows at mapped MRAM 0x007ff000 (_CopyRecListFromNvmToRam 0x4795dc,
   * _updateOneRecordToNVM 0x4799a8). Bonds made under any firmware version live
   * here. Without this rule the section fell into SSRAM .bss (0x201ff8c0), so
   * stored bonds were never found and new ones were lost on reset; the
   * 2026-10-31 sim OTA run showed the retained phone key rejected (HCI 0x06). */
  .opencfw_mram_records 0x007FF000 (NOLOAD) : { KEEP(*(.bss.opencfw.mram.records)) }
  ASSERT(SIZEOF(.opencfw_mram_records) == 0xA00, "bond record page is 10 x 256 bytes")

  .bss (NOLOAD) : ALIGN(4)
  {
    __bss_start = .;
    *(.bss .bss.* COMMON)
    . = ALIGN(4);
    __bss_end = .;
  } > SSRAM

  .noinit (NOLOAD) : { *(.noinit .noinit.*) } > SSRAM

  .stack (NOLOAD) :
  {
    _sstack = .;
    . = ORIGIN(STACK) + LENGTH(STACK);
    _estack = .;
  } > STACK

  /DISCARD/ : { *(.llvm_addrsig) *(.note.GNU-stack) }
}
