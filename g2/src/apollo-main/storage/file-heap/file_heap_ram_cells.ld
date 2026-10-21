SECTIONS {
  .opencfw.fileheap.mutex 0x200748f8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.fileheap.mutex))
  }
  .opencfw.fileheap.pool 0x20074abc (NOLOAD) : {
    KEEP(*(.bss.opencfw.fileheap.pool))
  }
} INSERT AFTER .bss;
