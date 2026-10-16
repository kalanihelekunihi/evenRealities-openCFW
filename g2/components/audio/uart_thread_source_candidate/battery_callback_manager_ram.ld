/* Bounded callback-manager RAM reservations, without startup image bytes. */
SECTIONS {
  .opencfw.callback.charge 0x20073f78 (NOLOAD) : {
    KEEP(*(.bss.opencfw.callback.charge))
  }
  .opencfw.callback.ring_battery 0x20073f90 (NOLOAD) : {
    KEEP(*(.bss.opencfw.callback.ring_battery))
  }
}
INSERT AFTER .bss;
