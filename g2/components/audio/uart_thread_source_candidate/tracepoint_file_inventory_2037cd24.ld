/* Bounded native file inventory span; final startup and adjacency remain open. */
SECTIONS {
  .opencfw.tracepoint.file_inventory 0x2037cd24 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tracepoint.file_inventory))
  }
}
INSERT AFTER .bss;
