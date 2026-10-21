/* Apollo LVGL page update flag at 0x44bde0..0x44bde9. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[]; /* native RAM 0x2006f548 */

void audio_uart_page_lock_44bde0(uint32_t value) {
    audio_uart_display_lv_state[0x24u] = (uint8_t)value;
}
