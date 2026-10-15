/* Apollo LVGL cache entry data at 0x4d5396..0x4d53c5. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char cache_entry_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_entry.c";
static const char cache_entry_name[] = "lv_cache_entry_get_data";
static const char cache_entry_assert[] = "Asserted at expression: %s (%s)";
static const char cache_entry_expression[] = "entry != NULL";
static const char cache_entry_reason[] = "NULL pointer";

uint32_t audio_uart_lv_cache_entry_4d5396(uint32_t entry) {
    if (entry==0u) {
        audio_uart_lvgl_log(3u,cache_entry_path,103u,cache_entry_name,
                            cache_entry_assert,cache_entry_expression,
                            cache_entry_reason);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    return entry-*(const uint32_t *)(uintptr_t)(entry+8u);
}
