SECTIONS {
  .opencfw.evenai.notify.sequence 0x20074ff9 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.notify.sequence))
  }
} INSERT AFTER .bss;
