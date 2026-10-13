SECTIONS { .internal 0x20000c50 (NOLOAD) : { *(.touch_bss.internal_context) } ASSERT(SIZEOF(.internal)==120,"LP context extent") }
