/* Place only the bounded receive scratch span at its stock Main RAM base. */
SECTIONS {
  .g2_transaction_transport_2007397c 0x2007397c (NOLOAD) : {
    KEEP(*(.g2_transaction_transport_2007397c))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_transaction_transport_2007397c) == 30,
       "GX8002 receive scratch requires 30 bytes")
ASSERT(g2_audio_transaction_transport == 0x2007397c,
       "GX8002 receive scratch RAM address")
ASSERT(g2_audio_transaction_transport + 30 <= 0x2007399c,
       "GX8002 receive scratch must not reach TX packet base")
