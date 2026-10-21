/* Native lv_freetype_set_cbs_glyph/image/outline 0x529406/0x5297f8/0x529b7e.
 * Callback functions are separate genuine code lowers at the addresses below. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern uint32_t audio_uart_font_cb_glyph(void *,void *,uint32_t,uint32_t); /* 0x529460 */
extern void *audio_uart_font_cb_bitmap_glyph(void *);/* 0x529858 */
extern void audio_uart_font_cb_bitmap_draw(void); /* 0x5298f8 */
extern void *audio_uart_font_cb_outline_glyph(void *);/* 0x529d70 */
extern void audio_uart_font_cb_outline_draw(void); /* 0x529e04 */
static const char glyph_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_glyph.c";
static const char bitmap_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_image.c";
static const char outline_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_outline.c";
static const char glyph_function[]="lv_freetype_set_cbs_glyph";
static const char bitmap_function[]="lv_freetype_set_cbs_image_font";
static const char outline_function[]="lv_freetype_set_cbs_outline_font";
static const char null_reason[]="NULL pointer";
static const char nonnull[]="dsc != NULL";
static const char magic_expr[]="LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(dsc)";
static const char assert_two[]="Asserted at expression: %s (%s)";
static const char assert_invalid[]="Asserted at expression: %s Invalid font descriptor: 0x%x";
static void callback_assert(const char *source,uint32_t line,const char *function,
                            const char *expr,uint32_t bad_magic,uint32_t is_null) {
    if(is_null!=0u) audio_uart_lvgl_log(3u,source,line,function,assert_two,expr,null_reason);
    else audio_uart_lvgl_log(3u,source,line,function,assert_invalid,expr,bad_magic);
    for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u; /* native faulting store */
}
static uint8_t *validate(void *descriptor,const char *source,const char *function,
                         uint32_t line) {
    if(descriptor==0)
        callback_assert(source,line,function,nonnull,0u,1u);
    uint32_t magic=*(const uint32_t *)descriptor;
    if(magic!=0x5f5f4654u)
        callback_assert(source,line,function,magic_expr,magic,0u);
    return (uint8_t *)descriptor;
}
void audio_uart_font_callbacks_common(void *descriptor) { /* 0x529406 */
    uint8_t *p=validate(descriptor,glyph_source,glyph_function,0x47u);
    *(uint32_t *)(void *)(p+4u)=(uint32_t)(uintptr_t)&audio_uart_font_cb_glyph;
}
void audio_uart_font_callbacks_bitmap(void *descriptor) { /* 0x5297f8 */
    uint8_t *p=validate(descriptor,bitmap_source,bitmap_function,0x4cu);
    *(uint32_t *)(void *)(p+8u)=(uint32_t)(uintptr_t)&audio_uart_font_cb_bitmap_glyph;
    *(uint32_t *)(void *)(p+12u)=(uint32_t)(uintptr_t)&audio_uart_font_cb_bitmap_draw;
}
void audio_uart_font_callbacks_outline(void *descriptor) { /* 0x529b7e */
    uint8_t *p=validate(descriptor,outline_source,outline_function,0x4fu);
    *(uint32_t *)(void *)(p+8u)=(uint32_t)(uintptr_t)&audio_uart_font_cb_outline_glyph;
    *(uint32_t *)(void *)(p+12u)=(uint32_t)(uintptr_t)&audio_uart_font_cb_outline_draw;
}
