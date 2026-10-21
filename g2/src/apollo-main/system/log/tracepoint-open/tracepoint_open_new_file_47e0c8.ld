/* Stock Main sequence/generation words; final whole-image RAM placement open. */
SECTIONS {
  .opencfw.tracepoint.next_sequence 0x20004188 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.next_sequence))
  }
  .opencfw.tracepoint.session_generation 0x20074ad4 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.session_generation))
  }
}
INSERT AFTER .bss;
