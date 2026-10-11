/* Native LVGL FreeType bitmap/outline draw descriptor cleanup callbacks
 * 0x5298f8 and 0x529e04. */
#include <stdint.h>
extern void audio_uart_font_cache_remove(void *,void *,uint32_t); /* 0x4d4e72 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
static const char bitmap_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_image.c";
static const char outline_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_outline.c";
static const char null_reason[]="NULL pointer";
static const char font_nonnull[]="font != NULL";
static const char assert_two[]="Asserted at expression: %s (%s)";
static const char bitmap_function[]="freetype_image_release_cb";
static const char outline_function[]="freetype_release_glyph_cb";
static void bad_font(const char *source,uint32_t line,const char *function) {
    audio_uart_lvgl_log(3u,source,line,function,assert_two,font_nonnull,null_reason);
    for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
}
void audio_uart_font_cb_bitmap_draw(void *font,void *draw_descriptor) {
    if(font==0) bad_font(bitmap_source,0x76u,bitmap_function);
    void *descriptor=(void *)(uintptr_t)word(font,0x18u);
    void *context=(void *)(uintptr_t)word(descriptor,0x34u);
    void *cache=(void *)(uintptr_t)word(context,0x1cu);
    audio_uart_font_cache_remove(cache,(void *)(uintptr_t)word(draw_descriptor,0x1cu),0u);
    store(draw_descriptor,0x1cu,0u);
}
void audio_uart_font_cb_outline_draw(void *font,void *draw_descriptor) {
    if(font==0) bad_font(outline_source,0xbdu,outline_function);
    void *descriptor=(void *)(uintptr_t)word(font,0x18u);
    void *node=(void *)(uintptr_t)word(draw_descriptor,0x1cu);
    if(node!=0) {
        void *context=(void *)(uintptr_t)word(descriptor,0x34u);
        void *cache=(void *)(uintptr_t)word(context,0x1cu);
        audio_uart_font_cache_remove(cache,node,0u);
        store(draw_descriptor,0x1cu,0u);
    }
}
