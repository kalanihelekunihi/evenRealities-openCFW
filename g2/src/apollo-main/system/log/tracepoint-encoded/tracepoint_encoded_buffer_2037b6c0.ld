/* Bounded Apollo Main TX RAM. Its 0x300-byte clear span ends at decode RAM. */
SECTIONS {
  .opencfw.tracepoint.encoded 0x2037b6c0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.encoded))
  }
}
INSERT AFTER .bss;
