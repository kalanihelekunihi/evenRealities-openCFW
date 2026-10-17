SECTIONS {
  .g2_conversate_timer_callbacks_75ea90 0x75ea90 : {
    KEEP(*(.g2_conversate_timer_callbacks_75ea90))
  }
}
INSERT AFTER .rodata;
ASSERT(SIZEOF(.g2_conversate_timer_callbacks_75ea90) == 0x20,
       "Conversate timer callback table size")
ASSERT(audio_conversate_timer_callbacks_75ea90 == 0x75ea90,
       "Conversate timer callback table address")
