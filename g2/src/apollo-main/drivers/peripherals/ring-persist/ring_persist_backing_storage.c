/* Native persistence ring storage at 0x200761f4 and queue state at
 * 0x200771f4 lie beyond the authenticated startup zero range.
 * The validator at 0x48e900 preserves valid contents across startup.
 * Final linker placement must keep these arrays contiguous and uninitialized. */
#include <stdint.h>

__attribute__((section(".noinit.ring_persist"),aligned(4)))
uint8_t audio_uart_ring_persist_storage[0x1000];
__attribute__((section(".noinit.ring_persist"),aligned(4)))
uint8_t audio_uart_ring_persist_queue_state[24];

volatile uint32_t audio_uart_ring_persist_event_pending; /* 0x20074ad0 */

_Static_assert(sizeof(audio_uart_ring_persist_storage)==0x1000u,"ring capacity");
_Static_assert(sizeof(audio_uart_ring_persist_queue_state)==24u,"ring header");
