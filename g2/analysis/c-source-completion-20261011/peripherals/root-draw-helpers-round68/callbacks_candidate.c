#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
/* Full48b80c..48b816: native adds seven with32-bit wrap. */
void *audio_uart_lv_draw_buf_malloc_cb_48b80c(uint32_t size,uint32_t cf)
{
    (void)cf;return audio_uart_lv_malloc(size+7u);
}
/* Full48b816..48b81e: void scratch R0 not return API. */
void audio_uart_lv_draw_buf_free_cb_48b816(void *data)
{
    audio_uart_lv_heap_free(data);
}
/* Full48b81e..48b82a: null stays null, otherwise8-byte align/wrap. */
void *audio_uart_lv_draw_buf_align_cb_48b81e(void *data,uint32_t cf)
{
    (void)cf;uint32_t ptr=(uint32_t)(uintptr_t)data;
    if(ptr!=0u) ptr=(ptr+7u)&~7u;
    return (void *)(uintptr_t)ptr;
}
/* Full48b82a..48b840: low-byte format, full child BPP return. */
uint32_t audio_uart_lv_draw_width_stride_cb_48b82a(uint32_t width,uint32_t cf)
{
    uint32_t bits=audio_uart_lv_color_bpp_440f44((uint8_t)cf);
    return (width*bits+7u)>>3;
}
