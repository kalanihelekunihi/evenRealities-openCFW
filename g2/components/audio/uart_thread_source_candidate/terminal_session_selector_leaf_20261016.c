/* Apollo session selector leaf helpers, stock 0x5eca00 and 0x5ecc74. */
#include <stdint.h>

extern void audio_uart_page_44122a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441238(void *,uint32_t,uint32_t);
extern void audio_uart_page_44120e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44121c(void *,uint32_t,uint32_t);
extern int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...);

void audio_terminal_session_four_margins_5eca00(void *object,uint32_t value,
                                                uint32_t selector) {
    audio_uart_page_44122a(object,value,selector);
    audio_uart_page_441238(object,value,selector);
    audio_uart_page_44120e(object,value,selector);
    audio_uart_page_44121c(object,value,selector);
}

void audio_terminal_session_row_text_5ecc74(char *destination,uint32_t capacity,
                                            const uint8_t *source) {
    if (destination==0 || capacity==0u) return;
    destination[0]=0;
    if (source==0) return;
    uint32_t length=(uint32_t)source[4]|((uint32_t)source[5]<<8);
    if (length>=capacity) length=capacity-1u;
    for (uint32_t i=0;i<length;++i) destination[i]=(char)source[6u+i];
    destination[length]=0;
    if (length==0u) {
        uint32_t id=(uint32_t)source[0]|((uint32_t)source[1]<<8)|
                    ((uint32_t)source[2]<<16)|((uint32_t)source[3]<<24);
        (void)g2_audio_dump_snprintf(destination,capacity,"Session %lu",id);
    }
}
