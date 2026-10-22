/* Native LVGL LRU/RB cache allocation 0x5c2bee. */
#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t); /* selected 0x44f718 */
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
/* Full native5c2af4..5c2b00 zeroing wrapper. */
void audio_uart_lv_cache_lru_memzero_5c2af4(void *p,uint32_t n)
{ audio_uart_lv_basic_box_clear_454746(p,0u,n); }
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Stock 0x5C2BEE (alloc_cb; upstream third-party/upstream/lvgl/src/misc/cache/lv_cache_lru_rb.c) */
void *audio_uart_font_lru_allocate(void) {
    void *result=audio_uart_lv_malloc(0x44u);
    if(result==0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c",
            0xbeu,"alloc_cb","Asserted at expression: %s (%s)",
            "res != NULL","Out of memory");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(result==0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c",
            192u,"alloc_cb","malloc failed");
        return 0;
    }
    audio_uart_lv_cache_lru_memzero_5c2af4(result,0x44u);
    return result;
}
