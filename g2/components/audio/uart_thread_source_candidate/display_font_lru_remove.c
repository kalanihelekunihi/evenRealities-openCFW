/* Native LRU remove/evict backend slots 0x5c2fd4 and 0x5c3098. */
#include <stdint.h>
extern void *audio_uart_font_cache_info(void *);
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern void audio_uart_font_cache_entry_delete(void *);
extern void *audio_uart_font_rb_find(void *,const void *); /* 0x5c3594 */
extern void *audio_uart_font_rb_remove(void *,void *); /* 0x5c3600 */
extern void audio_uart_lv_list_remove(void *,void *); /* selected 0x482c0e */
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
static void fail(uint32_t line,const char *function,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,function,
                        "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) { /* authenticated native assertion loop */ }
}
static uint32_t size_of(uint8_t *cache,const void *data) {
    uint32_t cb=*(uint32_t *)(void *)(cache+0x40u);
    return ((uint32_t (*)(const void *))(uintptr_t)cb)(data);
}
static uint32_t list_link(uint8_t *cache,uint8_t *rb) {
    uint32_t data=*(uint32_t *)(void *)(rb+0x10u);
    uint32_t address=*(uint32_t *)(void *)(cache+0x30u)+data-4u;
    return *(uint32_t *)(void *)(uintptr_t)address;
}
void audio_uart_font_lru_remove(void *cache,void *entry,uint32_t context) {
    (void)context;
    if(cache==0) fail(0x149u,"remove_cb","lru != NULL");
    if(entry==0) fail(0x14au,"remove_cb","entry != NULL");
    uint8_t *base=(uint8_t *)cache;
    void *data=audio_uart_font_cache_info(entry);
    uint8_t *rb=(uint8_t *)audio_uart_font_rb_find(base+0x28u,data);
    if(rb==0) return;
    uint32_t node=list_link(base,rb);
    (void)audio_uart_font_rb_remove(base+0x28u,rb);
    audio_uart_lv_list_remove(base+0x34u,(void *)(uintptr_t)node);
    audio_uart_lv_heap_free((void *)(uintptr_t)node);
    *(uint32_t *)(void *)(base+0x0cu)-=size_of(base,data);
}
void audio_uart_font_lru_evict(void *cache,const void *key,uint32_t context) {
    if(cache==0) fail(0x162u,"drop_cb","lru != NULL");
    if(key==0) fail(0x163u,"drop_cb","key != NULL");
    uint8_t *base=(uint8_t *)cache;
    uint8_t *rb=(uint8_t *)audio_uart_font_rb_find(base+0x28u,key);
    if(rb==0) return;
    uint32_t data=*(uint32_t *)(void *)(rb+0x10u);
    uint32_t callback=*(uint32_t *)(void *)(base+0x18u);
    ((void (*)(void *,uint32_t))(uintptr_t)callback)((void *)(uintptr_t)data,context);
    *(uint32_t *)(void *)(base+0x0cu)-=size_of(base,(void *)(uintptr_t)data);
    void *entry=audio_uart_font_cache_entry_at((void *)(uintptr_t)data,
                    *(uint32_t *)(void *)(base+4u));
    uint32_t node=list_link(base,rb);
    (void)audio_uart_font_rb_remove(base+0x28u,rb);
    audio_uart_font_cache_entry_delete(entry);
    audio_uart_lv_list_remove(base+0x34u,(void *)(uintptr_t)node);
    audio_uart_lv_heap_free((void *)(uintptr_t)node);
}
