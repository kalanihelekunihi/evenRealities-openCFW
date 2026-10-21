SECTIONS {
  .opencfw.fileheap.redirect_mutex 0x200748f4 (NOLOAD) : {
    KEEP(*(.bss.opencfw.fileheap.redirect_mutex))
  }
} INSERT AFTER .bss;
