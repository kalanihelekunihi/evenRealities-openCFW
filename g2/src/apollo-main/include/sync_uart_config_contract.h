#ifndef G2_SYNC_UART_CONFIG_CONTRACT_H
#define G2_SYNC_UART_CONFIG_CONTRACT_H

#include <stddef.h>
#include <stdint.h>

/* Observed reads by stock UART configure body 0x58e09e. This describes
 * the accessed prefix only. It does not establish the object extent,
 * initialization bytes, or its required RAM placement at 0x20000d9c. */
typedef struct {
    uint32_t requested_baud;       /* +0 */
    uint8_t line_mode;             /* +4, low two bits */
    uint8_t framing;               /* +5 */
    uint8_t parity;                /* +6, low bit */
    uint8_t reserved_7;
    uint16_t control_bits;         /* +8 */
    uint8_t tx_fifo_level;         /* +10, low three bits */
    uint8_t rx_fifo_level;         /* +11, low three bits */
    uint8_t clock_mode;            /* +12 */
} g2_sync_uart_config_prefix_t;

_Static_assert(offsetof(g2_sync_uart_config_prefix_t, requested_baud) == 0, "baud offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, line_mode) == 4, "line mode offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, framing) == 5, "framing offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, parity) == 6, "parity offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, control_bits) == 8, "control offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, tx_fifo_level) == 10, "TX threshold offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, rx_fifo_level) == 11, "RX threshold offset");
_Static_assert(offsetof(g2_sync_uart_config_prefix_t, clock_mode) == 12, "clock offset");

#endif
