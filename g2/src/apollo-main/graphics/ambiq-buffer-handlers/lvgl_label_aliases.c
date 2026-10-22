/* Selected LVGL provider names for the pinned upstream label translation unit. */
#include <stdint.h>

extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,
                                                     const int32_t *);
extern int32_t audio_uart_lv_area_width_451598(const int32_t *);
extern void audio_uart_ambiq_area_move_450bb2(int32_t *,int32_t,int32_t);
extern void *audio_uart_lv_draw_buf_reshape_48b196(void *,uint32_t,uint32_t,
                                                    uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_glyph_bitmap_4d5612(uint32_t,uint32_t);

uint32_t lv_area_intersect(int32_t *out,const int32_t *a,const int32_t *b) {
    return audio_uart_lv_area_intersect_450bcc(out,a,b);
}
int32_t lv_area_get_width(const int32_t *area) {
    return audio_uart_lv_area_width_451598(area);
}
void lv_area_move(int32_t *area,int32_t dx,int32_t dy) {
    audio_uart_ambiq_area_move_450bb2(area,dx,dy);
}
const void *lv_font_get_glyph_bitmap(void *glyph,void *draw_buf) {
    return (const void *)(uintptr_t)audio_uart_ambiq_glyph_bitmap_4d5612(
        (uint32_t)(uintptr_t)glyph,(uint32_t)(uintptr_t)draw_buf);
}
