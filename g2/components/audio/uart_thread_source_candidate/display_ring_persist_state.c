/* Apollo MAIN s200 v2.2.6.10 runtime cells in the authenticated
 * zero-initializer range 0x20004558..0x20075047. Final absolute placement
 * remains a linker contract. */
#include <stdint.h>

volatile uint32_t audio_uart_ring_persist_wrap_count; /* 0x20074ac4 */
volatile uint32_t audio_uart_ring_persist_last_tick;  /* 0x20074ac8 */
volatile uint32_t audio_uart_ring_persist_event_object; /* 0x20074acc */
uint32_t g2_audio_log_event_handle; /* 0x20074570 */
