/* The FlashDB print wrapper and board callback read the same stock RAM cell.
 * The callback source already owns its four-byte storage. */
SECTIONS {}
PROVIDE(g2_flashdb_print_sink = audio_uart_stdio_print_char_cell_200742f0);
ASSERT(g2_flashdb_print_sink == audio_uart_stdio_print_char_cell_200742f0,
       "FlashDB print sink must share the board callback cell");
