/* Native LVGL cache acquire-or-create 0x4d4f90, add 0x4d51c0, evict 0x4d5172. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void audio_uart_font_cache_retain(void *);
extern void *audio_uart_font_cache_info(void *);
extern void audio_uart_font_cache_entry_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
typedef void *(*lookup_fn)(void *,const void *,uint32_t);
typedef void (*remove_fn)(void *,void *,uint32_t);
typedef void *(*create_fn)(void *,const void *,uint32_t);
typedef uint32_t (*space_fn)(void *,const void *,uint32_t,uint32_t);
typedef void *(*victim_fn)(void *,uint32_t);
typedef uint8_t (*initialize_fn)(void *,uint32_t);
typedef void (*destroy_fn)(void *,uint32_t);
static uint32_t *vt(void *cache) { return *(uint32_t **)(void *)cache; }
static void fail(uint32_t line,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,"lv_cache_acquire_or_create",
                        "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) { /* authenticated native assertion loop */ }
}
uint32_t audio_uart_lv_cache_evict_one_4d5172(void *cache,uint32_t context) {
    uint32_t *v=vt(cache);
    void *entry=((victim_fn)(uintptr_t)v[8])(cache,context);
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x14bu,"cache_evict_one_internal_no_lock",
                            "No victim found");
        return 0u;
    }
    ((remove_fn)(uintptr_t)vt(cache)[5])(cache,entry,context);
    void *data=audio_uart_font_cache_info(entry);
    ((destroy_fn)(uintptr_t)*(uint32_t *)(void *)((uint8_t *)cache+0x18u))(data,context);
    audio_uart_font_cache_entry_delete(entry);
    return 1u;
}
void *audio_uart_lv_cache_add_internal_4d51c0(void *cache,const void *key,uint32_t context) {
    uint32_t *v=vt(cache);
    uint8_t room=((space_fn)(uintptr_t)v[9])(cache,key,0u,context);
    if(room==1u) {
        audio_uart_lvgl_log(3u,source,0x159u,"cache_add_internal_no_lock",
                            "data %p is too large that exceeds max size (%u)",
                            key,*(uint32_t *)(void *)((uint8_t *)cache+8u));
        return 0;
    }
    while(room==2u) {
        if(audio_uart_lv_cache_evict_one_4d5172(cache,context)==0u) return 0;
        room=((space_fn)(uintptr_t)vt(cache)[9])(cache,key,0u,context);
    }
    return ((create_fn)(uintptr_t)vt(cache)[4])(cache,key,context);
}
void *audio_uart_font_cache_add(void *cache,const void *key,uint32_t context) {
    if(cache==0) fail(0x95u,"cache != NULL");
    if(key==0) fail(0x96u,"key != NULL");
    uint8_t *base=(uint8_t *)cache;
    (void)audio_uart_lv_lock_core(base+0x1cu);
    uint32_t *v=vt(cache);
    void *entry=0;
    if(*(uint32_t *)(void *)(base+0x0cu)!=0u)
        entry=((lookup_fn)(uintptr_t)v[3])(cache,key,context);
    if(entry==0 && *(uint32_t *)(void *)(base+8u)!=0u) {
        entry=audio_uart_lv_cache_add_internal_4d51c0(cache,key,context);
        if(entry!=0) {
            void *data=audio_uart_font_cache_info(entry);
            if(((initialize_fn)(uintptr_t)*(uint32_t *)(void *)(base+0x14u))(data,context)==0u) {
                ((remove_fn)(uintptr_t)v[5])(cache,entry,context);
                audio_uart_font_cache_entry_delete(entry);
                entry=0;
            }
        }
    }
    if(entry!=0) audio_uart_font_cache_retain(entry);
    (void)audio_uart_lv_unlock_core(base+0x1cu);
    return entry;
}
