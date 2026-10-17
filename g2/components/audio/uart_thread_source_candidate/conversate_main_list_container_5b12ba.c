/* Apollo Main Conversate main-page list container, 0x5b12ba..0x5b133b. */
#include <stdint.h>

extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_48ba78(uint32_t, uint32_t);
extern void audio_uart_page_48ba92(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441246(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_ui_style_5b0ac4(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441386(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44e368(uint32_t, uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);

uint32_t audio_conversate_ui_main_list_container_5b12ba(uint32_t parent) {
    const uint32_t list = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(list, 0x240u, 0xa0u);
    audio_uart_page_48ba78(list, 1u);
    audio_uart_page_48ba92(list, 0u, 0u, 0u);
    audio_uart_page_441246(list, 0u, 0u);
    audio_conversate_ui_style_5b0ac4(list, 0u, 0u);
    audio_uart_page_44129e(list, 0u, 0u);
    audio_uart_page_44131c(list, 0u, 0u);
    audio_uart_page_44146a(list, 0u, 0u);
    audio_uart_page_441386(list, 0u, 0u);
    audio_uart_page_44e368(list, 0u);
    audio_uart_page_43ded4(list, 0x10u);
    audio_uart_page_43dfa4(list, 0x360u);
    return list;
}
