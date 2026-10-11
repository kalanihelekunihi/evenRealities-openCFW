/* Native LRU get-victim/reserve-condition 0x5c3222/0x5c328a. */
#include <stdint.h>
extern uint32_t audio_uart_font_cache_has_owner(void *);
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
static void fail(uint32_t line,const char *function) {
    audio_uart_lvgl_log(3u,source,line,function,
                        "Asserted at expression: %s (%s)","lru != NULL","NULL pointer");
    for(;;) { /* authenticated native assertion loop */ }
}
void *audio_uart_font_lru_get_victim(void *cache,uint32_t context) {
    (void)context;
    if(cache==0) fail(0x1a5u,"get_victim_cb");
    uint8_t *base=(uint8_t *)cache;
    uint32_t *list=(uint32_t *)(void *)(base+0x34u);
    uint32_t node=list[2];
    while(node!=0u) {
        uint32_t rb=*(uint32_t *)(void *)(uintptr_t)node;
        uint32_t data=*(uint32_t *)(void *)(uintptr_t)(rb+0x10u);
        void *entry=audio_uart_font_cache_entry_at((void *)(uintptr_t)data,
                               *(uint32_t *)(void *)(base+4u));
        if(audio_uart_font_cache_has_owner(entry)==0u) return entry;
        node=*(uint32_t *)(void *)(uintptr_t)(node+list[0]);
    }
    return 0;
}
uint8_t audio_uart_font_lru_reserve(void *cache,const void *data,uint32_t extra) {
    if(cache==0) fail(0x1bau,"reserve_cond_cb");
    uint8_t *base=(uint8_t *)cache;
    uint32_t size=0u;
    if(data!=0) {
        uint32_t callback=*(uint32_t *)(void *)(base+0x40u);
        size=((uint32_t (*)(const void *))(uintptr_t)callback)(data);
    }
    uint32_t maximum=*(uint32_t *)(void *)(base+8u);
    if(maximum<size) {
        audio_uart_lvgl_log(3u,source,0x1c2u,"reserve_cond_cb",
                            "data size (%u) is larger than max size (%u)",size,maximum);
        return 1u;
    }
    if(maximum<size+extra+*(uint32_t *)(void *)(base+0x0cu)) return 2u;
    return 0u;
}
