/* Native LVGL cache release/drop 0x4d4e72, 0x4d5094, and drop core 0x4d511c. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern uint32_t audio_uart_font_cache_has_owner(void *);
extern uint32_t audio_uart_font_cache_is_invalid(void *);
extern void *audio_uart_font_cache_info(void *);
extern void audio_uart_font_cache_release_data(void *);
extern void audio_uart_font_cache_set_invalid(void *,uint8_t);
extern void audio_uart_font_cache_entry_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
static const char assertion[]="Asserted at expression: %s (%s)";
static const char reason[]="NULL pointer";
static void fail(uint32_t line,const char *function,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,function,assertion,expression,reason);
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
typedef void *(*lookup_fn)(void *,const void *,uint32_t);
typedef void (*remove_fn)(void *,void *,uint32_t);
typedef void (*data_fn)(void *,uint32_t);
static uint32_t *vtable(void *cache) { return *(uint32_t **)(void *)cache; }
void audio_uart_lv_cache_drop_internal_4d511c(void *cache,const void *key,uint32_t context) {
    uint32_t *vt=vtable(cache);
    void *entry=((lookup_fn)(uintptr_t)vt[3])(cache,key,context);
    if(entry==0) return;
    if(audio_uart_font_cache_has_owner(entry)==0u) {
        ((remove_fn)(uintptr_t)vtable(cache)[5])(cache,entry,context);
        void *data=audio_uart_font_cache_info(entry);
        ((data_fn)(uintptr_t)*(uint32_t *)(void *)((uint8_t *)cache+0x18u))(data,context);
        audio_uart_font_cache_entry_delete(entry);
    } else {
        audio_uart_font_cache_set_invalid(entry,1u);
        ((remove_fn)(uintptr_t)vtable(cache)[5])(cache,entry,context);
    }
}
void audio_uart_font_cache_remove(void *cache,void *entry,uint32_t context) {
    if(entry==0) fail(0x6cu,"lv_cache_release","entry != NULL");
    uint8_t *base=(uint8_t *)cache;
    (void)audio_uart_lv_lock_core(base+0x1cu);
    audio_uart_font_cache_release_data(entry);
    if(audio_uart_font_cache_has_owner(entry)==0u &&
       audio_uart_font_cache_is_invalid(entry)!=0u) {
        void *data=audio_uart_font_cache_info(entry);
        ((data_fn)(uintptr_t)*(uint32_t *)(void *)(base+0x18u))(data,context);
        audio_uart_font_cache_entry_delete(entry);
    }
    (void)audio_uart_lv_unlock_core(base+0x1cu);
}
void audio_uart_font_cache_drop(void *cache,void *key,uint32_t context) {
    if(cache==0) fail(0xd3u,"lv_cache_drop","cache != NULL");
    if(key==0) fail(0xd4u,"lv_cache_drop","key != NULL");
    uint8_t *base=(uint8_t *)cache;
    (void)audio_uart_lv_lock_core(base+0x1cu);
    audio_uart_lv_cache_drop_internal_4d511c(cache,key,context);
    (void)audio_uart_lv_unlock_core(base+0x1cu);
}
