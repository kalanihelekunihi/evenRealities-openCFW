/* The extended logger, WSF assert, and display fatal paths use one callback
 * cell. Preserve prior fixed spans and place the existing source-owned cell. */
INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_platform_log_error_alias_43d574.ld"
SECTIONS {
  .g2_ram_2007456c 0x2007456c (NOLOAD) : {
    KEEP(*(.g2_ram_2007456c))
  }
}
INSERT AFTER .bss;
PROVIDE(g2_extended_log_fatal_callback = audio_uart_display_fatal_handler);
ASSERT(SIZEOF(.g2_ram_2007456c) == 4, "fatal callback cell size")
ASSERT(g2_extended_log_fatal_callback == 0x2007456c,
       "extended logger fatal callback RAM address")
ASSERT(audio_ble_wsf_assert_hook == g2_extended_log_fatal_callback,
       "WSF and extended logger must share fatal callback cell")
