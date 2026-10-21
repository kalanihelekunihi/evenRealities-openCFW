/* Apollo MAIN s200 v2.2.6.10 contiguous Nema pointer/capability cells.
 * Initial contents are zeroed by the authenticated startup callback.
 * Absolute placement remains a linker contract. */
#include <stdint.h>

volatile uint32_t audio_uart_nema_context_cell[1]; /* 0x20074efc */
volatile uint32_t audio_uart_nema_capabilities; /* 0x20074f00 */
volatile uint32_t audio_uart_nema_vg_context_cell; /* 0x20074f04 */
