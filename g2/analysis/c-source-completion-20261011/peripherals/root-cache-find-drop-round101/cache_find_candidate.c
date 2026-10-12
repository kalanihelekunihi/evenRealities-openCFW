/* Native LVGL cache acquire 0x4d4dca. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *); /* native 0x4d4666 */
extern uint32_t audio_uart_lv_unlock_core(void *); /* native 0x4d4696 */
extern void *audio_uart_font_cache_acquire_data(void *); /* native 0x4d53c6 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
static const char function[]="lv_cache_acquire";
static const char assertion[]="Asserted at expression: %s (%s)";
static const char reason[]="NULL pointer";
static void fail(uint32_t line,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,function,assertion,expression,reason);
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
void *audio_uart_font_cache_find(void *cache,const void *key,uint32_t context) {
    if(cache==0) fail(0x53u,"cache != NULL");
    if(key==0) fail(0x54u,"key != NULL");
    uint8_t *base=(uint8_t *)cache;
    (void)audio_uart_lv_lock_core(base+0x1cu);
    void *entry=0;
    if(*(uint32_t *)(void *)(base+0x0cu)!=0u) {
        uint32_t *vtable=*(uint32_t **)(void *)base;
        void *(*lookup)(void *,const void *,uint32_t)=
            (void *(*)(void *,const void *,uint32_t))(uintptr_t)vtable[3];
        entry=lookup(cache,key,context);
        if(entry!=0) (void)audio_uart_font_cache_acquire_data(entry);
    }
    (void)audio_uart_lv_unlock_core(base+0x1cu);
    return entry;
}
