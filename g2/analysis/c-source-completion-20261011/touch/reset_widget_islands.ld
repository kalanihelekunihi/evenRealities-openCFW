PHDRS { widgets PT_LOAD; position PT_LOAD; }
SECTIONS {
 .widgets 0x20000548 : AT(0xb614) { KEEP(*(.touch_init.widget_contexts)) } :widgets
 .position 0x20000656 : AT(0xb722) { KEEP(*(.touch_init.slider_position)) } :position
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
 ASSERT(SIZEOF(.widgets)==180,"three widget contexts")
 ASSERT(SIZEOF(.position)==8,"slider position")
}
