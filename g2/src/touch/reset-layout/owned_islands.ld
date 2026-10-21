/* Partial absolute placement of independently source-owned reset data only.
 * Holes are deliberately absent; this is not a 964-byte data image. */
PHDRS { cfg PT_LOAD; d32 PT_LOAD; dmhz PT_LOAD; dkhz PT_LOAD; clk PT_LOAD; }
SECTIONS {
  .touch_config 0x200004c0 : AT(0xb58c) { KEEP(*(.touch_init.eeprom)) } :cfg
  .touch_delay32k 0x2000086c : AT(0xb938) { KEEP(*(.data.cy_delay32kMs)) } :d32
  .touch_delay_mhz 0x20000870 : AT(0xb93c) { KEEP(*(.data.cy_delayFreqMhz)) } :dmhz
  .touch_delay_khz 0x20000874 : AT(0xb940) { KEEP(*(.data.cy_delayFreqKhz)) } :dkhz
  .touch_system_clock 0x20000878 : AT(0xb944) { KEEP(*(.touch_init.system_clock)) } :clk
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
  ASSERT(SIZEOF(.touch_config)==12, "EEPROM reset config")
  ASSERT(SIZEOF(.touch_delay32k)==4, "32k delay scale")
  ASSERT(SIZEOF(.touch_delay_mhz)==1, "MHz delay scale")
  ASSERT(SIZEOF(.touch_delay_khz)==4, "kHz delay scale")
  ASSERT(SIZEOF(.touch_system_clock)==4, "system clock reset value")
}
