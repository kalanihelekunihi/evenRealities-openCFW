#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void *audio_uart_lv_cache_add_internal_4d51c0(void *,const void *,uint32_t);
extern void *audio_uart_font_cache_acquire_data(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native4d4eea..4d4f90; no initializer callback in this cache-add API. */
void *audio_uart_lv_cache_add_4d4eea(void *cache,const void *key,void *user_data)
{
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
    if(cache==0) {
        audio_uart_lvgl_log(3u,source,125u,"lv_cache_add","Asserted at expression: %s (%s)","cache != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(key==0) {
        audio_uart_lvgl_log(3u,source,126u,"lv_cache_add","Asserted at expression: %s (%s)","key != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    void *lock=(void *)((uintptr_t)cache+28u);
    (void)audio_uart_lv_lock_core(lock);
    if(((volatile uint32_t *)cache)[2]==0u) {(void)audio_uart_lv_unlock_core(lock);return 0;}
    void *entry=audio_uart_lv_cache_add_internal_4d51c0(cache,key,(uint32_t)(uintptr_t)user_data);
    if(entry!=0) (void)audio_uart_font_cache_acquire_data(entry);
    (void)audio_uart_lv_unlock_core(lock);
    return entry;
}
