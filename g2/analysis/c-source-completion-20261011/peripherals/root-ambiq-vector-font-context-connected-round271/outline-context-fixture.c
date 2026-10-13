#include <stdint.h>
extern uint8_t audio_uart_display_lv_state[];
void *audio_uart_font_outline_context(void) {
    return *(void **)(void *)(audio_uart_display_lv_state+0x1c0u);
}