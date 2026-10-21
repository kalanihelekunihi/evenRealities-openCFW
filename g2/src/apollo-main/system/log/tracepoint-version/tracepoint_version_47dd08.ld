/* Authenticated stock version string; final ROM layout remains open. */
SECTIONS {
  .opencfw.tracepoint.version 0x0078c740 : {
    KEEP(*(.rodata.opencfw.tracepoint.version))
  }
}
INSERT AFTER .rodata;
