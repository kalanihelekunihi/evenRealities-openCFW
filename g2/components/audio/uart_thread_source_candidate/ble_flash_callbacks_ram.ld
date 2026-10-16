/* Contiguous native 0x3c-byte HAL callback table; no startup image bytes. */
SECTIONS {
  .opencfw.ble.flash.callbacks.head 0x20073270 (NOLOAD) : {
    KEEP(*(.bss.opencfw.ble.flash.callbacks.head))
  }
  .opencfw.ble.flash.callbacks.tail 0x20073278 (NOLOAD) : {
    KEEP(*(.bss.opencfw.ble.flash.callbacks.tail))
  }
}
INSERT AFTER .bss;
