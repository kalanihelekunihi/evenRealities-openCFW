SECTIONS {
  .g2_conversate_context_200d5bd8 0x200d5bd8 (NOLOAD) : {
    KEEP(*(.g2_conversate_context_200d5bd8))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_context_200d5bd8) == 0xfac,
       "Conversate context RAM size")
ASSERT(audio_conversate_context_200d5bd8 == 0x200d5bd8,
       "Conversate context RAM address")
