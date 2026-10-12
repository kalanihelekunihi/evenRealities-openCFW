#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
/* Full native4d5104..4d5114; native unconditionally dereferences cache. */
uint32_t audio_uart_lv_cache_enabled_4d5104(void *cache)
{
    return ((volatile uint32_t *)cache)[2]!=0u;
}
/* Full native4d4b24..4d4b32; image-cache owner at root+0x134. */
uint32_t audio_uart_lv_image_cache_enabled_4d4b24(void)
{
    uint32_t cache=*(volatile uint32_t *)(void *)(audio_uart_display_lv_root+0x134u);
    return audio_uart_lv_cache_enabled_4d5104((void *)(uintptr_t)cache);
}
