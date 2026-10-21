/* Bounded four-byte stock active-file pointer slot; no startup initializer. */
SECTIONS {
  .opencfw.tracepoint.active_file 0x20074ae0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.active_file))
  }
}
INSERT AFTER .bss;
