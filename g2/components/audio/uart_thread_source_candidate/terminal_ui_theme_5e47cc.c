/* Stock Terminal UI theme group at 0x5e47cc. */
#include <stdint.h>

extern void audio_uart_page_44122a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44120e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44121c(uint32_t, uint32_t, uint32_t);

void audio_terminal_ui_theme_5e47cc(uint32_t object, uint32_t value,
                                     uint32_t selector) {
    audio_uart_page_44122a(object, value, selector);
    audio_uart_page_441238(object, value, selector);
    audio_uart_page_44120e(object, value, selector);
    audio_uart_page_44121c(object, value, selector);
}
