/* Apollo LVGL cache acquire at 0x4d4dca..0x4d4e71. */
#include <stdint.h>

extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void *audio_uart_font_cache_acquire_data(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char cache_lookup_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
static const char cache_lookup_name[] = "lv_cache_acquire";
static const char cache_lookup_assert[] = "Asserted at expression: %s (%s)";
static const char cache_lookup_null[] = "NULL pointer";
static const char cache_lookup_cache_expression[] = "cache != NULL";
static const char cache_lookup_key_expression[] = "key != NULL";

uint32_t audio_uart_lv_cache_lookup_4d4dca(
        uint32_t cache,const void *key,uint32_t user_data) {
    if (cache==0u || key==0) {
        audio_uart_lvgl_log(3u,cache_lookup_path,cache==0u?83u:84u,
                            cache_lookup_name,cache_lookup_assert,
                            cache==0u?cache_lookup_cache_expression:
                                      cache_lookup_key_expression,
                            cache_lookup_null);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    audio_uart_lv_lock_core((void *)(uintptr_t)(cache+28u));
    if (*(uint32_t *)(uintptr_t)(cache+12u)==0u) {
        audio_uart_lv_unlock_core((void *)(uintptr_t)(cache+28u));
        return 0u;
    }
    const uint32_t manager=*(uint32_t *)(uintptr_t)cache;
    const uint32_t callback=*(uint32_t *)(uintptr_t)(manager+12u);
    const uint32_t entry=((uint32_t (*)(uint32_t,const void *,uint32_t))
        (uintptr_t)callback)(cache,key,user_data);
    if (entry!=0u) (void)audio_uart_font_cache_acquire_data(
        (void *)(uintptr_t)entry);
    audio_uart_lv_unlock_core((void *)(uintptr_t)(cache+28u));
    return entry;
}
