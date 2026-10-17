INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_conversate_success_tick_20074394.ld"
SECTIONS {
  .g2_conversate_action_mutex_20074398 0x20074398 (NOLOAD) : {
    KEEP(*(.g2_conversate_action_mutex_20074398))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_action_mutex_20074398) == 4,
       "Conversate mutex handle size")
ASSERT(audio_conversate_action_mutex_20074398 == 0x20074398,
       "Conversate mutex handle address")
