SECTIONS {
  .opencfw.tpl.timeout.ids 0x20074b04 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tpl.timeout.ids))
  }
} INSERT AFTER .bss;
