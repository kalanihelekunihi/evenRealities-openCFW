/* Offline selected-section placement only; not a production linker script. */
SECTIONS {
 .native_speed 0x3efc : { *(.text.touch_gesture_speed) }
 .native_support 0x110000 : { *(.text.divide) }
}
ASSERT(SIZEOF(.native_speed) <= 324, "speed exceeds original helper extent")
