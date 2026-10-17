SECTIONS {
  .g2_conversate_ui_deinit_tail_200713fd 0x200713fd (NOLOAD) : {
    KEEP(*(.g2_conversate_ui_deinit_tail_200713fd))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_ui_deinit_tail_200713fd) == 0x17,
       "Conversate UI deinit tail size")
ASSERT(audio_conversate_ui_deinit_tail_200713fd == 0x200713fd,
       "Conversate UI deinit tail address")
