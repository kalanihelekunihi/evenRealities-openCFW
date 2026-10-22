/* Voice page LVGL property wrappers and four-side margin composite. */
#include <stdint.h>
extern void audio_uart_page_style_apply_44be4c(void *,uint8_t,uint32_t,
                                                uint32_t);
extern void audio_uart_page_44122a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441238(void *,uint32_t,uint32_t);
extern void audio_uart_page_44120e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44121c(void *,uint32_t,uint32_t);

void audio_terminal_ui_margins_5ebc5c(void *object,uint32_t value,
                                       uint32_t selector) {
    audio_uart_page_44122a(object,value,selector);
    audio_uart_page_441238(object,value,selector);
    audio_uart_page_44120e(object,value,selector);
    audio_uart_page_44121c(object,value,selector);
}
