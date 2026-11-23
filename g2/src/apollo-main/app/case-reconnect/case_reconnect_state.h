#ifndef G2_CASE_RECONNECT_STATE_H
#define G2_CASE_RECONNECT_STATE_H

#include <stdint.h>

/* Stock RAM 0x20075010..12 are the first three bytes of the state block
 * also used by the codec UART and radio lifecycle code. */
extern uint8_t g2_stock_ram_20075010[7u];

#define audio_box_reconnect_suppressed_20075010 \
    (*(volatile uint8_t *)(void *)&g2_stock_ram_20075010[0])
#define audio_box_reconnect_pending_20075011 \
    (*(volatile uint8_t *)(void *)&g2_stock_ram_20075010[1])
#define audio_uart_case_status_disabled \
    (*(volatile uint8_t *)(void *)&g2_stock_ram_20075010[2])

#endif
