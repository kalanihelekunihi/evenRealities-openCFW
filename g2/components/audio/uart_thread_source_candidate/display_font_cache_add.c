/* Native LVGL cache acquire-or-create 0x4d4f90, add 0x4d51c0, evict 0x4d5172. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void audio_uart_font_cache_retain(void *);
extern void *audio_uart_font_cache_acquire_data(void *);
extern void *audio_uart_font_cache_info(void *);
extern void audio_uart_font_cache_entry_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
typedef void *(*lookup_fn)(void *,const void *,uint32_t);
typedef void (*remove_fn)(void *,void *,uint32_t);
typedef void *(*create_fn)(void *,const void *,uint32_t);
typedef uint32_t (*space_fn)(void *,const void *,uint32_t,uint32_t);
typedef void *(*victim_fn)(void *,uint32_t);
typedef uint32_t (*initialize_fn)(void *,uint32_t);
typedef void (*destroy_fn)(void *,uint32_t);
static uint32_t *vt(void *cache) { return *(uint32_t **)(void *)cache; }
static void fail(uint32_t line,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,"lv_cache_acquire_or_create",
                        "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
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
/* Full native4d4f90..4d5094; preserve fast existing-entry acquire and fresh class/ops loads. */
void *audio_uart_font_cache_add(void *cache,const void *key,uint32_t context)
{
    if(cache==0) fail(149u,"cache != NULL");
    if(key==0) fail(150u,"key != NULL");
    volatile uint32_t *c=cache;
    void *lock=(void *)((uintptr_t)cache+28u);
    (void)audio_uart_lv_lock_core(lock);
    void *entry;
    if(c[3]!=0u) {
        entry=((lookup_fn)(uintptr_t)vt(cache)[3])(cache,key,context);
        if(entry!=0) {
            (void)audio_uart_font_cache_acquire_data(entry);
            (void)audio_uart_lv_unlock_core(lock);return entry;
        }
    }
    if(c[2]==0u) {(void)audio_uart_lv_unlock_core(lock);return 0;}
    entry=audio_uart_lv_cache_add_internal_4d51c0(cache,key,context);
    if(entry==0) {(void)audio_uart_lv_unlock_core(lock);return 0;}
    void *data=audio_uart_font_cache_info(entry);
    uint32_t initialized=((initialize_fn)(uintptr_t)c[5])(data,context);
    if((uint8_t)initialized==0u) {
        ((remove_fn)(uintptr_t)vt(cache)[5])(cache,entry,context);
        audio_uart_font_cache_entry_delete(entry);entry=0;
    } else (void)audio_uart_font_cache_acquire_data(entry);
    (void)audio_uart_lv_unlock_core(lock);
    return entry;
}
