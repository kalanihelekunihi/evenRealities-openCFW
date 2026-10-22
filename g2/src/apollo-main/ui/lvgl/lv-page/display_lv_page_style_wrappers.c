/* Native LV style setters and page manager composite 0x44120e..0x4413b0,
 * 0x44146a and 0x45ec7c. Return R7 is unused by authenticated callers. */
#include <stdint.h>
extern void audio_uart_page_style_apply_44be4c(void *,uint8_t,uint32_t,uint32_t);
#define SETTER(name,index) \
void name(void *object,uint32_t value,uint32_t selector) { \
    audio_uart_page_style_apply_44be4c(object,index,value,selector); \
}
SETTER(audio_uart_page_44120e,0x10u)
SETTER(audio_uart_page_44121c,0x11u)
SETTER(audio_uart_page_44122a,0x12u)
SETTER(audio_uart_page_441238,0x13u)
SETTER(audio_uart_page_44131c,0x30u)
SETTER(audio_uart_page_44133a,0x38u)
SETTER(audio_uart_page_441378,0x3bu)
SETTER(audio_uart_page_441386,0x3cu)
SETTER(audio_uart_page_441394,0x40u)
SETTER(audio_uart_page_4413a2,0x41u)
SETTER(audio_uart_page_4413b0,0x42u)
SETTER(audio_uart_page_44146a,0x0cu)
void audio_uart_page_45ec7c(void *object,uint32_t value,uint32_t selector) {
    audio_uart_page_44122a(object,value,selector);
    audio_uart_page_441238(object,value,selector);
    audio_uart_page_44120e(object,value,selector);
    audio_uart_page_44121c(object,value,selector);
}
