SECTIONS {
  .g2_conversate_reply_list_200d6b84 0x200d6b84 (NOLOAD) : {
    KEEP(*(.g2_conversate_reply_list_200d6b84))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_reply_list_200d6b84) == 0xaac,
       "Conversate reply/list RAM span size")
ASSERT(audio_conversate_reply_status_200d6b84 == 0x200d6b84,
       "Conversate reply/list RAM span address")
