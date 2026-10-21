/* Bounded Apollo Main tracepoint reply RAM. No startup image bytes. */
SECTIONS {
  .opencfw.tracepoint.reply 0x2037bbc8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.reply))
  }
}
INSERT AFTER .bss;
