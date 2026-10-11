SECTIONS {
 .touch_init.app_context 0x200004e8 : AT(0xb5b4) {
  KEEP(*(.touch_init.app_threshold))
  . = ALIGN(4);
  KEEP(*(.touch_init.capsense_context))
 }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) }
}
