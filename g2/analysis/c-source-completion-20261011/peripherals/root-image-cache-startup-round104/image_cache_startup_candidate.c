#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern const uintptr_t audio_uart_font_cache_backend_vtable[10];
extern const uintptr_t audio_uart_lv_cache_size_backend_vtable[10];
extern void *audio_uart_lv_cache_create_4d4cd4(const uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_image_cache_compare_4d4b94(const void *,const void *);
extern int32_t audio_uart_lv_image_header_cache_compare_4d4c9c(const void *,const void *);
extern void audio_uart_lv_image_cache_free_4d4ba4(void *);
extern void audio_uart_lv_image_header_cache_free_4d4cac(void *);
/* Native4d5114..4d511c: null is deliberately a no-op. */
void audio_uart_lv_cache_set_name_4d5114(void *cache,const char *name)
{
    if(cache!=0) *(volatile uint32_t *)((uint8_t *)cache+36u)=(uint32_t)(uintptr_t)name;
}
/* Native4d4ad4..4d4b24: image-cache startup, not font init. */
uint32_t audio_uart_lv_image_cache_init_4d4ad4(uint32_t size)
{
    volatile uint32_t *slot=(void *)(audio_uart_display_lv_root+0x134u);
    if(*slot!=0u) return 1u;
    void *cache=audio_uart_lv_cache_create_4d4cd4(
        (const uint32_t *)audio_uart_lv_cache_size_backend_vtable,24u,size,
        (uint32_t)(uintptr_t)audio_uart_lv_image_cache_compare_4d4b94,0u,
        (uint32_t)(uintptr_t)audio_uart_lv_image_cache_free_4d4ba4);
    *slot=(uint32_t)(uintptr_t)cache;
    audio_uart_lv_cache_set_name_4d5114((void *)(uintptr_t)*slot,"IMAGE");
    return *slot!=0u ? 1u : 0u;
}
/* Native4d4bdc..4d4c2c: header-cache startup, not font deinit. */
uint32_t audio_uart_lv_image_header_cache_init_4d4bdc(uint32_t count)
{
    volatile uint32_t *slot=(void *)(audio_uart_display_lv_root+0x138u);
    if(*slot!=0u) return 1u;
    void *cache=audio_uart_lv_cache_create_4d4cd4(
        (const uint32_t *)audio_uart_font_cache_backend_vtable,24u,count,
        (uint32_t)(uintptr_t)audio_uart_lv_image_header_cache_compare_4d4c9c,0u,
        (uint32_t)(uintptr_t)audio_uart_lv_image_header_cache_free_4d4cac);
    *slot=(uint32_t)(uintptr_t)cache;
    audio_uart_lv_cache_set_name_4d5114((void *)(uintptr_t)*slot,"IMAGE_HEADER");
    return *slot!=0u ? 1u : 0u;
}
