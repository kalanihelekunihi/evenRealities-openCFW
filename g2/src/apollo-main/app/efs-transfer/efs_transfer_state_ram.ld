/* Bounded EFS state RAM span, without startup image bytes. */
SECTIONS {
  .opencfw.efs.transfer 0x20071cc8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.efs.transfer))
  }
}
INSERT AFTER .bss;
