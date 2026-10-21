/* Bounded nominal TX packet span at its stock Main RAM address. */
SECTIONS {
  .g2_transaction_transport_2007397c 0x2007397c (NOLOAD) : {
    KEEP(*(.g2_transaction_transport_2007397c))
  }
  .g2_tx_packet_2007399c 0x2007399c (NOLOAD) : {
    KEEP(*(.g2_tx_packet_2007399c))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_transaction_transport_2007397c) == 30,
       "GX8002 RX scratch requires 30 bytes")
ASSERT(g2_audio_transaction_transport == 0x2007397c,
       "GX8002 RX scratch RAM address")
ASSERT(SIZEOF(.g2_tx_packet_2007399c) == 30,
       "GX8002 TX packet requires 30 nominal bytes")
ASSERT(g2_audio_tx_packet == 0x2007399c,
       "GX8002 TX packet RAM address")
ASSERT(g2_audio_tx_packet + 30 <= 0x20073a1c,
       "GX8002 TX packet must not reach stream state base")
