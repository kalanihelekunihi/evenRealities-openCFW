SECTIONS {
  .opencfw.terminal.event_names 0x20003e6c (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.event_names))
  }
}
INSERT AFTER .bss;
