/* Observed scheduler state cells; no startup image bytes. */
SECTIONS {
  .opencfw.os.scheduler.running 0x20074a3c (NOLOAD) : {
    KEEP(*(.bss.opencfw.os.scheduler.running))
  }
  .opencfw.os.scheduler.suspended 0x20074a58 (NOLOAD) : {
    KEEP(*(.bss.opencfw.os.scheduler.suspended))
  }
}
INSERT AFTER .bss;
