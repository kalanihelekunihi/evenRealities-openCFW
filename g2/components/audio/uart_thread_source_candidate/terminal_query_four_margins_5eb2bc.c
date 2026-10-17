/* Query four-side spacing wrapper, stock 0x5eb2bc..0x5eb2ed. */
#include <stdint.h>
extern void audio_uart_page_44122a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441238(void *,uint32_t,uint32_t);
extern void audio_uart_page_44120e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44121c(void *,uint32_t,uint32_t);

void audio_terminal_query_four_margins_5eb2bc(void *object,uint32_t value,
                                              uint32_t selector) {
    audio_uart_page_44122a(object,value,selector);
    audio_uart_page_441238(object,value,selector);
    audio_uart_page_44120e(object,value,selector);
    audio_uart_page_44121c(object,value,selector);
}
