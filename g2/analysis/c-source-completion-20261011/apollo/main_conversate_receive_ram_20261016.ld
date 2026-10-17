INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_conversate_response_ram_20261016.ld"
SECTIONS {
  .g2_conversate_last_magic_20074ff8 0x20074ff8 (NOLOAD) : {
    KEEP(*(.g2_conversate_last_magic_20074ff8))
  }
  .g2_conversate_last_frame_tick_2007485c 0x2007485c (NOLOAD) : {
    KEEP(*(.g2_conversate_last_frame_tick_2007485c))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_last_magic_20074ff8) == 1,
       "Conversate magic cell size")
ASSERT(SIZEOF(.g2_conversate_last_frame_tick_2007485c) == 4,
       "Conversate frame tick size")
ASSERT(audio_conversate_last_magic_20074ff8 == 0x20074ff8,
       "Conversate magic cell address")
ASSERT(audio_conversate_last_frame_tick_2007485c == 0x2007485c,
       "Conversate frame tick address")
