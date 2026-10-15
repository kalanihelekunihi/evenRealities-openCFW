/* Include in final Apollo linker script, with workspace placed in the
 * external RAM region initialized before _xip_font_configure runs. */
SECTIONS {
  .noinit.ring_config_workspace (NOLOAD) : {
    KEEP(*(.noinit.ring_config_workspace))
  }
}
INSERT AFTER .bss;
