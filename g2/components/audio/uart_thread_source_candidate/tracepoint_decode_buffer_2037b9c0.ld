/* Bounded Apollo Main tracepoint RAM reservation. No startup image bytes. */
SECTIONS {
  .opencfw.tracepoint.decode 0x2037b9c0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.decode))
  }
}
INSERT AFTER .bss;
