/* Native FreeType per-font cache setup 0x4b202c. */
#include <stdint.h>
extern void *audio_uart_font_glyph_cache_create(uint32_t); /* 0x5293c0 */
extern void *audio_uart_font_bitmap_cache_create(uint32_t); /* 0x5297b8 */
extern void *audio_uart_font_outline_cache_create(uint32_t); /* 0x529b38 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
static const char function[]="freetype_on_font_create";
static const char glyph_error[]="glyph cache creating failed";
static const char bitmap_error[]="draw data cache creating failed";
static const char mode_error[]="unknown render mode";
int32_t audio_uart_font_size_setup(void *font,uint32_t capacity) {
    uint8_t *descriptor=(uint8_t *)font;
    uint8_t *cache=*(uint8_t **)(void *)(descriptor+0x34u);
    void *glyph=audio_uart_font_glyph_cache_create(capacity<<1u);
    if(glyph==0) {
        audio_uart_lvgl_log(3u,source,0xf2u,function,glyph_error);
        return 0;
    }
    *(uint32_t *)(void *)(cache+0x18u)=(uint32_t)(uintptr_t)glyph;
    uint8_t mode=descriptor[0x2du];
    void *draw;
    if(mode==0u) draw=audio_uart_font_bitmap_cache_create(capacity);
    else if(mode==1u) draw=audio_uart_font_outline_cache_create(capacity);
    else {
        audio_uart_lvgl_log(3u,source,0xffu,function,mode_error);
        return 0;
    }
    if(draw==0) {
        audio_uart_lvgl_log(3u,source,0x104u,function,bitmap_error);
        return 0;
    }
    *(uint32_t *)(void *)(cache+0x1cu)=(uint32_t)(uintptr_t)draw;
    return 1;
}
