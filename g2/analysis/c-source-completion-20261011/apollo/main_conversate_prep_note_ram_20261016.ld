SECTIONS {
  .g2_conversate_prep_note_ram_200d7630 0x200d7630 (NOLOAD) : {
    KEEP(*(.g2_conversate_prep_note_ram_200d7630))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_prep_note_ram_200d7630) == 0xb4b1,
       "Conversate prep-note RAM span size")
ASSERT(audio_conversate_prep_note_ram_200d7630 == 0x200d7630,
       "Conversate prep-note RAM span address")
