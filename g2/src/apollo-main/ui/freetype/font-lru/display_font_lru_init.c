/* Native count5c2c54..5c2d30, size5c2d30..5c2e0c and data-size leaves. */
#include <stdint.h>
extern uint32_t audio_uart_font_rb_initialize(void *,uint32_t,uint32_t);
extern void audio_uart_lv_array_init_482b00(uint8_t *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
static void assertion(uint32_t line,const char *function,const char *expression,uint32_t simple)
{
    if(simple!=0u) audio_uart_lvgl_log(3u,source,line,function,
        "Asserted at expression: %s",expression);
    else audio_uart_lvgl_log(3u,source,line,function,
        "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
uint32_t audio_uart_lv_cache_count_data_size_5c330c(const void *unused)
{ (void)unused; return 1u; }
uint32_t audio_uart_lv_cache_size_data_size_5c3310(const void *data)
{ return *(const volatile uint32_t *)data; }
static uint32_t initialize(void *cache,uint32_t size_class)
{
    volatile uint32_t *c=cache;
    const char *function=size_class!=0u ? "init_size_cb" : "init_cnt_cb";
    uint32_t line=size_class!=0u ? 227u : 204u;
    if(c[4]==0u) assertion(line,function,"lru->cache.ops.compare_cb != NULL",0u);
    if(c[6]==0u) assertion(line+1u,function,"lru->cache.ops.free_cb != NULL",0u);
    if(c[1]==0u) assertion(line+2u,function,"lru->cache.node_size > 0",1u);
    if(c[1]==0u || c[4]==0u || c[6]==0u) return 0u;
    if(audio_uart_font_rb_initialize((uint8_t *)cache+40u,c[4],c[1]+20u)==0u) return 0u;
    audio_uart_lv_array_init_482b00((uint8_t *)cache+52u,4u);
    c[16]=(uint32_t)(uintptr_t)(size_class!=0u ?
        audio_uart_lv_cache_size_data_size_5c3310 : audio_uart_lv_cache_count_data_size_5c330c);
    return 1u;
}
/* Stock 0x5C2C54 (init_cnt_cb; upstream third-party/upstream/lvgl/src/misc/cache/lv_cache_lru_rb.c) */
uint32_t audio_uart_font_lru_initialize(void *cache)
{ return initialize(cache,0u); }
uint32_t audio_uart_lv_cache_size_lru_init_5c2d30(void *cache)
{ return initialize(cache,1u); }
