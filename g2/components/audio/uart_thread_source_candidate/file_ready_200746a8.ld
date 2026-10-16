/* Bounded stock file facade readiness cell, without an inferred initializer. */
SECTIONS {
  .opencfw.file.ready 0x200746a8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.file.ready))
  }
}
INSERT AFTER .bss;
