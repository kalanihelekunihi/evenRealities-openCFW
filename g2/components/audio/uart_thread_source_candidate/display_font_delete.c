/* Native LVGL FreeType font delete 0x4b1ef6. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_font_cache_remove(void *,void *,uint32_t); /* 0x4d4e72 */
extern uint32_t audio_uart_font_cache_has_owner(void *); /* 0x4d5312 */
extern void audio_uart_font_cache_drop(void *,void *,uint32_t); /* 0x4d5094 */
extern void audio_uart_font_path_release(void *,uint32_t); /* 0x4b21a0 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* source equivalent of 0x4b1b8c */
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
static const char function[]="lv_freetype_font_delete";
static const char assert_two[]="Asserted at expression: %s (%s)";
static const char assert_invalid[]="Asserted at expression: %s Invalid font descriptor: 0x%x";
static const char font_nonnull[]="font != NULL";
static const char descriptor_nonnull[]="dsc != NULL";
static const char descriptor_magic[]="LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(dsc)";
static const char null_pointer[]="NULL pointer";
static void font_delete_assert(uint32_t line,const char *expression,const char *reason,
                               uint32_t value) {
    if(reason!=0)
        audio_uart_lvgl_log(3u,source,line,function,assert_two,expression,reason);
    else
        audio_uart_lvgl_log(3u,source,line,function,assert_invalid,expression,value);
    for(;;) { /* authenticated native assertion loop */ }
}
void audio_uart_font_delete(void *font) {
    if(font==0) font_delete_assert(0xc0u,font_nonnull,null_pointer,0u);
    uint8_t *descriptor=*(uint8_t **)(void *)((uint8_t *)font+0x18u);
    if(descriptor==0) font_delete_assert(0xc3u,descriptor_nonnull,null_pointer,0u);
    uint32_t magic=*(uint32_t *)(void *)descriptor;
    if(magic!=0x5f5f4654u)
        font_delete_assert(0xc3u,descriptor_magic,0,magic);
    uint8_t *context=*(uint8_t **)(void *)(audio_uart_display_lv_state+0x1c0u);
    void *cache=*(void **)(void *)(context+0x18u);
    void *node=*(void **)(void *)(descriptor+0x38u);
    audio_uart_font_cache_remove(cache,node,0u);
    if(audio_uart_font_cache_has_owner(node)==0u)
        audio_uart_font_cache_drop(cache,*(void **)(void *)(descriptor+0x34u),0u);
    audio_uart_font_path_release(context,*(uint32_t *)(void *)(descriptor+0x3cu));
    audio_uart_buffer_zero(descriptor,0x44u,0u);
    audio_uart_lv_heap_free(descriptor);
}
