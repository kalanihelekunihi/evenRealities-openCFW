/* Stock shared directory entry name/type buffer, bounded 0x101 bytes. */
SECTIONS {
  .opencfw.tracepoint.dir_result 0x200701e8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.dir_result))
  }
}
INSERT AFTER .bss;
