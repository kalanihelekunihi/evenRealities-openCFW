/* Native LVGL style-flag scan 0x44ce2c and style reset 0x482796. */
#include <stdint.h>
extern uint32_t audio_uart_page_style_needs_invalidate_44b844(uint32_t,uint32_t);
extern void audio_uart_lv_heap_free(void *); /* selected native 0x44f758 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
uint32_t audio_uart_lv_style_has_flag_44ce2c(void *style,uint32_t mask) {
    uint8_t *s=(uint8_t *)style;
    uint8_t *values=*(uint8_t **)(void *)s;
    if(s[8u]!=0xffu) {
        uint32_t count=s[8u];
        for(uint32_t i=0;i<count;i++)
            if(audio_uart_page_style_needs_invalidate_44b844(values[count*4u+i],mask)!=0u)
                return 1u;
    }
    else {
        for(uint32_t i=0;values[i*8u]!=0u;i++)
            if(audio_uart_page_style_needs_invalidate_44b844(values[i*8u],mask)!=0u)
                return 1u;
    }
    return 0u;
}
void audio_uart_lv_style_reset_482796(void *style) {
    uint8_t *s=(uint8_t *)style;
    if(s[8u]!=0xffu)audio_uart_lv_heap_free(*(void **)(void *)s);
    audio_uart_buffer_zero(s,12u,0u);
}
