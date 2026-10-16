/* Apollo Main persistent OTA flag placement. Never initialize flash contents. */
SECTIONS {
  .opencfw.ota.bootloader_flag 0x007fe000 (NOLOAD) : {
    KEEP(*(.bss.opencfw.ota.bootloader_flag))
  }
}
INSERT AFTER .bss;
