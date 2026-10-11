/* Native LVGL LRU/RB cache allocation 0x5c2bee. */
#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t); /* selected 0x44f718 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected memset lower */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
void *audio_uart_font_lru_allocate(void) {
    void *result=audio_uart_lv_malloc(0x44u);
    if(result==0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c",
            0xbeu,"alloc_cb","Asserted at expression: %s (%s)",
            "res != NULL","Out of memory");
        for(;;) { /* authenticated native assertion loop */ }
    }
    audio_uart_buffer_zero(result,0x44u,0u);
    return result;
}
