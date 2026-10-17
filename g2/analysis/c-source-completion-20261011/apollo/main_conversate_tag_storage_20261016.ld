SECTIONS {
  .g2_conversate_tag_storage_200e3af4 0x200e3af4 (NOLOAD) : {
    KEEP(*(.g2_conversate_tag_storage_200e3af4))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_tag_storage_200e3af4) == 12,
       "Conversate tag-storage state size")
ASSERT(audio_conversate_tag_storage_state_200e3af4 == 0x200e3af4,
       "Conversate tag-storage state address")
