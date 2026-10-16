/* Apollo Main active input object, native 0x452ffa..0x453001.
 * Literal at 0x453058 points to the existing LVGL state at 0x2006f548. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];

void *audio_uart_lv_input_active_452ffa(void) {
    return (void *)(uintptr_t)*(uint32_t *)(void *)(audio_uart_display_lv_state + 0x54u);
}
