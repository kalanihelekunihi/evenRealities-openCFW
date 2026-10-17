SECTIONS {
  .g2_conversate_timer_mgr_ram_20073a3c 0x20073a3c (NOLOAD) : {
    KEEP(*(.g2_conversate_timer_mgr_ram_20073a3c))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_timer_mgr_ram_20073a3c) == 0x1c,
       "Conversate timer-manager RAM size")
ASSERT(audio_conversate_timer_mgr_ram_20073a3c == 0x20073a3c,
       "Conversate timer-manager RAM address")
