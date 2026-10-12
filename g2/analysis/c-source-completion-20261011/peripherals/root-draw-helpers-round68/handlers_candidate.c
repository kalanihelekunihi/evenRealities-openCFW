/* Full48aaa2..48aad8 and48aa80..48aaa2. Unselected pending comparisons.
 * Native48aa80 is handlers initialization, not memory-pool initialization. */
#include <stdint.h>
extern void audio_uart_lv_draw_memzero_48aa54(void *,uint32_t);
/* Address-only callback declarations; invocation ABIs require body evidence. */
extern void audio_uart_lv_draw_buf_malloc_cb_48b80c(void);
extern void audio_uart_lv_draw_buf_free_cb_48b816(void);
extern void audio_uart_lv_draw_buf_align_cb_48b81e(void);
extern void audio_uart_lv_draw_width_stride_cb_48b82a(void);
void audio_uart_lv_draw_handlers_init_48aaa2(void *object,uint32_t allocate,uint32_t release,uint32_t align,uint32_t invalidate,uint32_t flush,uint32_t stride)
{
    audio_uart_lv_draw_memzero_48aa54(object,32u);
    volatile uint32_t *h=object;
    h[0]=allocate;h[1]=release;h[2]=align;h[3]=invalidate;h[4]=flush;h[5]=stride;
}
void audio_uart_lv_draw_handlers_default_48aa80(void *object)
{
    audio_uart_lv_draw_handlers_init_48aaa2(object,
        (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_malloc_cb_48b80c,
        (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_free_cb_48b816,
        (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_align_cb_48b81e,
        0u,0u,(uint32_t)(uintptr_t)audio_uart_lv_draw_width_stride_cb_48b82a);
}
