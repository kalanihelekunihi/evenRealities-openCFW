SECTIONS {
  .opencfw.evenai.stream_display 0x20073a1c (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.stream_display))
  }
} INSERT AFTER .bss;
