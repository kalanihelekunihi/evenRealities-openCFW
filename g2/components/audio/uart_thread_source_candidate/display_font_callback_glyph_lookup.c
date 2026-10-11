/* Native FreeType common glyph-descriptor callback 0x529460. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x48949c */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 */
extern void *audio_uart_font_cache_add(void *,const void *,uint32_t); /* 0x4d4f90 */
extern void *audio_uart_font_cache_info(void *); /* 0x4d5396 */
extern void audio_uart_font_cache_remove(void *,void *,uint32_t); /* 0x4d4e72 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_glyph.c";
static const char function[]="freetype_get_glyph_dsc_cb";
static const char assertion[]="Asserted at expression: %s (%s)";
static const char invalid_assertion[]="Asserted at expression: %s Invalid font descriptor: 0x%x";
static const char null_pointer[]="NULL pointer";
static const char font_nonnull[]="font != NULL";
static const char gdesc_nonnull[]="g_dsc != NULL";
static const char dsc_nonnull[]="dsc != NULL";
static const char valid_magic[]="LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(dsc)";
static const char lookup_error[]="glyph lookup failed for unicode = 0x%x";
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void fatal(void) {for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;}
uint32_t audio_uart_font_cb_glyph(void *font,void *glyph_descriptor,
                                  uint32_t unicode,uint32_t is_next) {
    if(font==0) {audio_uart_lvgl_log(3u,source,0x52u,function,assertion,font_nonnull,null_pointer);fatal();}
    if(glyph_descriptor==0) {
        audio_uart_lvgl_log(3u,source,0x53u,function,assertion,gdesc_nonnull,null_pointer);fatal();
    }
    uint8_t *glyph=(uint8_t *)glyph_descriptor;
    if(unicode<0x20u) {
        *(uint16_t *)(void *)(glyph+4u)=0u;
        *(uint16_t *)(void *)(glyph+8u)=0u;
        *(uint16_t *)(void *)(glyph+6u)=0u;
        *(uint16_t *)(void *)(glyph+10u)=0u;
        *(uint16_t *)(void *)(glyph+12u)=0u;
        glyph[14u]=0u;
        return 1u;
    }
    uint8_t *dsc=(uint8_t *)(uintptr_t)w(font,0x18u);
    if(dsc==0) {audio_uart_lvgl_log(3u,source,0x62u,function,assertion,dsc_nonnull,null_pointer);fatal();}
    if(w(dsc,0u)!=0x5f5f4654u) {
        audio_uart_lvgl_log(3u,source,0x62u,function,invalid_assertion,valid_magic,w(dsc,0u));
        fatal();
    }
    uint32_t key[10];
    audio_uart_buffer_zero(key,40u,0u);
    key[0]=unicode;key[1]=w(dsc,0x28u);
    uint8_t *context=(uint8_t *)(uintptr_t)w(dsc,0x34u);
    void *cache=(void *)(uintptr_t)w(context,0x18u);
    void *entry=audio_uart_font_cache_add(cache,key,(uint32_t)(uintptr_t)dsc);
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x6du,function,lookup_error,unicode);
        return 0u;
    }
    audio_uart_checksum_copy(glyph,(uint8_t *)audio_uart_font_cache_info(entry)+8u,32u);
    if((dsc[0x2cu]&1u)!=0u && is_next==0u) {
        *(uint16_t *)(void *)(glyph+4u)=(uint16_t)((uint16_t)*(uint16_t *)(void *)(glyph+6u)+
                                                 (int16_t)*(uint16_t *)(void *)(glyph+10u));
    }
    *(uint32_t *)(void *)(glyph+0x1cu)=0u;
    audio_uart_font_cache_remove(cache,entry,0u);
    return 1u;
}
