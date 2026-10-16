/* Bounded backend-ready byte and failure counter; final RAM layout open. */
SECTIONS {
  .opencfw.tracepoint.pull_failure_count 0x20074ac0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.pull_failure_count))
  }
  .opencfw.tracepoint.pull_backend_ready 0x20075035 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.pull_backend_ready))
  }
}
INSERT AFTER .bss;
