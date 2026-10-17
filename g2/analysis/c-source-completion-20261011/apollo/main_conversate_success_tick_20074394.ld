INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_sync_info_response_471ee8.ld"
SECTIONS {
  .g2_conversate_last_success_tick_20074394 0x20074394 (NOLOAD) : {
    KEEP(*(.g2_conversate_last_success_tick_20074394))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_last_success_tick_20074394) == 4,
       "Conversate success tick size")
ASSERT(audio_conversate_last_success_tick_20074394 == 0x20074394,
       "Conversate success tick address")
