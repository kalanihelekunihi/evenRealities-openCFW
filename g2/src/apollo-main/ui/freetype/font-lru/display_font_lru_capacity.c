/* Full native victim5c3222..5c328a and reserve5c328a..5c330c. */
#include <stdint.h>
extern uint32_t audio_uart_font_cache_has_owner(void *);
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern void *audio_uart_lv_list_first_482ce4(void *);
extern void *audio_uart_lv_list_next_482cfa(void *,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
static void fail(uint32_t line,const char *function)
{
    audio_uart_lvgl_log(3u,source,line,function,
        "Asserted at expression: %s (%s)","lru != NULL","NULL pointer");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Stock 0x5C3222 (get_victim_cb; upstream third-party/upstream/lvgl/src/misc/cache/lv_cache_lru_rb.c) */
void *audio_uart_font_lru_get_victim(void *cache,uint32_t context)
{
    (void)context;
    if(cache==0) fail(421u,"get_victim_cb");
    const volatile uint32_t *c=cache;
    void *list=(uint8_t *)cache+52u;
    void *node=audio_uart_lv_list_first_482ce4(list);
    while(node!=0) {
        const volatile uint32_t *rb=(void *)(uintptr_t)*(volatile uint32_t *)node;
        void *entry=audio_uart_font_cache_entry_at((void *)(uintptr_t)rb[4],c[1]);
        if(audio_uart_font_cache_has_owner(entry)==0u) return entry;
        node=audio_uart_lv_list_next_482cfa(list,node);
    }
    return 0;
}
/* Stock 0x5C328A (reserve_cond_cb; upstream third-party/upstream/lvgl/src/misc/cache/lv_cache_lru_rb.c) */
uint32_t audio_uart_font_lru_reserve(void *cache,const void *data,uint32_t extra,uint32_t context)
{
    (void)context; /* native R3 unused */
    if(cache==0) fail(442u,"reserve_cond_cb");
    const volatile uint32_t *c=cache;
    uint32_t size=0u;
    if(data!=0) {
        uint32_t (*size_callback)(const void *)=(uint32_t (*)(const void *))(uintptr_t)c[16];
        size=size_callback(data);
    }
    if(c[2]<size) {
        audio_uart_lvgl_log(3u,source,450u,"reserve_cond_cb",
            "data size (%u) is larger than max size (%u)",size,c[2]);
        return 1u;
    }
    if(c[2]<size+extra+c[3]) return 2u;
    return 0u;
}
