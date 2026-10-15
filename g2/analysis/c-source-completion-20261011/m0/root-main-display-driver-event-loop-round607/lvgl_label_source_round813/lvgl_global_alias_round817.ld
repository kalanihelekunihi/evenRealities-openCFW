/* Trial alias for the authenticated Apollo LVGL state at RAM 0x2006f548.
 * A final memory map must reserve the complete 0x1ec-byte region. */
PROVIDE(audio_uart_display_lv_root = 0x2006f548);
PROVIDE(lv_global = 0x2006f548);
