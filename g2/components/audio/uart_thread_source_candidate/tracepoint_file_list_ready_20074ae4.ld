/* Stock one-byte local file list ready flag; final RAM adjacency open. */
SECTIONS {
  .opencfw.tracepoint.file_list_ready 0x20074ae4 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.file_list_ready))
  }
}
INSERT AFTER .bss;
