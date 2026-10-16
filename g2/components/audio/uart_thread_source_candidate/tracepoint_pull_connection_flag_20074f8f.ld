/* Stock one-byte flag observed at 0x20074f8f; surrounding RAM remains open. */
SECTIONS {
  .opencfw.tracepoint.pull_connection_flag 0x20074f8f (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.pull_connection_flag))
  }
}
INSERT AFTER .bss;
