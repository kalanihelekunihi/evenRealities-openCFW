/* Stock Terminal session-list row style at 0x5ecb08. */
#include <stdint.h>

extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_4412ec(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44130c(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_session_row_show_5897ee(uint32_t);
extern void audio_terminal_session_row_hide_589892(uint32_t);

void audio_terminal_session_row_style_5ecb08(uint32_t object,
                                              uint32_t selected) {
    if (object == 0u)
        return;
    const uint32_t color = audio_uart_page_44104c(0x00ffffffu);
    audio_uart_page_4412ec(object, color, 0u);
    audio_uart_page_44130c(object, (uint8_t)selected != 0u ? 0xffu : 0u, 0u);
    if ((uint8_t)selected != 0u)
        audio_terminal_session_row_show_5897ee(object);
    else
        audio_terminal_session_row_hide_589892(object);
}
