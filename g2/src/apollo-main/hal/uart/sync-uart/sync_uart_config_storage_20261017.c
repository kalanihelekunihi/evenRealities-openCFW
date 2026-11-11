/* UART0 (inter-temple TinyFrame link) configuration, stock RAM 0x20000d9c.
 * Evidence (Fix 54): stk12 under Renode, ReadDoubleWord 0x20000d9c.. at 3 s
 * = 0x000E1000 0x00000203 0x02020000 0x00000000 (0 at t=0, i.e. .data copy).
 * Same word shape as the UART1-3 configs in board_data.c. The zero BSS copy
 * configured UART0 as baud 0 / 5-bit words and broke the peer-arm pipe.
 * Extent beyond 16 bytes is still unproven. */
#include "sync_uart_config_contract.h"
g2_sync_uart_config_prefix_t g2_uart_sync_buffer = {
    .requested_baud = 921600u,        /* 0x000E1000 */
    .line_mode = 0x03u, .framing = 0x02u, /* word 0x00000203 */
    .parity = 0u, .reserved_7 = 0u,
    .control_bits = 0x0000u, .tx_fifo_level = 0x02u, .rx_fifo_level = 0x02u, /* 0x02020000 */
    .clock_mode = 0u,
};
_Static_assert(sizeof(g2_sync_uart_config_prefix_t) == 16, "4 stock words");
