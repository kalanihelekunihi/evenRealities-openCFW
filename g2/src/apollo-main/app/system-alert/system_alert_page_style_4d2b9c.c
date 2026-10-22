/* Native call target 0x4d2b9c, inside decompiler envelope 0x4d2b9a. */
#include <stdint.h>
extern void audio_uart_page_44122a(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_441238(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44120e(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44121c(uint32_t,uint32_t,uint32_t);

/* Stock 0x4D2B9A (system-alert page style; TSV row starts at the 2-byte pad before 0x4d2b9c) */
void audio_system_alert_page_style_4d2b9c(uint32_t object,uint32_t value,
                                           uint32_t selector) {
    audio_uart_page_44122a(object,value,selector);
    audio_uart_page_441238(object,value,selector);
    audio_uart_page_44120e(object,value,selector);
    audio_uart_page_44121c(object,value,selector);
}
