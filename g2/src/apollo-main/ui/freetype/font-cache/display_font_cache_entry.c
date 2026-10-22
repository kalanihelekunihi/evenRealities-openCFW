/* Native LVGL cache-entry accessors 0x4d5312 and 0x4d5396. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_entry.c";
static const char assertion[]="Asserted at expression: %s (%s)";
static const char expression[]="entry != NULL";
static const char reason[]="NULL pointer";
static const char ref_function[]="lv_cache_entry_get_ref";
static const char data_function[]="lv_cache_entry_get_data";
static const char inc_function[]="lv_cache_entry_inc_ref";


void *audio_uart_font_cache_info(void *entry) {
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x67u,data_function,assertion,expression,reason);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t offset=*(uint32_t *)(void *)((uint8_t *)entry+8u);
    return (void *)((uintptr_t)entry-offset);
}







extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */


