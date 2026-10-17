SECTIONS {
  .g2_conversate_transcribe_length_2007439c 0x2007439c (NOLOAD) : {
    KEEP(*(.g2_conversate_transcribe_length_2007439c))
  }
  .g2_conversate_transcribe_flag_20074fa2 0x20074fa2 (NOLOAD) : {
    KEEP(*(.g2_conversate_transcribe_flag_20074fa2))
  }
  .g2_conversate_transcribe_output_200e2ae4 0x200e2ae4 (NOLOAD) : {
    KEEP(*(.g2_conversate_transcribe_output_200e2ae4))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_transcribe_length_2007439c) == 4,
       "Conversate transcribe length size")
ASSERT(SIZEOF(.g2_conversate_transcribe_flag_20074fa2) == 1,
       "Conversate transcribe flag size")
ASSERT(SIZEOF(.g2_conversate_transcribe_output_200e2ae4) == 0x1008,
       "Conversate transcribe output size")
ASSERT(audio_conversate_transcribe_length_2007439c == 0x2007439c,
       "Conversate transcribe length address")
ASSERT(audio_conversate_transcribe_flag_20074fa2 == 0x20074fa2,
       "Conversate transcribe flag address")
ASSERT(audio_conversate_transcribe_output_200e2ae4 == 0x200e2ae4,
       "Conversate transcribe output address")
