/* Native FreeType bitmap cache initializer 0x529936-0x529a8a. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *); /* 0x4d4666 */
extern uint32_t audio_uart_lv_unlock_core(void *); /* 0x4d4696 */
extern int32_t audio_uart_font_face_load_scalable(void *,uint32_t,uint32_t); /* 0x526d54 */
extern int32_t audio_uart_font_face_select_size(void *,uint32_t); /* 0x526ca8 */
extern int32_t audio_uart_font_load_glyph(void *,uint32_t,uint32_t); /* 0x525574 */
extern int32_t audio_uart_font_render_glyph(void *,uint32_t); /* 0x527228 */
extern int32_t audio_uart_font_get_glyph(void *,void **); /* 0x567ec8 */
extern void audio_uart_font_done_glyph(void *); /* 0x567f88 */
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t); /* 0x48aad8 */
extern void *audio_uart_font_bitmap_allocate(void *,uint32_t,uint32_t,uint8_t,uint32_t); /* 0x48b010 */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x454738 forwards to selected 0x439be4 copy body; return ignored */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern uint8_t audio_uart_display_lv_state[]; /* authenticated RAM 0x2006f548; +0xe8 => 0x2006f630 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
static const char function[]="freetype_image_create_cb";
static const char size_error[]="FT_Set_Pixel_Sizes error(0x%x)";
static const char load_error[]="FT_Load_Glyph error(0x%x)";
static const char render_error[]="FT_Render_Glyph error(0x%x)";
static const char get_error[]="FT_Get_Glyph error(0x%x)";
static uint32_t word(const void *p,uint32_t o) { return *(const uint32_t *)(const void *)((const uint8_t *)p+o); }
uint32_t audio_uart_font_bitmap_cache_initialize(void *entry,void *font) {
    uint8_t *f=(uint8_t *)font;
    uint8_t *context=(uint8_t *)(uintptr_t)word(f,0x34u);
    (void)audio_uart_lv_lock_core(context+0x10u);
    uint8_t *face=(uint8_t *)(uintptr_t)word(context,0x0cu);
    int32_t error=(face[8u]&1u)?audio_uart_font_face_load_scalable(face,0u,word(f,0x28u)):
                    audio_uart_font_face_select_size(face,0u);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0x92u,function,size_error,error);
        (void)audio_uart_lv_unlock_core(context+0x10u);
        return 0u;
    }
    error=audio_uart_font_load_glyph(face,word(entry,0u),0x108004u);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0x99u,function,load_error,error);
        (void)audio_uart_lv_unlock_core(context+0x10u);
        return 0u;
    }
    error=audio_uart_font_render_glyph((void *)(uintptr_t)word(face,0x54u),0u);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0xa0u,function,render_error,error);
        (void)audio_uart_lv_unlock_core(context+0x10u);
        return 0u;
    }
    void *glyph=0;
    error=audio_uart_font_get_glyph((void *)(uintptr_t)word(face,0x54u),&glyph);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0xa9u,function,get_error,error);
        (void)audio_uart_lv_unlock_core(context+0x10u);
        return 0u;
    }
    uint8_t *g=(uint8_t *)glyph;
    uint16_t rows=(uint16_t)word(g,0x1cu);
    uint16_t width=(uint16_t)word(g,0x20u);
    uint8_t format=g[0x2eu]==7u?0x10u:0x0eu;
    uint32_t pitch=word(g,0x24u);
    uint32_t stride=audio_uart_font_bitmap_stride(width,format);
    void *buffer=audio_uart_font_bitmap_allocate(audio_uart_display_lv_state+0xe8u,
                                                  width,rows,format,stride);
    *(uint32_t *)(void *)((uint8_t *)entry+8u)=(uint32_t)(uintptr_t)buffer;
    for(uint32_t row=0u;row<rows;row++) {
        uint8_t *destination=(uint8_t *)(uintptr_t)word(buffer,0x10u)+stride*row;
        const uint8_t *source_row=(const uint8_t *)(uintptr_t)word(g,0x28u)+pitch*row;
        audio_uart_checksum_copy(destination,source_row,pitch);
    }
    audio_uart_font_done_glyph(glyph);
    (void)audio_uart_lv_unlock_core(context+0x10u);
    return 1u;
}
