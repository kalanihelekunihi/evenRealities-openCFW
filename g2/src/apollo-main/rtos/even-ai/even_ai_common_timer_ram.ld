SECTIONS {
  .opencfw.evenai.common.timer 0x20074008 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.common.timer))
  }
} INSERT AFTER .bss;
