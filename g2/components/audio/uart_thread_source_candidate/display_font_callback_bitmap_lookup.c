/* Native LVGL FreeType bitmap glyph callback 0x529858. */
#include <stdint.h>
extern void *audio_uart_font_cache_add(void *,const void *,uint32_t); /* 0x4d4f90 */
extern void *audio_uart_font_cache_info(void *); /* 0x4d5396 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_image.c";
static const char function[]="freetype_get_glyph_bitmap_cb";
static const char assertion[]="Asserted at expression: %s (%s)";
static const char invalid_assertion[]="Asserted at expression: %s Invalid font descriptor: 0x%x";
static const char null_pointer[]="NULL pointer";
static const char descriptor_nonnull[]="dsc != NULL";
static const char valid_magic[]="LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(dsc)";
static const char lookup_error[]="glyph bitmap lookup failed for glyph_index = 0x%x";
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void fatal(void) {
    for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
}
void *audio_uart_font_cb_bitmap_glyph(void *font) {
    uint8_t *descriptor=(uint8_t *)(uintptr_t)w(font,0u);
    uint8_t *dsc=(uint8_t *)(uintptr_t)w(descriptor,0x18u);
    if(dsc==0) {
        audio_uart_lvgl_log(3u,source,0x5bu,function,assertion,descriptor_nonnull,null_pointer);
        fatal();
    }
    if(w(dsc,0u)!=0x5f5f4654u) {
        audio_uart_lvgl_log(3u,source,0x5bu,function,invalid_assertion,
                            valid_magic,w(dsc,0u));
        fatal();
    }
    uint32_t index=w(font,0x18u);
    uint8_t *context=(uint8_t *)(uintptr_t)w(dsc,0x34u);
    void *cache=(void *)(uintptr_t)w(context,0x1cu);
    uint32_t key[3]={index,w(dsc,0x28u),0u};
    void *entry=audio_uart_font_cache_add(cache,key,(uint32_t)(uintptr_t)dsc);
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x68u,function,lookup_error,index);
        return 0;
    }
    *(uint32_t *)(void *)((uint8_t *)font+0x1cu)=(uint32_t)(uintptr_t)entry;
    uint8_t *data=(uint8_t *)audio_uart_font_cache_info(entry);
    return (void *)(uintptr_t)w(data,8u);
}
