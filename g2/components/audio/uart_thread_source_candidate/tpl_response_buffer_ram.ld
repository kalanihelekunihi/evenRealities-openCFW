SECTIONS {
  .opencfw.tpl.response.buffer 0x20004204 (NOLOAD) : {
    KEEP(*(.bss.opencfw.tpl.response.buffer))
  }
} INSERT AFTER .bss;
