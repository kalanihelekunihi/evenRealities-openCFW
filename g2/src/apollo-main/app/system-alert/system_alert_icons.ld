/* Isolated Apollo system-alert icon placement probe. Full ROM map still gated. */
SECTIONS {
  .g2.rom.system_alert_pixels_connect 0x006ba700 : {
    KEEP(*(.g2.rom.system_alert_pixels_connect))
  }
  .g2.rom.system_alert_pixels_disconnect 0x006bb6c0 : {
    KEEP(*(.g2.rom.system_alert_pixels_disconnect))
  }
  .g2.rom.system_alert_icon_connect 0x00772928 : {
    KEEP(*(.g2.rom.system_alert_icon_connect))
  }
  .g2.rom.system_alert_icon_disconnect 0x007747e4 : {
    KEEP(*(.g2.rom.system_alert_icon_disconnect))
  }
}
ASSERT(SIZEOF(.g2.rom.system_alert_pixels_connect) == 0x240, "connect pixel size")
ASSERT(SIZEOF(.g2.rom.system_alert_pixels_disconnect) == 0x240, "disconnect pixel size")
ASSERT(SIZEOF(.g2.rom.system_alert_icon_connect) == 28, "connect descriptor size")
ASSERT(SIZEOF(.g2.rom.system_alert_icon_disconnect) == 28, "disconnect descriptor size")
