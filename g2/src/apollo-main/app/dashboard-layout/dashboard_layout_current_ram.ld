/* Bounded dashboard layout RAM destination; no startup image bytes. */
SECTIONS {
  .opencfw.dashboard.layout.current 0x200e7934 (NOLOAD) : {
    KEEP(*(.bss.opencfw.dashboard.layout.current))
  }
}
INSERT AFTER .bss;
