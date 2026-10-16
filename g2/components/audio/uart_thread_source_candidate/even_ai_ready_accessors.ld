SECTIONS {
  .opencfw.evenai.pending.empty 0x00552cf4 : {
    KEEP(*(.rodata.opencfw.evenai.pending.empty))
  }
} INSERT AFTER .rodata;
