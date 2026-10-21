/* Isolated placement proof; include only after checking the full RAM map. */
SECTIONS {
  .bss.opencfw.audio.codec_check_timer 0x20074a98 (NOLOAD) : {
    KEEP(*(.bss.opencfw.audio.codec_check_timer))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.bss.opencfw.audio.codec_check_timer) == 4,
       "codec watchdog timer handle size")
