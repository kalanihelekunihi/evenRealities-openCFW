/* Isolated stock placement proof; include only after full RAM-map review. */
SECTIONS {
  .bss.opencfw.registry.ring_connect_buffer 0x2010f4cc (NOLOAD) : {
    KEEP(*(.bss.opencfw.registry.ring_connect_buffer))
  }
  .bss.opencfw.registry.ring_connect_state 0x2010fd1c (NOLOAD) : {
    KEEP(*(.bss.opencfw.registry.ring_connect_state))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.bss.opencfw.registry.ring_connect_buffer) == 0x850,
       "ring-connect buffer interval")
ASSERT(SIZEOF(.bss.opencfw.registry.ring_connect_state) == 1,
       "ring-connect state size")
