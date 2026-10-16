/* Linker fragment for the Apollo Main image. This section must be NOLOAD. */
SECTIONS {
  .opencfw.mram.records 0x007ff000 (NOLOAD) : {
    KEEP(*(.bss.opencfw.mram.records))
  }
}
INSERT AFTER .bss;
