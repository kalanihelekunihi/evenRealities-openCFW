/* Apollo MAIN s200 v2.2.6.10 byte cells in the authenticated startup
 * zero range 0x20004558..0x20075047. Final absolute placement remains open. */
#include <stdint.h>

uint8_t audio_uart_pool_initialized;                    /* 0x20075031 */
volatile uint8_t audio_uart_ring_persist_initialized;  /* 0x20075032 */
volatile uint8_t audio_uart_ring_persist_has_tail;     /* 0x20075033 */
volatile uint8_t audio_uart_ring_persist_early_pending;/* 0x20075034 */
volatile uint8_t audio_uart_ring_persist_wake_blocked; /* 0x20075036 */
volatile uint8_t audio_uart_ring_persist_wake_pending; /* 0x20075037 */
