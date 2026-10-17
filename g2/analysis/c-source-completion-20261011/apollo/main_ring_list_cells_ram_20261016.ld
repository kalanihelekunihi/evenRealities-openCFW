SECTIONS {
  .g2_ram_200746d4 0x200746d4 (NOLOAD) : { KEEP(*(.g2_ram_200746d4)) }
  .g2_ram_200746d8 0x200746d8 (NOLOAD) : { KEEP(*(.g2_ram_200746d8)) }
  .g2_ram_200746dc 0x200746dc (NOLOAD) : { KEEP(*(.g2_ram_200746dc)) }
  .g2_ram_200746e0 0x200746e0 (NOLOAD) : { KEEP(*(.g2_ram_200746e0)) }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_ram_200746d4) == 4, "ring primary list cell size")
ASSERT(SIZEOF(.g2_ram_200746d8) == 4, "ring secondary list cell size")
ASSERT(SIZEOF(.g2_ram_200746dc) == 4, "ring primary head cell size")
ASSERT(SIZEOF(.g2_ram_200746e0) == 4, "ring secondary head cell size")
ASSERT(audio_uart_ring_primary_list_cell == 0x200746d4, "ring primary list cell address")
ASSERT(audio_uart_ring_secondary_list_cell == 0x200746d8, "ring secondary list cell address")
ASSERT(audio_uart_ring_primary_head_cell == 0x200746dc, "ring primary head cell address")
ASSERT(audio_uart_ring_secondary_head_cell == 0x200746e0, "ring secondary head cell address")
