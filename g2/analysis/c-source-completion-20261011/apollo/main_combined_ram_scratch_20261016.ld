/* Preserve all already claimed fixed RAM spans in one partial-link step. */
SECTIONS {
  .g2_print_buffer_2006b930 0x2006b930 (NOLOAD) : {
    KEEP(*(.g2_print_buffer_2006b930))
  }
  .g2_ram_2006bd30 0x2006bd30 (NOLOAD) : {
    KEEP(*(.g2_ram_2006bd30))
  }
  .g2_transaction_transport_2007397c 0x2007397c (NOLOAD) : {
    KEEP(*(.g2_transaction_transport_2007397c))
  }
  .g2_tx_packet_2007399c 0x2007399c (NOLOAD) : {
    KEEP(*(.g2_tx_packet_2007399c))
  }
  .g2_pdm_clock_pin_words 0x2007421c (NOLOAD) : {
    KEEP(*(.g2_pdm_clock_pin_words))
  }
  .g2_ram_200742f0 0x200742f0 (NOLOAD) : {
    KEEP(*(.g2_ram_200742f0))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_print_buffer_2006b930) == 1024, "stdio buffer size")
ASSERT(SIZEOF(.g2_ram_2006bd30) == 1024, "dump buffer size")
ASSERT(SIZEOF(.g2_transaction_transport_2007397c) == 30, "RX size")
ASSERT(SIZEOF(.g2_tx_packet_2007399c) == 30, "TX size")
ASSERT(SIZEOF(.g2_pdm_clock_pin_words) == 8, "PDM pin size")
ASSERT(SIZEOF(.g2_ram_200742f0) == 4, "stdio sink cell size")
ASSERT(g2_flashdb_print_buffer == 0x2006b930, "stdio buffer address")
ASSERT(g2_audio_dump_buffer == 0x2006bd30, "dump buffer address")
ASSERT(g2_audio_transaction_transport == 0x2007397c, "RX address")
ASSERT(g2_audio_tx_packet == 0x2007399c, "TX address")
ASSERT(g2_pdm_clock_pin_50 == 0x2007421c, "PDM pin 50 address")
ASSERT(g2_pdm_clock_pin_51 == 0x20074220, "PDM pin 51 address")
ASSERT(g2_flashdb_print_sink == 0x200742f0, "stdio sink address")
ASSERT(g2_flashdb_print_buffer + 1024 == g2_audio_dump_buffer,
       "stdio and dump buffers must be adjacent")
ASSERT(g2_audio_transaction_transport + 30 <= g2_audio_tx_packet,
       "RX and TX buffers must not overlap")
