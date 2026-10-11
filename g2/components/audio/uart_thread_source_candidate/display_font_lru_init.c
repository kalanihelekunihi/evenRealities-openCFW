/* Native count-based LRU init 0x5c2c54 and size callback 0x5c330c. */
#include <stdint.h>
extern uint32_t audio_uart_font_rb_initialize(void *,uint32_t,uint32_t); /* 0x5c3428 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
static const char function[]="init_cnt_cb";
static void assertion(uint32_t line,const char *expression,uint32_t detailed) {
    if(detailed!=0u)
        audio_uart_lvgl_log(3u,source,line,function,"Asserted at expression: %s",expression);
    else
        audio_uart_lvgl_log(3u,source,line,function,
                            "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) { /* authenticated native assertion loop */ }
}
static uint32_t count_size(const void *unused) { /* native 0x5c330c */
    (void)unused;
    return 1u;
}
uint32_t audio_uart_font_lru_initialize(void *cache) {
    uint8_t *base=(uint8_t *)cache;
    uint32_t compare=*(uint32_t *)(void *)(base+0x10u);
    uint32_t free_callback=*(uint32_t *)(void *)(base+0x18u);
    uint32_t node_size=*(uint32_t *)(void *)(base+4u);
    if(compare==0u) assertion(0xccu,"lru->cache.ops.compare_cb != NULL",0u);
    if(free_callback==0u) assertion(0xcdu,"lru->cache.ops.free_cb != NULL",0u);
    if(node_size==0u) assertion(0xceu,"lru->cache.node_size > 0",1u);
    if(audio_uart_font_rb_initialize(base+0x28u,compare,node_size+0x14u)==0u)
        return 0u;
    uint32_t *list=(uint32_t *)(void *)(base+0x34u);
    list[0]=4u;
    list[1]=0u;
    list[2]=0u;
    *(uint32_t *)(void *)(base+0x40u)=(uint32_t)(uintptr_t)&count_size;
    return 1u;
}
