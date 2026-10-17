INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_conversate_receive_ram_20261016.ld"
SECTIONS {
  .g2_conversate_event_names_200004f4 0x200004f4 : {
    KEEP(*(.g2_conversate_event_names_200004f4))
  }
  .g2_conversate_ui_state_names_20000540 0x20000540 : {
    KEEP(*(.g2_conversate_ui_state_names_20000540))
  }
}
INSERT AFTER .data;
SECTIONS {
  .g2_conversate_ui_state_20071368 0x20071368 (NOLOAD) : {
    KEEP(*(.g2_conversate_ui_state_20071368))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_event_names_200004f4) == 52,
       "Conversate event-name table size")
ASSERT(SIZEOF(.g2_conversate_ui_state_names_20000540) == 28,
       "Conversate UI-state name table size")
ASSERT(SIZEOF(.g2_conversate_ui_state_20071368) == 1,
       "Conversate UI-state cell size")
ASSERT(audio_conversate_event_names_200004f4 == 0x200004f4,
       "Conversate event-name table address")
ASSERT(audio_conversate_ui_state_names_20000540 == 0x20000540,
       "Conversate UI-state name table address")
ASSERT(audio_conversate_ui_state_20071368 == 0x20071368,
       "Conversate UI-state cell address")
