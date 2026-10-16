SECTIONS {
  .bss.opencfw.terminal.ui_timer 0x20073c38 (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.ui_timer))
  }
}
INSERT AFTER .bss;
