/* Bounded pending pull slots and enabled byte; final startup/layout open. */
SECTIONS {
  .opencfw.tracepoint.pull_pending 0x20074ad8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.pull_pending))
  }
  .opencfw.tracepoint.pull_enabled 0x20075038 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.pull_enabled))
  }
}
INSERT AFTER .bss;
