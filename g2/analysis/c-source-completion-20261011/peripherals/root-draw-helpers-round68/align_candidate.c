#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
/* Complete48aa54..48aa60: native R0 scratch discarded by caller. */
void audio_uart_lv_draw_memzero_48aa54(void *object,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(object,0u,size);
}
/* Complete48ab16..48ab30. Null handler returns null, not original data. */
void *audio_uart_lv_draw_align_ex_48ab16(void *handlers,void *data,uint32_t cf)
{
    volatile uint32_t *h=handlers;
    if(h[2]!=0u) {
        uint32_t callback=h[2];
        return ((void *(*)(void *,uint32_t))(uintptr_t)callback)(data,(uint8_t)cf);
    }
    return 0;
}
/* Complete48ab04..48ab16. Native default handlers root+0xc8. */
void *audio_uart_lv_draw_align_48ab04(void *data,uint32_t cf)
{
    return audio_uart_lv_draw_align_ex_48ab16(audio_uart_display_lv_root+0xc8u,data,(uint8_t)cf);
}
