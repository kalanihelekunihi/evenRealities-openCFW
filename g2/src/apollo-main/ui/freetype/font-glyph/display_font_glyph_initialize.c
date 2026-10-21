/* Native FreeType glyph cache initializer 0x5295a8-0x529726. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *); /* 0x4d4666 */
extern uint32_t audio_uart_lv_unlock_core(void *); /* 0x4d4696 */
extern uint32_t audio_uart_font_get_char_index(void *,uint32_t); /* 0x526f10 */
extern int32_t audio_uart_font_face_load_scalable(void *,uint32_t,uint32_t); /* 0x526d54 */
extern int32_t audio_uart_font_face_select_size(void *,uint32_t); /* 0x526ca8 */
extern int32_t audio_uart_font_load_glyph(void *,uint32_t,uint32_t); /* 0x525574 */
extern int16_t audio_uart_font_italic_shift(uint16_t,uint16_t); /* 0x4b201e */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
static const char function[]="freetype_glyph_create_cb";
static const char size_error[]="FT_Set_Pixel_Sizes error(0x%x)";
static const char load_error[]="FT_Load_Glyph error(0x%x)";
static uint32_t word(const void *p,uint32_t o) { return *(const uint32_t *)(const void *)((const uint8_t *)p+o); }
static int32_t signed_word(const void *p,uint32_t o) { return *(const int32_t *)(const void *)((const uint8_t *)p+o); }
static void half(void *p,uint32_t o,int32_t v) { *(uint16_t *)(void *)((uint8_t *)p+o)=(uint16_t)v; }
uint32_t audio_uart_font_glyph_cache_initialize(void *entry,void *font) {
    uint8_t *f=(uint8_t *)font;
    uint8_t *context=(uint8_t *)(uintptr_t)word(f,0x34u);
    (void)audio_uart_lv_lock_core(context+0x10u);
    uint8_t *face=(uint8_t *)(uintptr_t)word(context,0x0cu);
    uint32_t index=audio_uart_font_get_char_index(face,word(entry,0u));
    int32_t error=(face[8u]&1u)?audio_uart_font_face_load_scalable(face,0u,word(f,0x28u)):
                    audio_uart_font_face_select_size(face,0u);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0x96u,function,size_error,error);
        (void)audio_uart_lv_unlock_core(context+0x10u);
        return 0u;
    }
    if(f[0x2du]==1u) error=audio_uart_font_load_glyph(face,index,0x208008u);
    else if(f[0x2du]==0u) error=audio_uart_font_load_glyph(face,index,0x208000u);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0xa2u,function,load_error,error);
        (void)audio_uart_lv_unlock_core(context+0x10u);
        return 0u;
    }
    uint8_t *slot=(uint8_t *)(uintptr_t)word(face,0x54u);
    if(f[0x2du]==1u) {
        half(entry,0x0cu,signed_word(slot,0x28u)>>6);
        half(entry,0x10u,signed_word(slot,0x1cu)>>6);
        half(entry,0x0eu,signed_word(slot,0x18u)>>6);
        half(entry,0x12u,signed_word(slot,0x20u)>>6);
        half(entry,0x14u,(signed_word(slot,0x24u)-signed_word(slot,0x1cu))>>6);
        ((uint8_t *)entry)[0x16u]=0x1au;
        if((f[0x2cu]&1u)!=0u) {
            uint16_t bearing=*(uint16_t *)(void *)((uint8_t *)entry+0x0eu);
            uint16_t width=*(uint16_t *)(void *)((uint8_t *)entry+0x10u);
            half(entry,0x0eu,audio_uart_font_italic_shift(bearing,width));
        }
    } else if(f[0x2du]==0u) {
        half(entry,0x0cu,signed_word(slot,0x40u)>>6);
        half(entry,0x10u,signed_word(slot,0x4cu));
        half(entry,0x0eu,signed_word(slot,0x50u));
        half(entry,0x12u,signed_word(slot,0x64u));
        int16_t baseline=*(int16_t *)(void *)((uint8_t *)entry+0x10u);
        half(entry,0x14u,signed_word(slot,0x68u)-baseline);
        ((uint8_t *)entry)[0x16u]=word(slot,0x48u)==0x62697473u?0x19u:8u;
    }
    ((uint8_t *)entry)[0x17u]=(((uint8_t *)entry)[0x17u]&0xfeu)|(index==0u);
    *(uint32_t *)(void *)((uint8_t *)entry+0x20u)=index;
    (void)audio_uart_lv_unlock_core(context+0x10u);
    return 1u;
}
