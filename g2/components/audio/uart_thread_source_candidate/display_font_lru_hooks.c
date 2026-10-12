/* Native shared LRU backend destroy/add vtable entries 0x5c2e0c/0x5c2f32. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_font_lru_insert(void *,const void *); /* native 0x5c2b00 */
extern void *audio_uart_font_cache_entry_at(void *,uint32_t); /* native 0x4d5452 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
static void fail(uint32_t line,const char *function,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,function,
                        "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
void audio_uart_font_lru_destroy(void *cache,uint32_t context) {
    if(cache==0) fail(0xfcu,"destroy_cb","lru != NULL");
    volatile uint32_t *c=cache;
    const volatile uint32_t *vtable=(void *)(uintptr_t)c[0];
    void (*destroy_all)(void *,uint32_t)=(void (*)(void *,uint32_t))(uintptr_t)vtable[7];
    destroy_all(cache,context);
}
void *audio_uart_font_lru_add(void *cache,const void *key,uint32_t context) {
    (void)context; /* native R2 unused */
    if(cache==0) fail(0x130u,"add_cb","lru != NULL");
    if(key==0) fail(0x131u,"add_cb","key != NULL");
    uint8_t *base=(uint8_t *)cache;
    uint8_t *node=(uint8_t *)audio_uart_font_lru_insert(cache,key);
    if(node==0) return 0;
    void *data=(void *)(uintptr_t)*(volatile uint32_t *)(void *)(node+0x10u);
    void *entry=audio_uart_font_cache_entry_at(data,
                        *(volatile uint32_t *)(void *)(base+4u));
    uint32_t (*size)(const void *)=(uint32_t (*)(const void *))(uintptr_t)
                            *(volatile uint32_t *)(void *)(base+0x40u);
    uint32_t delta=size(key);
    volatile uint32_t *current=(void *)(base+0x0cu);
    *current=*current+delta;
    return entry;
}
