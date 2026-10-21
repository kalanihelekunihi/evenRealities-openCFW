/* Isolated proof layout for the authenticated reset descriptor positions.
 * The data payload comes from a separate synthetic fixture, not firmware. */
ENTRY(g2_touch_candidate_reset_tables)
SECTIONS {
  .text 0x8000 : { *(.text*) }
  .copy_table 0xb578 : {
    LONG(LOADADDR(.touch_data))
    LONG(ADDR(.touch_data))
    LONG(SIZEOF(.touch_data) / 4)
  }
  .zero_table 0xb584 : {
    LONG(ADDR(.touch_bss))
    LONG(SIZEOF(.touch_bss) / 4)
  }
  .touch_data 0x200004c0 : AT(0xb58c) { *(.touch_data) }
  .touch_bss 0x200008a8 (NOLOAD) : { *(.touch_bss) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) }
  ASSERT(SIZEOF(.copy_table) == 12, "copy descriptor size")
  ASSERT(SIZEOF(.zero_table) == 8, "zero descriptor size")
  ASSERT(SIZEOF(.touch_data) == 964, "synthetic data word count")
  ASSERT(SIZEOF(.touch_bss) == 1712, "synthetic bss word count")
}
