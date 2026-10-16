/* Apollo LVGL page context lookup 0x44d33a..0x44d341. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[]; /* native RAM 0x2006f548 */

void *audio_uart_page_context_44d33a(void) {
    return *(void **)(void *)(audio_uart_display_lv_state + 0x40u);
}
