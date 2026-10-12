#include <stdint.h>
/* Both names identify native48b010..48b12c. Canonical selected implementation
 * remains in display_font_bitmap_allocate.c; the entry ABI truncates cf. */
extern void *audio_uart_font_bitmap_allocate(void *,uint32_t,uint32_t,uint8_t,uint32_t);
void *audio_uart_lv_draw_buf_create_ex_48b010(void *handlers,uint32_t width,uint32_t height,uint32_t cf,uint32_t stride)
{
    return audio_uart_font_bitmap_allocate(handlers,width,height,(uint8_t)cf,stride);
}
