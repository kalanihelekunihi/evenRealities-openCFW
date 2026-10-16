/* Native page style wrapper 0x44143e..0x44144b: property 0x5a. */
#include <stdint.h>

extern void audio_uart_page_style_apply_44be4c(void *,uint8_t,uint32_t,uint32_t);

void audio_uart_page_44143e(void *object,uint32_t value,uint32_t selector)
{
    audio_uart_page_style_apply_44be4c(object,0x5au,value,selector);
}
