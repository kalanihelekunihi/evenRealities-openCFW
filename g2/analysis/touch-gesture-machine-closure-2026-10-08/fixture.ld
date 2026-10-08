/* Selected independent source in offline guest, never production linker input. */
SECTIONS {
 .native_gesture 0x4070 : { *(.text.touch_gesture_step) }
 .native_support 0x110000 : { *(.text*) }
}
ASSERT(SIZEOF(.native_gesture) <= 874, "gesture body exceeds original extent")
