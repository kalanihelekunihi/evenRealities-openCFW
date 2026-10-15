/* Apollo LVGL cache release at 0x4d4e72..0x4d4ee9. */
#include <stdint.h>

extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void audio_uart_font_cache_release_data(void *);
extern uint32_t audio_uart_font_cache_has_owner(void *);
extern uint32_t audio_uart_font_cache_is_invalid(void *);
extern uint32_t audio_uart_lv_cache_entry_4d5396(uint32_t);
extern void audio_uart_font_cache_entry_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char cache_release_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
static const char cache_release_name[] = "lv_cache_release";
static const char cache_release_assert[] = "Asserted at expression: %s (%s)";
static const char cache_release_expression[] = "entry != NULL";
static const char cache_release_reason[] = "NULL pointer";

void audio_uart_lv_decoder_release_4d4e72(
        uint32_t cache,uint32_t entry,uint32_t user_data) {
    if (entry==0u) {
        audio_uart_lvgl_log(3u,cache_release_path,108u,cache_release_name,
                            cache_release_assert,cache_release_expression,
                            cache_release_reason);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    audio_uart_lv_lock_core((void *)(uintptr_t)(cache+28u));
    audio_uart_font_cache_release_data((void *)(uintptr_t)entry);
    if (audio_uart_font_cache_has_owner((void *)(uintptr_t)entry)==0u &&
        audio_uart_font_cache_is_invalid((void *)(uintptr_t)entry)!=0u) {
        const uint32_t data=audio_uart_lv_cache_entry_4d5396(entry);
        const uint32_t callback=*(const uint32_t *)(uintptr_t)(cache+24u);
        ((void (*)(uint32_t,uint32_t))(uintptr_t)callback)(data,user_data);
        audio_uart_font_cache_entry_delete((void *)(uintptr_t)entry);
    }
    audio_uart_lv_unlock_core((void *)(uintptr_t)(cache+28u));
}
