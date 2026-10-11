/* Native LVGL cache creation 0x4d4cd4 and FreeType wrappers 0x5293c0,
 * 0x5297b8, 0x529b38. Backend vtable/callback tables remain typed source-data
 * contracts until each table and every native backend function is recovered. */
#include <stdint.h>
extern void audio_uart_lv_mutex_ensure(uint32_t *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern const uintptr_t audio_uart_font_cache_backend_vtable[]; /* ROM0x73f478 */
extern const uintptr_t audio_uart_font_glyph_cache_hooks[3]; /* ROM0x78ae74 */
extern const uintptr_t audio_uart_font_bitmap_cache_hooks[3]; /* ROM0x78ae8c */
extern const uintptr_t audio_uart_font_outline_cache_hooks[3]; /* ROM0x78aeb0 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
static const char function[]="lv_cache_create";
static void *cache_create(const uint32_t *vtable,uint32_t block_size,uint32_t capacity,
                          uint32_t initialize,uint32_t destroy,uint32_t compare) {
    void *(*allocate)(void)=(void *(*)(void))(uintptr_t)vtable[0];
    uint32_t *cache=(uint32_t *)allocate();
    if(cache==0) {
        audio_uart_lvgl_log(3u,source,0x33u,function,
                            "Asserted at expression: %s (%s)","cache != NULL","Out of memory");
        for(;;) { /* authenticated native assertion loop */ }
    }
    cache[0]=(uint32_t)(uintptr_t)vtable;
    cache[1]=block_size;
    cache[2]=capacity;
    cache[3]=0u;
    cache[4]=initialize;
    cache[5]=destroy;
    cache[6]=compare;
    uint32_t (*init)(void *)=(uint32_t (*)(void *))(uintptr_t)vtable[1];
    if(init(cache)==0u) {
        audio_uart_lvgl_log(3u,source,0x3cu,function,"Cache init failed");
        audio_uart_lv_heap_free(cache);
        return 0;
    }
    audio_uart_lv_mutex_ensure(cache+7);
    return cache;
}
static void *create_font_cache(uint32_t capacity,uint32_t block_size,
                               const uintptr_t hooks[3],const char *name) {
    uint32_t *cache=(uint32_t *)cache_create((const uint32_t *)(const void *)audio_uart_font_cache_backend_vtable,
                          block_size,capacity,hooks[0],hooks[1],hooks[2]);
    if(cache!=0) cache[9]=(uint32_t)(uintptr_t)name; /* native 0x4d5114 */
    return cache;
}
void *audio_uart_font_glyph_cache_create(uint32_t capacity) {
    return create_font_cache(capacity,0x28u,audio_uart_font_glyph_cache_hooks,"FREETYPE_GLYPH");
}
void *audio_uart_font_bitmap_cache_create(uint32_t capacity) {
    return create_font_cache(capacity,0x0cu,audio_uart_font_bitmap_cache_hooks,"FREETYPE_IMAGE");
}
void *audio_uart_font_outline_cache_create(uint32_t capacity) {
    return create_font_cache(capacity,8u,audio_uart_font_outline_cache_hooks,"FREETYPE_OUTLINE");
}
