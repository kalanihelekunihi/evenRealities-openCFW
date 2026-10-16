/* Apollo display ID membership predicate at 0x4434d0..0x4434e7. */
#include <stdint.h>

extern uint32_t audio_uart_display_active;     /* native RAM 0x200744d8 */
extern uint32_t audio_uart_display_background; /* native RAM 0x200744e0 */

uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t id) {
    return id == audio_uart_display_active || id == audio_uart_display_background;
}
