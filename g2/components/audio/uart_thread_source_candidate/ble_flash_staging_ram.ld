/* Bounded BLE bond erase staging RAM, without startup image bytes. */
SECTIONS {
  .opencfw.ble.flash.staging 0x200636a0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.ble.flash.staging))
  }
}
INSERT AFTER .bss;
